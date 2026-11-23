from django.db import migrations


def create_menu(apps, schema_editor):
    Category = apps.get_model("menu", "Category")
    Product = apps.get_model("menu", "Product")
    categories = {
        "pasta": Category.objects.create(
            name="Паста", slug="pasta", description="Итальянские блюда с душой"
        ),
        "salads": Category.objects.create(
            name="Салаты", slug="salads", description="Свежие и сезонные"
        ),
        "main": Category.objects.create(
            name="Основное", slug="main", description="Сытные блюда на каждый день"
        ),
        "desserts": Category.objects.create(
            name="Десерты", slug="desserts", description="Немного сладкого счастья"
        ),
    }
    products = [
        ("Паста с томатами", "pasta-tomato", "Свежая паста, томаты черри, базилик и пармезан.", 690, "320 г", "pasta", "photo-1473093295043-cdd812d0e601", True),
        ("Паста с грибами", "pasta-mushroom", "Кремовый соус, лесные грибы, тимьян и тёртый пармезан.", 740, "340 г", "pasta", "photo-1551183053-bf91a1d81141", True),
        ("Зелёный салат", "green-salad", "Авокадо, свежая зелень, огурец и лёгкая лимонная заправка.", 520, "250 г", "salads", "photo-1512621776951-a57141f2eefd", False),
        ("Боул с лососем", "salmon-bowl", "Лосось, рис, авокадо и хрустящие овощи.", 890, "360 г", "main", "photo-1546069901-ba9599a7e63c", True),
        ("Курица с овощами", "chicken-vegetables", "Запечённая курица, сезонные овощи и соус на травах.", 790, "380 г", "main", "photo-1532550907401-a500c9a57435", False),
        ("Тарт с ягодами", "berry-tart", "Рассыпчатая основа, нежный крем и свежие ягоды.", 420, "160 г", "desserts", "photo-1488477181946-6428a0291777", False),
    ]
    for name, slug, description, price, weight, category, image, popular in products:
        Product.objects.create(
            category=categories[category],
            name=name,
            slug=slug,
            description=description,
            price=price,
            weight=weight,
            image_url=f"https://images.unsplash.com/{image}?auto=format&fit=crop&w=900&q=80",
            is_popular=popular,
        )


def remove_menu(apps, schema_editor):
    Category = apps.get_model("menu", "Category")
    Product = apps.get_model("menu", "Product")
    Product.objects.filter(
        slug__in=[
            "pasta-tomato",
            "pasta-mushroom",
            "green-salad",
            "salmon-bowl",
            "chicken-vegetables",
            "berry-tart",
        ]
    ).delete()
    Category.objects.filter(slug__in=["pasta", "salads", "main", "desserts"]).delete()


class Migration(migrations.Migration):
    dependencies = [("menu", "0001_initial")]

    operations = [migrations.RunPython(create_menu, remove_menu)]
