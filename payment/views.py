import braintree
import weasyprint
from io import BytesIO

from django.conf import settings
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string

from orders.models import Order


def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        # Получение токена для создания транзакции
        nonce = request.POST.get('payment_method_nonce', None)

        # Создание и сохранение транзакции
        # формируем идентификатор платежной транзакции, обращаясь к методу
        # braintree.Transaction.sale(). В качестве аргументов этот метод
        # принимает:
        #  - amount (общую сумму заказа);
        #  - payment_method_nonce (токен, сгенерированный Braintree для
        #  платежной транзакции. Он формируется на странице силами
        #  JavaScript SDK);
        # - options (дополнительные параметры. Мы передали значение submit_
        # for_settlement, равное True, благодаря чему транзакция будет обраба-
        # тываться автоматически);
        result = braintree.Transaction.sale({
            'amount': '{:.2f}'.format(order.get_total_price()),
            'payment_method_nonce': nonce,
            'options': {
                'submit_for_settlement': True
            }
        })
        if result.is_success:
            # Отметка заказа как оплаченного
            order.paid = True
            # Сохранение ID транзакции в заказе
            order.braintree_id = result.transaction.id
            order.save()

            # Создание электронного сообщения.
            subject = 'My Shop - Invoice no. {}'.format(order.id)
            message = 'Please, find attached the invoice for your ' \
                      'recent purchase.'
            email = EmailMessage(subject,
                                 message,
                                 'admin@localhost',
                                 [order.email])
            # Формирование PDF.
            html = render_to_string('orders/order/pdf.html', {'order': order})
            out = BytesIO()
            stylesheets = [weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
            weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)
            # Прикрепляем PDF к электронному сообщению.
            email.attach('order_{}.pdf'.format(order.id),
                         out.getvalue(),
                         'application/pdf')
            # Отправка сообщения
            email.send()

            return redirect('payment:done')
        else:
            return redirect('payment:canceled')
    else:
        # Формирование одноразового токена для JavaScript SDK
        client_token = braintree.ClientToken.generate()
        return render(request,
                      'payment/process.html',
                      {'order': order,
                       'client_token': client_token})


def payment_done(request):
    return render(request, 'payment/done.html')


def payment_canceled(request):
    return render(request, 'payment/canceled.html')
