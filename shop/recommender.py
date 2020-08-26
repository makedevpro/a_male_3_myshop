import redis

from django.conf import settings

from .models import Product

# connect to redis
r = redis.StrictRedis(host=settings.REDIS_HOST,
                      port=settings.REDIS_PORT,
                      db=settings.REDIS_DB)


class Recommender(object):
    """
    Реализует сохранение информации о купленных вместе товарах
    и подбор рекомендаций
    """

    # Формируем ключ хранилица
    def get_product_key(self, id):
        return 'product:{}:purchased_with'.format(id)

    # Получаем список объектов, которые были куплены вместе.
    def products_bought(self, products):
        # для каждого товара из списка получаем ID, формируя список
        product_ids = [p.id for p in products]
        # проходим по каждому идентификатору из списка и получаем товары, ко-
        # торые были куплены вместе с текущим
        for product_id in product_ids:
            for with_id in product_ids:
                # Получаем товары, купленные вместе с текущим.
                if product_id != with_id:
                    # для этого формируем ключ Redis,
                    # вызывая метод get_product_id()
                    # увеличиваем рейтинг каждого товара из списка, сохраняя
                    # информацию о том, что эти товары часто покупают вместе.
                    r.zincrby(self.get_product_key(product_id),
                              with_id, amount=1)

    # Получить рекомендуемые объекты
    def suggest_products_for(self, products, max_results=6):
        # Получаем идентификаторы переданных объектов
        product_ids = [p.id for p in products]
        if len(products) == 1:
            # Передан только один товар
            # Получаем список товаров, купленных с ним,
            # при этом учитывая их рейтинг
            suggestions = r.zrange(self.get_product_key(product_ids[0]),
                                   0, -1, desc=True)[:max_results]
        else:
            # Формируем временный ключ хранилица Redis.
            flat_ids = ''.join([str(id) for id in product_ids])
            tmp_key = 'tmp_{}'.format(flat_ids)
            # Передано несколько товаров, суммируем рейтинги их рекомендаций.

            # суммируем рейтинги для каждого товара, который был куплен вместе
            # с каким-либо из переданных в аргументе

            # Сохраняем суммы по временном ключе.
            keys = [self.get_product_key(id) for id in product_ids]
            # выполняем объединение множеств по указанным ключам и сохраняем
            # в Redis агрегированное значение по новому ключу
            # Сохраняем результат суммирования во
            # временном ключе, который генерировали на предыдущем шаге
            r.zunionstore(tmp_key, keys)
            # Удаляем ID товаров, котоыре были переданы в списке.
            # Чтобы они не попали в список рекомендаций
            r.zrem(tmp_key, *product_ids)
            # Получаем товары, отсортированные по рейтингу.
            # получаем идентификаторы всех товаров по временному ключу
            suggestions = r.zrange(tmp_key, 0, -1, desc=True)[:max_results]
            # Удаляем временный ключ.
            r.delete(tmp_key)
        suggest_products_ids = [int(id) for id in suggestions]

        # Получаем рекомендуемые товары и сортируем их.
        suggested_products = list(Product.objects
                                  .filter(id__in=suggest_products_ids))
        suggested_products.sort(key=lambda x: suggest_products_ids.index(x.id))
        return suggested_products

    # Очистка рекомендаций
    def clear_purchases(self):
        for id in Product.objects.values_list('id', flat=True):
            r.delete(self.get_product_key(id))

