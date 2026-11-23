from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Order, OrderItem, Product


class OrderingFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="guest", password="safe-test-password", first_name="Аня"
        )
        self.category = Category.objects.create(name="Тестовая паста", slug="test-pasta")
        self.product = Product.objects.create(
            category=self.category,
            name="Паста с томатами",
            slug="test-pasta-tomato",
            description="Свежая паста",
            price=690,
            weight="320 г",
            is_available=True,
        )

    def test_catalog_filters_by_category_and_hides_unavailable_products(self):
        hidden = Product.objects.create(
            category=self.category,
            name="Скрытое блюдо",
            slug="hidden-dish",
            description="Временно недоступно",
            price=100,
            weight="100 г",
            is_available=False,
        )

        response = self.client.get(reverse("catalog"), {"category": self.category.slug})

        self.assertContains(response, self.product.name)
        self.assertNotContains(response, hidden.name)

    def test_checkout_creates_order_items_and_clears_session_cart(self):
        self.client.force_login(self.user)
        self.client.post(reverse("add_to_cart", args=[self.product.pk]))

        response = self.client.post(
            reverse("checkout"),
            {"address": "ул. Лесная, 5", "phone": "+7 900 000-00-00", "comment": ""},
        )

        self.assertRedirects(response, reverse("profile"))
        order = Order.objects.get(user=self.user)
        item = OrderItem.objects.get(order=order)
        self.assertEqual(order.total, 690)
        self.assertEqual((item.product, item.quantity, item.price), (self.product, 1, 690))
        self.assertEqual(self.client.session["cart"], {})

    def test_add_to_cart_rejects_external_redirect_target(self):
        response = self.client.post(
            reverse("add_to_cart", args=[self.product.pk]),
            {"next": "https://example.com/"},
        )

        self.assertRedirects(response, reverse("catalog"))
        self.assertEqual(self.client.session["cart"], {str(self.product.pk): 1})

    def test_dashboard_is_staff_only_and_staff_can_update_order_status(self):
        order = Order.objects.create(
            user=self.user, address="ул. Лесная, 5", phone="123", total=690
        )
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 302)

        staff = User.objects.create_user(
            username="staff", password="safe-test-password", is_staff=True
        )
        self.client.force_login(staff)
        response = self.client.post(
            reverse("update_order_status", args=[order.pk]),
            {"status": Order.Status.COOKING},
        )

        self.assertRedirects(response, reverse("dashboard"))
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.COOKING)
