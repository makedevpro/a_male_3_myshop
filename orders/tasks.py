from celery import task

from django.core.mail import send_mail

from .models import Order


@task
def order_created(order_id):
    # Рекомендуем передавать в качестве аргументов функции только идентификаторы
    # и получать сами объекты из базы данных лишь во время вы- полнения задачи
    """ Задача отправки email-уведомления при успешном оформлении заказа. """
    order = Order.objects.get(id=order_id)
    subject = f'Order nr.{order.id}'
    message = f'Dear {order.first_name}, \n\nYou have successfully placed an ' \
              f'order. Your order id is {order.id}.'
    mail_sent = send_mail(subject,
                          message,
                          'admin@localhost',
                          [order.email])
    return mail_sent
