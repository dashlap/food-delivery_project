import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, unique=True, verbose_name='название')),
                ('slug', models.SlugField(max_length=90, unique=True, verbose_name='слаг')),
                ('description', models.CharField(blank=True, max_length=180, verbose_name='описание')),
            ],
            options={
                'verbose_name': 'категория',
                'verbose_name_plural': 'категории',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('new', 'Новый'), ('confirmed', 'Подтверждён'), ('cooking', 'Готовится'), ('delivering', 'В пути'), ('completed', 'Доставлен'), ('cancelled', 'Отменён')], default='new', max_length=12, verbose_name='статус')),
                ('address', models.CharField(max_length=240, verbose_name='адрес доставки')),
                ('phone', models.CharField(max_length=30, verbose_name='телефон')),
                ('comment', models.CharField(blank=True, max_length=300, verbose_name='комментарий')),
                ('total', models.PositiveIntegerField(verbose_name='сумма, ₽')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='создан')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='клиент')),
            ],
            options={
                'verbose_name': 'заказ',
                'verbose_name_plural': 'заказы',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='название')),
                ('slug', models.SlugField(max_length=140, unique=True, verbose_name='слаг')),
                ('description', models.TextField(verbose_name='описание')),
                ('price', models.PositiveIntegerField(verbose_name='цена, ₽')),
                ('weight', models.CharField(max_length=40, verbose_name='вес / объём')),
                ('image_url', models.URLField(blank=True, verbose_name='ссылка на изображение')),
                ('is_available', models.BooleanField(default=True, verbose_name='есть в меню')),
                ('is_popular', models.BooleanField(default=False, verbose_name='популярное')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='menu.category', verbose_name='категория')),
            ],
            options={
                'verbose_name': 'блюдо',
                'verbose_name_plural': 'блюда',
                'ordering': ['-is_popular', 'name'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveSmallIntegerField(verbose_name='количество')),
                ('price', models.PositiveIntegerField(verbose_name='цена на момент заказа, ₽')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='menu.order', verbose_name='заказ')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='order_items', to='menu.product', verbose_name='блюдо')),
            ],
            options={
                'verbose_name': 'позиция заказа',
                'verbose_name_plural': 'позиции заказа',
            },
        ),
    ]
