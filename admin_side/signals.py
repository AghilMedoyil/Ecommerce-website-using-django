from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Category,product,ProductVarient
from cart.models import WishlistItem,Orders,order_item


@receiver(post_save, sender=Category)
def update_related_products(sender, instance, **kwargs):
    """Soft delete related products when a category is soft deleted."""
    related_products = product.objects.filter(category=instance)
    if instance.delete_status == Category.DELETE:
        # Soft delete all related products
        # instance.products.update(delete_status=Category.DELETE)
        related_products.update(delete_status=Category.DELETE) 

    if instance.delete_status == Category.LIVE:
        # Soft delete all related products
        # instance.products.update(delete_status=Category.DELETE)
        related_products.update(delete_status=Category.LIVE) 

@receiver(post_save, sender=ProductVarient)
def update_wishlist_stock(sender, instance, **kwargs):
    WishlistItem.objects.filter(Product=instance.products, size=instance.size).update(
        variant_stock_quantity=instance.stock
    )

@receiver(post_save, sender=Orders)
def update_product_sold_count(sender, instance, **kwargs):
    print(f"Signal triggered for Order ID: {instance.id}, Status: {instance.order_status}")
    if instance.order_status in ['Pending', 'Delivered']:  # Test with both
        for item in instance.items.all():
            print(f"Updating sold_count for product: {item.product}, Quantity: {item.product_quantity}")
            product = item.product
            if product and product.delete_status == product.LIVE:
                product.sold_count += item.product_quantity or 0
                product.save()
                print(f"Sold count updated for Product ID: {product.id}. New sold_count: {product.sold_count}")


    elif instance.order_status in ['Cancelled', 'Refund']:
        for item in instance.items.all():
            product = item.product
            if product:
                product.sold_count -= item.product_quantity or 0
                # Ensure `sold_count` does not drop below 0
                product.sold_count = max(product.sold_count, 0)
                product.save()