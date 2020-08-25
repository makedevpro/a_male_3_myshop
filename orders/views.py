import weasyprint

from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.template.loader import render_to_string

from .models import Order, OrderItem
from .forms import OrderCreateForm
from .tasks import order_created
from cart.cart import Cart


def order_create(request):
    cart = Cart(request)
    form = OrderCreateForm()
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            # Очищаем корзину
            cart.clear()
            # Запуск асинхронной задачи
            order_created.delay(order.id)
            # Сохранение заказа в сессии
            request.session['order_id'] = order.id
            # Перенаправление на страницу оплаты
            return redirect(reverse('payment:process'))

        else:
            form = OrderCreateForm()
    return render(request,
                  'orders/order/create.html',
                  {'cart': cart, 'form': form})


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request,
                  'admin/orders/order/detail.html',
                  {'order': order})


@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('orders/order/pdf.html',
                            {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="order_{}.pdf'.format(order.id)
    weasyprint.HTML(string=html)\
        .write_pdf(response,
                   stylesheets=[weasyprint.CSS(
                       settings.STATIC_ROOT + 'css/pdf.css'
                   )])
    return response
