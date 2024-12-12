from django.shortcuts import render,redirect,get_object_or_404
from admin_side.models import product,ProductVarient,ProductOffer
from admin_side.models import multiimage,Category,Brand
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from cart.models import Orders,order_item
from home.models import Wallet,WalletTransaction
from django.http import JsonResponse
from cart.models import Coupons
from home.models import Notification
import json
from django.db.models import Sum, Count
from datetime import datetime, timedelta
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from decimal import Decimal
from django.db import IntegrityError
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO


from .forms import MultiImageForm

def photo_list(request):
    photos = multiimage.objects.all()  # Fetch all images
    if request.method == 'POST':
        form = MultiImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Save the image with cropping/resizing if applicable
            return redirect('photo_list')  # Replace with your URL name for this view
    else:
        form = MultiImageForm()

    return render(request, 'photo_list.html', {
        'form': form,
        'photos': photos
    })

# Create your views here.
# product management
def is_superuser(user):
    return user.is_authenticated and user.is_superuser

@never_cache
@user_passes_test(is_superuser, login_url='signin')
def product_management(request):
    products=product.objects.all()
    return render(request,'admin/admin_product.html',{'products':products})
@user_passes_test(is_superuser, login_url='signin')
def add_product(request):
    if request.method == 'POST':
        categoriess=Category.objects.all()
        brands=Brand.objects.all()
        title=request.POST.get('name')
        description=request.POST.get('description')
       
        
        brand_id=request.POST.get('brand')
        category_id=request.POST.get('category')

        if not title or not description :
            return render(request,'admin/add_product.html')
        
        image=request.FILES.get('image') if 'image' in request.FILES else None

        #assuming we have a the category's name in category model

        category=Category.objects.get(id=category_id)
        brand=Brand.objects.get(id=brand_id)

        sizes = request.POST.getlist('varient_size[]')
        prices = request.POST.getlist('varient_price[]')
        stocks = request.POST.getlist('varient_stock[]')

        for price in prices:
            if float(price) < 0:
                messages.error(request, "Price cannot be negative.")
                return render(request, 'admin/add_product.html', {'form': request.POST,'categories':categoriess,'brands':brands})
        for stock in stocks:
            if float(stock) < 0:
                messages.error(request, "Stock cannot be negative.")
                return render(request, 'admin/add_product.html', {'form': request.POST,'categories':categoriess,'brands':brands})
            if not stock.isdigit():  # This checks if stock is a valid number
                messages.error(request, "Stock must be a whole number.")
                return render(request, 'admin/add_product.html', {'form': request.POST, 'categories': categories, 'brands': brands})

      
       # Ensure the lists are of equal length before processing
        if len(sizes) == len(prices) == len(stocks):
        
            # Saving the extracted product data
            products, created = product.objects.get_or_create(
                title=title,
                description=description,
                image=image,
                category=category,
                brand=brand
            )

            if not created:
                messages.error(request,'product is already added')

            # Saving each variant related to the product
            for size, price, stock in zip(sizes, prices, stocks):
                # Convert price to Decimal and stock to int for proper storage
                ProductVarient.objects.create(
                    products=products,  # Assigning the actual Product instance
                    size=size,
                    price=Decimal(price),  # Convert price to Decimal
                    stock=int(stock),  # Convert stock to integer
                )

           
        else:
            # Handle the case where the input lists are not of equal length
            messages.error(request, "Mismatched input lengths for sizes, prices, and stocks.")
            print("Error: Mismatched input lengths")
            

        #handling the additional image files
        multipleimages=request.FILES.getlist('additional_images[]')
        for img in multipleimages:
            multiimage.objects.create(product=products,img=img)

        return redirect('product_list')
        
    categories=Category.objects.all()
    brand=Brand.objects.all()
    return render(request,'admin/add_product.html',{'categories':categories,'brands':brand,'range_obj': range(3)})

