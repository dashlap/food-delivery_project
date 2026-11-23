from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CheckoutForm, OrderStatusForm, RegistrationForm
from .models import Category, Order, OrderItem, Product


def home(request):
    products = Product.objects.filter(is_available=True, is_popular=True)[:3]
    return render(request, "menu/home.html", {"products": products})


def catalog(request):
    products = Product.objects.filter(is_available=True).select_related("category")
    categories = Category.objects.all()
    category_slug = request.GET.get("category")
    if category_slug:
        products = products.filter(category__slug=category_slug)
    return render(
        request,
        "menu/catalog.html",
        {"products": products, "categories": categories, "active_category": category_slug},
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category"), slug=slug, is_available=True
    )
    return render(request, "menu/product_detail.html", {"product": product})


def register(request):
    if request.user.is_authenticated:
        return redirect("profile")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Аккаунт создан. Добро пожаловать!")
        return redirect("profile")
    return render(request, "menu/register.html", {"form": form})


@login_required
def profile(request):
    orders = request.user.orders.prefetch_related("items__product")
    return render(request, "menu/profile.html", {"orders": orders})


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_available=True)
    cart_items = request.session.get("cart", {})
    key = str(product.pk)
    cart_items[key] = min(cart_items.get(key, 0) + 1, 99)
    request.session["cart"] = cart_items
    messages.success(request, f"«{product.name}» добавлено в корзину.")
    next_url = request.POST.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(next_url)
    return redirect("catalog")


@require_POST
def remove_from_cart(request, product_id):
    cart_items = request.session.get("cart", {})
    cart_items.pop(str(product_id), None)
    request.session["cart"] = cart_items
    return redirect("checkout")


@login_required
def checkout(request):
    cart_items = request.session.get("cart", {})
    products = Product.objects.filter(
        pk__in=[int(key) for key in cart_items if key.isdigit()], is_available=True
    )
    lines = [
        {"product": product, "quantity": cart_items.get(str(product.pk), 0)}
        for product in products
    ]
    total = sum(line["product"].price * line["quantity"] for line in lines)
    if not lines:
        messages.info(request, "Корзина пока пуста.")
        return redirect("catalog")
    form = CheckoutForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                address=form.cleaned_data["address"],
                phone=form.cleaned_data["phone"],
                comment=form.cleaned_data["comment"],
                total=total,
            )
            OrderItem.objects.bulk_create(
                [
                    OrderItem(
                        order=order,
                        product=line["product"],
                        quantity=line["quantity"],
                        price=line["product"].price,
                    )
                    for line in lines
                ]
            )
        request.session["cart"] = {}
        messages.success(request, f"Заказ №{order.pk} оформлен. Скоро позвоним!")
        return redirect("profile")
    return render(
        request, "menu/checkout.html", {"form": form, "lines": lines, "total": total}
    )


def staff_required(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(staff_required, login_url="login")
def dashboard(request):
    orders = Order.objects.select_related("user").prefetch_related("items__product")
    return render(
        request,
        "menu/dashboard.html",
        {"orders": orders, "status_form": OrderStatusForm()},
    )


@require_POST
@user_passes_test(staff_required, login_url="login")
def update_order_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    form = OrderStatusForm(request.POST)
    if form.is_valid():
        order.status = form.cleaned_data["status"]
        order.save(update_fields=["status"])
        messages.success(request, f"Статус заказа №{order.pk} обновлён.")
    else:
        messages.error(request, "Не удалось изменить статус заказа.")
    return redirect("dashboard")
