from localflavor.us.forms import USZipCodeField

from django import forms

from .models import Order


class OrderCreateForm(forms.ModelForm):
    """
    Форма для созданиея нового объекта Order при формировании заказа из корзины
    """
    postal_code = USZipCodeField()

    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address',
                  'postal_code', 'city']