@user_passes_test(is_superuser, login_url='signin')
def update_product(request,id):
    Product=get_object_or_404(product,id=id)
    product_varient=ProductVarient.objects.filter(products=Product)
    categories=Category.objects.all()
    brand=Brand.objects.all()
    messages.get_messages(request).used = True

    if request.method == 'POST':
        title=request.POST.get('title')
        description=request.POST.get('description')
        category_id=request.POST.get('category')
        brand_id=request.POST.get('brand')
        status=request.POST.get('status')
        image=request.FILES.get('image') if 'image' in request.FILES else None
        Product.category=Category.objects.get(id=category_id)
        Product.brand=Brand.objects.get(id=brand_id)

        Product.title=title
        Product.description=description
        Product.delete_status=status


        if image:
            Product.image=image

        Product.save()

        multipleimages = request.FILES.getlist('multiple') if 'multiple' in request.FILES else None

        if multipleimages:
            Product.multiimage_set.all().delete()
            for img in multipleimages:
            # Create a new MultiImage instance and associate it with the Product
                
                multi_image =multiimage(product=Product, img=img)  # 'img' is the field in MultiImage
                multi_image.save()  # Save the MultiImage instance
        
        variant_sizes = request.POST.getlist('varient_size[]')
        variant_prices = request.POST.getlist('varient_price[]')
        variant_stocks = request.POST.getlist('varient_stock[]')
                        # Check for duplicate sizes
        if len(variant_sizes) != len(set(variant_sizes)):
            messages.error(request, 'Duplicate variant sizes are not allowed')
            
            return render(request,'admin/edit_product.html',{'product':Product,'varient':product_varient,'categories':categories,'brands':brand})

        # Validate at least one variant exists
        if not variant_sizes:
            messages.error(request, 'At least one variant is required')
            return render(request,'admin/edit_product.html',{'product':Product,'varient':product_varient,'categories':categories,'brands':brand})

        # Delete existing variants that were marked for deletion
        deleted_variants = request.POST.get('deleted_variants', '').split(',')
        if deleted_variants[0]:  # Check if there are any deleted variants
            ProductVarient.objects.filter(
                id__in=deleted_variants,
                product=product
            ).delete()

        # Update or create variants
        existing_variants = list(Product.varients.all())
        for i, (size, price, stock) in enumerate(zip(variant_sizes, variant_prices, variant_stocks)):
        
            price = float(price)
            stock = int(stock)
            
            if price <= 0:
                messages.error(request, f'Invalid price for size {size}')
                return render(request,'admin/edit_product.html',{'product':Product,'varient':product_varient,'categories':categories,'brands':brand})
            
            if stock < 0:
                messages.error(request, f'Invalid stock quantity for size {size}')
                return render(request,'admin/edit_product.html',{'product':Product,'varient':product_varient,'categories':categories,'brands':brand})

            # Update existing variant or create new one
            if i < len(existing_variants):
                variant = existing_variants[i]
                variant.size = size
                variant.price = price
                variant.stock = stock
                variant.save()
            else:
                ProductVarient.objects.create(
                    products=Product,
                    size=size,
                    price=price,
                    stock=stock
                )

        

        return redirect('product_list')
    
    
    return render(request,'admin/edit_product.html',{'product':Product,'varient':product_varient,'categories':categories,'brands':brand})

@user_passes_test(is_superuser, login_url='signin')
def delete_product(request,id):
    
    Product=get_object_or_404(product,id=id)
    Product.delete_status=product.DELETE
    Product.save()

    return redirect('product_list')

# category management

@user_passes_test(is_superuser, login_url='signin')
def category_management(request):
    categories=Category.objects.all()

    return render(request,'admin/category_management.html',{'categories':categories})

@user_passes_test(is_superuser, login_url='signin')
def add_category(request):
    if request.method =='POST':
        Name=request.POST.get('name')
        description=request.POST.get('description')

        Category.objects.get_or_create(
            Name=Name,
            description=description,
        )
        return redirect('category_list')

    return render(request,'admin/add_category.html')

@user_passes_test(is_superuser, login_url='signin')
def update_category(request,id):
    category=get_object_or_404(Category,id=id)
    if request.method=='POST':
        name=request.POST.get('name')
        description=request.POST.get('description')
        status=request.POST.get('status')

        category.Name=name
        category.description=description
        category.delete_status=status
        category.save()

        return redirect('category_list')
    
    return render(request,'admin/edit_category.html',{'category':category})

@user_passes_test(is_superuser, login_url='signin')
def delete_category(request,id):
    category=get_object_or_404(Category,id=id)
    if request.method == 'POST':
        
        category.delete_status=Category.DELETE
        category.save()

        return redirect('category_list')
    return render(request,'admin/delete_category.html',{'categories':category})

