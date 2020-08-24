from decimal import Decimal
from typing import Union

from django.db import models

from shop.models import  Product


class Order(models.Model):
    """ Модель заказа """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created',)

    def __str__(self) -> str:
        return f'Order {self.id}'

    def get_total_price(self) -> Union[Decimal, int]:
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    """ Модель информации о товаре и связаной с ним корзиной """
    order = models.ForeignKey(Order,
                              related_name='items',
                              on_delete=models.CASCADE)
    product = models.ForeignKey(Product,
                                related_name='order_items',
                                on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        return f'{self.id}'

    def get_cost(self) -> Union[Decimal, int]:
        return self.price * self.quantity
