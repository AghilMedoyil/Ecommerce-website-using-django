from django.shortcuts import render,get_object_or_404
from admin_side.models import product,Category,Brand,ProductVarient,ProductOffer
from django.core.paginator import Paginator 
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db.models import Q,Count,Min,Max
from home.models import Notification
from cart.models import Wishlist,WishlistItem
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Lower

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Notification,Wallet
# Create your views here.
@login_required(login_url='signin')
@never_cache
def index(request):
    
    latest_products=product.objects.order_by('-created_at')
   
    return render(request,'index.html',{'latest':latest_products})



@login_required(login_url='signin')
def products(request):
    
    page=1
  
    page=request.GET.get('page',1)
    query = request.GET.get('query', None)
    sort_by = request.GET.get('sort', 'date')  

    Products = product.objects.exclude(delete_status=0)
    category_id = request.GET.getlist('category')
    brand_id = request.GET.getlist('brand')

    if category_id:
        Products = Products.filter(category_id__in=category_id)
    if brand_id:
        Products = Products.filter(brand_id__in=brand_id)

    Products = Products.annotate(
    first_price=Subquery(
        ProductVarient.objects.filter(products=OuterRef('pk'))
        .values('price')[:1]
    )
)


  

# Apply search query filters first
    if query :
        products = products.filter(
            Q(title__icontains=query) |
            Q(category_name__icontains=query) |
            Q(brand_name__icontains=query) |
            Q(varients__price__icontains=query)
        ).distinct()

     # Apply sorting
    if sort_by == 'price_asc':
        Products = Products.order_by('first_price')
    elif sort_by == 'price_desc':
        Products = Products.order_by('-first_price')
    elif sort_by == 'name_a-z':
        Products = Products.order_by(Lower('title'))
    elif sort_by == 'name_z-a':
        Products = Products.order_by(Lower('title').desc())
    
    elif sort_by == 'date':
        Products = Products.order_by('-created_at')  # Assuming `created_at` exists

   
   

    Product_paginator=Paginator(Products,6)
    Products=Product_paginator.get_page(page)
    category=Category.objects.annotate(product_count=Count('products'))
    brands = Brand.objects.annotate(product_count=Count('Product'))  

    context={
        'products':Products,
        'categories':category,
        'brands':brands,
        'query': query,
        'current_sort':sort_by,
        'selected_categories': category_id,
        'selected_brands': brand_id,
        
    }
    return render(request,'products.html',context)

@csrf_exempt
def remove_notification(request, notification_id):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True  # Mark as read
            notification.save()
            return JsonResponse({'success': True})
        except Notification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Notification not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)

@login_required(login_url='signin')
def product_details(request,id,varient):

    Product = get_object_or_404(product, id=id)
    
    # Fetch all unique sizes for this product's variants
    sizes = Product.varients.values_list('size', flat=True).distinct()  # Correct way to access related varients
    
    # Retrieve the specific variant based on the size
    variant_instance = get_object_or_404(ProductVarient, products=Product, size=varient)  # Correct foreign key reference

    # Get the price and quantity of the selected variant
    variant_price = variant_instance.price
    variant_quantity = variant_instance.stock
    wishlist,created=Wishlist.objects.get_or_create(user=request.user)
    wishlist_product_ids = WishlistItem.objects.filter(wishlist=wishlist).values_list('Product__id', flat=True)
    

    # Check if there's an offer for the product and apply it to the variant price
    product_offer = ProductOffer.objects.filter(Product=Product).first()
    

    if product_offer:
        
    
        variant_price -= product_offer.discount

    # Prepare context for the template
    context = {
        'product': Product,
        'sizes': sizes,
        'variant_price': variant_price,
        'variant_quantity': variant_quantity,
        'offer':product_offer,
        'wishlist_item':wishlist_product_ids
    }

    return render(request, 'product_details.html', context)
  

  

def searchbar(request):
    categories=Category.objects.exclude(delete_status=0)
    Product=product.objects.exclude(delete_status=0)

    query=request.GET.get('q')
    if query:
        Product=product.objects.filter(Q(title__icontains=query) | Q(category__Name__icontains=query))
    
        
    category=request.GET.get('category')
    if category=='all_categories':
        return render(request,'products.html',{'products':Product,'categories':categories})
    else:
        if query:
            Product=product.objects.filter(Q(title__icontains=query) & Q(category__Name=category))
        else:
            Product=product.objects.filter(category__Name=category)

        return render(request,'products.html',{'products':Product,'categories':categories})


def wallet(request):
    wallet,created=Wallet.objects.get_or_create(user=request.user)
    return render(request,'wallet.html',{'wallet':wallet})