#brand mannagement

@user_passes_test(is_superuser, login_url='signin')
def brand_mangement(request):
    brand=Brand.objects.all()

    return render(request,'admin/brand_management.html',{'brands':brand})

@user_passes_test(is_superuser, login_url='signin')
def add_brand(request):
    if request.method =='POST':
        Name=request.POST.get('name')
        description=request.POST.get('description')
        image=request.FILES.get('image') if 'image' in request.FILES else None

        Brand.objects.get_or_create(
            Name=Name,
            description=description,
            image=image,
        )
        return redirect('brand_list')

    return render(request,'admin/add_brand.html')

@user_passes_test(is_superuser, login_url='signin')
def update_brand(request,id):
    brand=get_object_or_404(Brand,id=id)
    if request.method=='POST':
        name=request.POST.get('name')
        description=request.POST.get('description')
        status=request.POST.get('status')
        image=request.FILES.get('image') if 'image' in request.FILES else None

        if image:
            brand.image=image

        brand.Name=name
        brand.description=description
        brand.delete_status=status
        brand.save()

        return redirect('brand_list')
    return render(request,'admin/edit_brand.html',{'brands':brand})

@user_passes_test(is_superuser, login_url='signin')
def delete_brand(request,id):
    brand=get_object_or_404(Brand,id=id)
    if request.method == 'POST':
        
        brand.delete_status=Brand.DELETE
        brand.save()

        return redirect('brand_list')
    return render(request,'admin/delete_brand.html',{'brands':brand})
@user_passes_test(is_superuser, login_url='signin')
def user_management(request):
    users=User.objects.exclude(is_superuser=True)
    return render(request,'admin/user_management.html',{'users':users})
@user_passes_test(is_superuser, login_url='signin')
def user_activate(request,id):
    user=get_object_or_404(User,id=id)
    return render(request,'admin/user_activate.html',{'users':user})
@user_passes_test(is_superuser, login_url='signin')
def block_user(request, id):
    user = get_object_or_404(User, id=id)
    if user.is_active:
        user.is_active = False
        user.save()
        messages.success(request, f'{user.username} has been blocked.')
    else:
        messages.info(request, f'{user.username} is already blocked.')
    return redirect('users')
@user_passes_test(is_superuser, login_url='signin')
def unblock_user(request, id):
    user = get_object_or_404(User, id=id)
    if not user.is_active:
        user.is_active = True
        user.save()
        messages.success(request, f'{user.username} has been unblocked.')
    else:
        messages.info(request, f'{user.username} is already active.')
    return redirect('users')
@user_passes_test(is_superuser, login_url='signin')
def block_category(request, id):
    category = get_object_or_404(Category, id=id)
    if category.delete_status==Category.LIVE:
        category.delete_status=Category.DELETE
        
        category.save()
        messages.success(request, f'{category.Name} has been blocked.')
    else:
        messages.info(request, f'{category.Name} is already blocked.')
    return redirect('category_list')
@user_passes_test(is_superuser, login_url='signin')
def unblock_category(request, id):
    
    
    category = get_object_or_404(Category, id=id)
    if category.delete_status==Category.DELETE:
        category.delete_status=Category.LIVE
        
        category.save()
        messages.success(request, f'{category.Name} has been unblocked.')
    else:
        messages.info(request, f'{category.Name} is already unblocked.')
    return redirect('category_list')
@user_passes_test(is_superuser, login_url='signin')
def order_management(request):
    orders = Orders.objects.all().order_by('-order_time')

    order_items=order_item.objects.all
    return render(request,'admin/order_management.html',{'orders':orders,'order_item':order_items})
@user_passes_test(is_superuser, login_url='signin')
def edit_orders(request,id):
    
    if request.method=='POST':
        order_item=get_object_or_404(Orders,id=id)
        order_item.order_status=request.POST.get('status')
        order_item.save()
        return redirect('order_management')

