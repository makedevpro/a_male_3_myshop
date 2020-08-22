from django import forms


PRODUCT_QUANTITY_CHOICE = [(i, str(i)) for i in range(1, 21)]


class CartAddProductForm(forms.Form):
    """ Форма добавления товара в корзину """
    # coerce=int, чтобы авто- матически преобразовывать
    # выбранное значение в целое число
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICE,
                                      coerce=int)
    # обновить (значение True) или заменить (значение False)
    # количество единиц для товара.
    update = forms.BooleanField(required=False,
                                initial=False,
                                widget=forms.HiddenInput)
