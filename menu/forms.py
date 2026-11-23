from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Электронная почта")
    first_name = forms.CharField(label="Имя", max_length=150)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "username", "email")
        labels = {"username": "Логин"}


class CheckoutForm(forms.Form):
    address = forms.CharField(label="Адрес доставки", max_length=240)
    phone = forms.CharField(label="Телефон", max_length=30)
    comment = forms.CharField(
        label="Комментарий к заказу",
        max_length=300,
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )


class OrderStatusForm(forms.Form):
    status = forms.ChoiceField(label="Новый статус", choices=())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Order

        self.fields["status"].choices = Order.Status.choices