@user_passes_test(is_superuser, login_url='signin')
def cancel_orders(request,id):
    
    if request.method=='POST':

        order_item=get_object_or_404(Orders,id=id)
        wallet,created = Wallet.objects.get_or_create(user=order_item.user)

        print(f"Before Update: Order Status: {order_item.order_status}, Payment Method: {order_item.payment_method}")
        if order_item.order_status=='Delivered':
            order_item.order_status='Return'
            wallet.balance+=order_item.grand_total
            wallet.save()
        elif order_item.order_status in ['pending','Dispatch'] and order_item.payment_method=='cod':
            order_item.order_status='Cancelled'
            
        elif order_item.order_status in ['pending','Dispatch'] and order_item.payment_method=='paypal':
            order_item.order_status='Refund'
            wallet.balance+=order_item.grand_total
            wallet.save()
        order_item.cancellation_status='Approved'
        order_item.cancellation_requested=False
        order_item.save()
               # Notify the user
        Notification.objects.create(
            user=order_item.user,
            head='Order cancellation',
            message=f"Your order #{order_item.id} has been successfully cancelled.",
            is_read=False
        )
       
        WalletTransaction.objects.create(wallet=wallet,
        transaction_type ='CREDIT',
        amount=order_item.grand_total,
        description='Refund',
        )
        return redirect('order_management')
    
@user_passes_test(is_superuser, login_url='signin')   
def approve_denied(request,id):
    
    if request.method=='POST':
        order_item=get_object_or_404(Orders,id=id)
        order_item.cancellation_requested=False
        order_item.save()

        Notification.objects.create(
            user=order_item.user,
            head='Order cancellation',
            message=f"Cancellation denied for your order #{order_item.id}.",
            is_read=False
        )

     
        return redirect('order_management')
@user_passes_test(is_superuser, login_url='signin')
def view_orders(request,id):
    order=get_object_or_404(Orders,id=id)
    order_items=order_item.objects.filter(order=order)
    return render(request,'admin/view_orders.html',{'order':order,'order_item':order_items})

@user_passes_test(is_superuser, login_url='signin')   
def productOffer(request):
    products=product.objects.all()
    offer=ProductOffer.objects.all()
    active_offers_count = ProductOffer.objects.filter(is_active=True).count()
    inactive_offers_count = ProductOffer.objects.filter(is_active=False).count()
   

    context={
        'products':products,
        'offers':offer,
        'active_offers':active_offers_count,
        'inactive_offers':inactive_offers_count,
    }
    
    return render(request,'admin/offer_management.html',context)

# views.py
@user_passes_test(is_superuser, login_url='signin')   
def add_offer(request):
    products=product.objects.all()
    context={
        'products':products,

    }
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('offer_name')
        discount = request.POST.get('discount_value')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        description = request.POST.get('description')
        selected_product = request.POST.get('selected_product')  # Single product ID
        is_active  = request.POST.get('is_active')

        is_active = True if is_active else False
        
        messages.get_messages(request).used = True

     

        # Create an offer for each selected product
        productt = product.objects.get(id=selected_product)

        if start_date>end_date:
            messages.error(request,'Start date cannot be after end date')
            return render(request,'admin/add_productoffer.html',context)

        
                # Check if the product already has an offer
        if ProductOffer.objects.filter(Product=productt).exists():
               messages.error(request,'Product has already one offer')
               return render(request,'admin/add_productoffer.html',context)
      
        ProductOffer.objects.create(
            name=name,
            discount=discount,
            start_date=start_date,
            end_date=end_date,
            description=description,
            Product=productt,
            is_active=is_active,  
        )
       

        return redirect('product_offer')
   
    return render(request,'admin/add_productoffer.html',context)

@user_passes_test(is_superuser, login_url='signin')
def edit_offer(request,id):
    products=product.objects.all()
    offers=get_object_or_404(ProductOffer,id=id)
    context={
        'products':products,
        'offers':offers,
    }
    if request.method=='POST':

        name = request.POST.get('offer_name')
        discount = request.POST.get('discount_value')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        description = request.POST.get('description')
        selected_product = request.POST.get('selected_product')
        is_active  = request.POST.get('is_active')
        

        messages.get_messages(request).used = True

        offers.is_active = True if is_active else False
        existed_product=offers.Product

        productt = product.objects.get(id=selected_product)

        if start_date>end_date:
            messages.error(request,'Start date cannot be after end date')
            return render(request,'admin/edit_productoffer.html',context)
        
        if ProductOffer.objects.filter(Product=productt).exists() and existed_product!=productt:
               messages.error(request,'Product has already one offer')
               return render(request,'admin/edit_productoffer.html',context)

        

        offers.name=name
        offers.discount=discount
        offers.start_date=start_date
        offers.end_date=end_date
        offers.description=description
        offers.Product=productt  

        offers.save()

        return redirect('product_offer')
    

 
    return render(request,'admin/edit_productoffer.html',context)
