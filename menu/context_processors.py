def cart(request):
    items = request.session.get("cart", {})
    return {"cart_count": sum(items.values())}
