from django.conf import settings
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField("название", max_length=80, unique=True)
    slug = models.SlugField("слаг", max_length=90, unique=True)
    description = models.CharField("описание", max_length=180, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "категория"
        verbose_name_plural = "категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products", verbose_name="категория"
    )
    name = models.CharField("название", max_length=120)
    slug = models.SlugField("слаг", max_length=140, unique=True)
    description = models.TextField("описание")
    price = models.PositiveIntegerField("цена, ₽")
    weight = models.CharField("вес / объём", max_length=40)
    image_url = models.URLField("ссылка на изображение", blank=True)
    is_available = models.BooleanField("есть в меню", default=True)
    is_popular = models.BooleanField("популярное", default=False)

    class Meta:
        ordering = ["-is_popular", "name"]
        verbose_name = "блюдо"
        verbose_name_plural = "блюда"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"slug": self.slug})


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новый"
        CONFIRMED = "confirmed", "Подтверждён"
        COOKING = "cooking", "Готовится"
        DELIVERING = "delivering", "В пути"
        COMPLETED = "completed", "Доставлен"
        CANCELLED = "cancelled", "Отменён"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders", verbose_name="клиент"
    )
    status = models.CharField(
        "статус", max_length=12, choices=Status.choices, default=Status.NEW
    )
    address = models.CharField("адрес доставки", max_length=240)
    phone = models.CharField("телефон", max_length=30)
    comment = models.CharField("комментарий", max_length=300, blank=True)
    total = models.PositiveIntegerField("сумма, ₽")
    created_at = models.DateTimeField("создан", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "заказ"
        verbose_name_plural = "заказы"

    def __str__(self):
        return f"Заказ №{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name="заказ"
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="order_items", verbose_name="блюдо"
    )
    quantity = models.PositiveSmallIntegerField("количество")
    price = models.PositiveIntegerField("цена на момент заказа, ₽")

    class Meta:
        verbose_name = "позиция заказа"
        verbose_name_plural = "позиции заказа"

    def __str__(self):
        return f"{self.product} × {self.quantity}"