@user_passes_test(is_superuser, login_url='signin')
def delete_offer(request, offer_id):
    if request.method == "POST":
        offer = get_object_or_404(ProductOffer, id=offer_id)
        offer.delete()
        
        return redirect('product_offer')  # Replace with the URL name of your main product offer page
    return redirect('product_offer')

@user_passes_test(is_superuser, login_url='signin')
def coupons(request):
    products=product.objects.all()
    coupon=Coupons.objects.all
  
    context={
        'products':products,
        'coupons':coupon,
       
    }
    
    return render(request,'admin/coupon.html',context)
@user_passes_test(is_superuser, login_url='signin')
def add_coupon(request):
    messages.get_messages(request).used = True
    if request.method == "POST":
        

        code = request.POST.get('code')
        discount=request.POST.get('discount')
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')
        usage = request.POST.get('usage')

        

        if Decimal(discount) < 0 or Decimal(usage) < 0:
            messages.error(request, "Enter a positive number")
            return redirect('add_coupon')  # Assuming you have a page for adding a coupon



        # Check if the code already exists
        if Coupons.objects.filter(code=code).exists():
            messages.error(request, "This coupon code already exists.")
            return redirect('add_coupon')  # Assuming you have a page for adding a coupon

        # Check if the 'valid_to' date is later than 'valid_from'
        if valid_from >= valid_to:
            messages.error(request, "The 'valid_to' date must be later than 'valid_from'.")
            return redirect('add_coupon')

        # Create the new coupon
        coupon = Coupons(
            code=code,
            valid_from=valid_from,
            valid_to=valid_to,
            discount_percentage=discount,
            maximum_usage_count=usage,
        )
        coupon.save()

     
       
        return redirect('coupons')  
    
    return render(request,'admin/add_coupon.html')
    

@user_passes_test(is_superuser, login_url='signin')
def edit_coupon(request,id):
    coupon=get_object_or_404(Coupons,id=id)
    context={
        'coupon':coupon,
    }
    if request.method == "POST":
        
        code = request.POST.get('code')
        discount=request.POST.get('discount')
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')
        usage = request.POST.get('usage')

        messages.get_messages(request).used = True

        existed_code=coupon.code

        # Check if the code already exists
        if Coupons.objects.filter(code=code).exists() and code != existed_code:
            messages.error(request, "This coupon code already exists.")
            return render(request,'admin/edit_coupon.html',context)  



        # Create the new coupon
        
        coupon.code=code
        coupon.valid_from=valid_from
        coupon.valid_to=valid_to
        coupon.discount_percentage=discount
        coupon.maximum_usage_count=usage
        
        coupon.save()

     
     
        return redirect('coupons')  
    

    return render(request,'admin/edit_coupon.html',context)


@user_passes_test(is_superuser, login_url='signin')
def delete_coupon(request,id):
    if request.method == "POST":
        coupon = get_object_or_404(Coupons, id=id)
        coupon.delete()
        
        return redirect('coupons')  
    return redirect('coupons')


@user_passes_test(is_superuser, login_url='signin')
def dashboard(request):
    report_type = request.GET.get('report_type', 'daily')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    orders = Orders.objects.all()
    today = timezone.now().date()

    # Initialize grouped_sales for chart
    grouped_sales = []

    # Custom date range
    if report_type == 'custom' and start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date() + timedelta(days=1)
        orders = orders.filter(order_time__range=[start_date, end_date])
        grouped_sales = orders.annotate(period=TruncDay('order_time')).values('period').annotate(
            total_sales=Sum('total_price')
        ).order_by('period')

    elif report_type == 'daily':
        orders = orders.filter(order_time__date=today)
        grouped_sales = orders.annotate(period=TruncDay('order_time')).values('period').annotate(
            total_sales=Sum('total_price')
        ).order_by('period')

    elif report_type == 'weekly':
        week_ago = today - timedelta(days=7)
        orders = orders.filter(order_time__date__gte=week_ago)
        grouped_sales = orders.annotate(period=TruncDay('order_time')).values('period').annotate(
            total_sales=Sum('total_price')
        ).order_by('period')

    elif report_type == 'monthly':
        month_ago = today - timedelta(days=30)
        orders = orders.filter(order_time__date__gte=month_ago)
        grouped_sales = orders.annotate(period=TruncDay('order_time')).values('period').annotate(
            total_sales=Sum('total_price')
        ).order_by('period')

    elif report_type == 'yearly':
        year_ago = today - timedelta(days=365)
        orders = orders.filter(order_time__date__gte=year_ago)
        grouped_sales = orders.annotate(period=TruncMonth('order_time')).values('period').annotate(
            total_sales=Sum('total_price')
        ).order_by('period')

    # Summary statistics
    summary = orders.aggregate(
        total_sales=Sum('total_price'),
        total_discounts=Sum('discount'),
        net_revenue=Sum('grand_total')
    )
    total_orders = orders.count()
    total_sales = summary['total_sales'] or 0
    total_discounts = summary['total_discounts'] or 0
    net_revenue = summary['net_revenue'] or 0

    # Prepare grouped_sales (assuming you've already generated this)
    grouped_sales = [
        {"period": sale['period'].strftime('%Y-%m-%d'), "total_sales": str(sale['total_sales'])}
        for sale in grouped_sales
    ]
    print(grouped_sales)

     # Handle export requests
    # Check for export type
    export_type = request.GET.get('export')
    print("Export Type:", export_type)  # Debugging

    if export_type == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

        # Create a SimpleDocTemplate for the PDF
        doc = SimpleDocTemplate(response, pagesize=letter)

        # Define the table header and data
        data = [
            ['Order ID', 'Date', 'Time', 'Customer', 'Items', 'Subtotal', 'Discount', 'Total'],
        ]
        
        # Add order data to the table
        for order in orders:
            data.append([
                f'#{order.id}',
                order.order_time.strftime('%Y-%m-%d'),
                order.order_time.strftime('%H:%M'),
                order.user.first_name,
                len(order.items.all()),
                f'₹{order.total_price}',
                f'₹{order.discount}',
                f'₹{order.grand_total}',
            ])

        # Create the Table object
        table = Table(data)

        # Apply styles to the table
        table_style = TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Header text color
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),  # Header background color
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center the text in all cells
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font style
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Body font style
            ('FONTSIZE', (0, 0), (-1, -1), 10),  # Font size
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding for header row
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Body background color
            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Grid lines
        ])

        table.setStyle(table_style)

        # Build the PDF document
        doc.build([table])

        return response
    best_seller_product,top_category,top_brands=get_top_selling_products()
    print(best_seller_product)
    print(top_category)
        
    # Pass grouped_sales as JSON
    context = {
        'orders': orders,
        'report_type': report_type,
        'start_date': start_date if report_type == 'custom' else '',
        'end_date': end_date if report_type == 'custom' else '',
        'total_sales': total_sales,
        'total_discounts': total_discounts,
        'net_revenue': net_revenue,
        'total_orders': total_orders,
        'best_seller_product':best_seller_product,
        'top_category':top_category,
        'top_brands':top_brands,
        
    'grouped_sales': json.dumps(grouped_sales, default=str),  # Serialize to JSON
    }
    return render(request, 'admin/dashboard.html', context)

def get_top_selling_products():
    top_products = (
    product.objects
    .filter(sold_count__gt=0)  # Filter products with sales
    .order_by('-sold_count')[:5]  # Order by `sold_count` in descending order
    )

    # Assuming each Product belongs to a Category
    top_catgeory = (
        Category.objects
        .annotate(total_sold=Sum('products__sold_count'))  # Aggregate `sold_count` for products in each category
        .filter(total_sold__gt=0)
        .order_by('-total_sold')[:2]
    )

    top_brand = (
        Brand.objects
        .annotate(total_sold=Sum('Product__sold_count'))  # Aggregate `sold_count` for products in each brand
        .filter(total_sold__gt=0)
        .order_by('-total_sold')[:2]
    )
    

    return top_products,top_catgeory,top_brand

