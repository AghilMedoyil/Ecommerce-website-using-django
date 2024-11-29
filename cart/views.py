from django.shortcuts import render,redirect,get_object_or_404
from admin_side.models import product,ProductVarient
from userprofile.models import customer,addresses
from django.http import JsonResponse
from .models import Orders,order_item,Coupons,coupon_usage
from django.utils import timezone
from django.contrib import messages
from decimal import Decimal
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from home.models import Notification,Wallet
from django.core.mail import EmailMessage

from .models import cart,cartitem,Wishlist,WishlistItem
# Create your views here.
@login_required(login_url='signin')
def view_cart(request):
    Cart,created=cart.objects.get_or_create(user=request.user)
    cart_item=cartitem.objects.filter(Cart=Cart).select_related('Product')
    total_price=sum(item.quantity*item.price for item in cart_item)
    return render(request,'cart.html',{'cart_items':cart_item,'total_price':total_price})


@login_required(login_url='signin')
def add_to_cart(request, id):
    if request.method=='POST':
        Product = get_object_or_404(product, id=id)
        varient_id=request.POST.get('variant')
        varient=get_object_or_404(ProductVarient,id=varient_id)

        variant_price=request.POST.get('variant_price')
        print(variant_price)
        
        # Get or create the user's cart
        Cart, created = cart.objects.get_or_create(user=request.user)
        
        # Get or create the cart item for this product in the user's cart
        cart_item, item_created = cartitem.objects.get_or_create(Cart=Cart, Product=Product, varient=varient)
            # Clear any old messages
        storage = messages.get_messages(request)
        storage.used = True
        
        # Update quantity and save the cart item
        if not item_created:
            if cart_item.quantity >= 5:
                messages.error(request, "Quantity limit exceeded. You cannot add more than 5 items to the cart.")
                
                return redirect('productsdetail', id=Product.id, varient=varient.size)

            
            elif cart_item.quantity >= cart_item.varient.stock:
                messages.error(request, "Quantity limit exceeded. Product stock is limited")
                
                return redirect('productsdetail', id=Product.id, varient=varient.size)

            else:

                cart_item.quantity += 1
        else:
            cart_item.quantity = 1
            cart_item.price = variant_price
        
        cart_item.save()
        
    # Retrieve all items in the user's cart for display
    cart_items = cartitem.objects.filter(Cart=Cart).select_related('Product','varient')
    total_price = sum(item.quantity * item.price for item in cart_items)   
   
    return render(request, 'cart.html', {'cart': Cart, 'cart_items': cart_items, 'total_price': total_price})


@login_required(login_url='signin')        
def remove_cartitem(request,id):
    if request.method=='POST':
        cart_item=get_object_or_404(cartitem,id=id)
        cart_item.delete()
        return redirect('cart')


@login_required(login_url='signin')
def checkout(request):
    
    host= request.get_host()

   
    Cart=cart.objects.get(user=request.user)
    Cartitem=cartitem.objects.filter(Cart=Cart)
    order = Orders.objects.all()
    wallet=Wallet.objects.get(user=request.user)

    address=addresses.objects.filter(user=request.user)
    total_price=sum(item.quantity*item.price for item in Cartitem)   
    discount=0
   
    shipping_price=30
    tax=10
    HI=10.00
    grand_total=total_price+shipping_price+tax
   

    context={
        'cart':Cart,
        'cart_item':Cartitem,
        'address':address,
        'total_price':total_price,
        'shipping_price':shipping_price,
        'tax':tax,
        'grand_total':grand_total,
        'discount':discount,
        'wallet':wallet,
        
       
    }
   

    if request.method == 'POST':
        address_id = request.POST.get('address')
       
        Address=addresses.objects.get(id=address_id)
        grand_total=request.POST.get('grand_total')
        total=request.POST.get('total_price')
        discount=request.POST.get('discount')
        wallet=request.POST.get('wallet',0)
        grand_total = Decimal(grand_total)  # Convert grand_total to a float
        wallet_balance = Decimal(wallet)  # Convert wallet balance to a float
        waalet=Wallet.objects.get(user=request.user)

# Subtract wallet balance from grand total
        grand = grand_total - wallet_balance
        if wallet_balance > 0:
            waalet.balance-=wallet_balance
            waalet.save()


    
        # Get the selected payment method from the form
        payment_method = request.POST.get('payment_method')

        if grand==0:
            payment_method = 'wallet'
            
            order = create_order(request.user, Address, total, grand_total, discount, shipping_price, tax, Cartitem,payment_method)

            return redirect('order_success' ,id=order.id)


        if payment_method == 'paypal':
            paypal_checkout={
                'business':settings.PAYPAL_RECEIVER_EMAIL,
                'amount':grand_total,
                'invoice':uuid.uuid4(),
                'item_name':'hello',
                'currency_code':'USD',
                'notify_url': f"http://{host}{reverse('paypal-ipn')}",
                'return_url': f"http://{host}{reverse('payment-success')}?address_id={address_id}&total_price={total}&grand_total={grand_total}&discount={discount}&payment_method={payment_method}",
                'cancel_url':  f"http://{host}{reverse('payment-failed')}",
                
                }
            paypal_payment=PayPalPaymentsForm(initial=paypal_checkout)

            context={
                'paypal':paypal_payment,
                'grand_total':grand_total,
                'total_price':total_price,
                'shipping_price':shipping_price,
                'tax':tax,
            }

            return render(request,'payment.html',context)
        
        order = create_order(request.user, Address, total, grand_total, discount, shipping_price, tax, Cartitem,payment_method)

        return redirect('order_success' ,id=order.id)
    return render(request,'checkout.html',context)



def create_order(user, Address, total, grand_total, discount, shipping_price, tax, Cartitem,payment_method):
    full_address = f"{Address.address1}, {Address.address2}, {Address.city}, {Address.district}, {Address.state}"
    order = Orders.objects.create(
            user=user,
            order_time=timezone.now(),
            user_address=full_address,
             # Assuming you want to store the total price for the order
            order_status='pending',
            shipping_price=shipping_price,
            tax=tax,
            grand_total=grand_total,
            total_price=total,
            discount=discount,
            payment_method=payment_method,
        )

        # Create order items for each item in the cart, linking them to the created order
    for item in Cartitem:
        order_item.objects.create(
            order=order,# Associate this order item with the order we just created
            product=item.Product,
            product_quantity=item.quantity,
            product_price=item.price,
            varient=item.varient,
            
            # Use item price times quantity for the order item
        )
    for item in Cartitem:
        item.varient.stock-=item.quantity
        item.varient.save()
    
     # Email details
    subject = f"Order #{order.id} Confirmation"
    recipient_email = order.user.email
    message = f"""
    <html>
        <body>
            <p>Dear {order.user.first_name},</p>
            <p>Your order <strong>#{order.id}</strong> has been successfully placed!</p>
            <p>Thank you for shopping with us!</p>
            <p>Best regards,<br>Shop.Co</p>
        </body>
    </html>
    """
    
    # Send email
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        to=[recipient_email],
    )
    email.content_subtype = 'html'  # Specify email format as HTML
    email.send(fail_silently=False)


    # Optionally clear the cart
    Cartitem.delete()
    return order


@login_required(login_url='signin')
def apply_coupon(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        coupon_code = request.POST.get('coupon_code')
        grand_total = Decimal(request.POST.get('grand_total', 0))

        try:
            coupon = Coupons.objects.get(code=coupon_code, is_active=True)
            discount_amount = (grand_total * Decimal(coupon.discount_percentage)) / Decimal(100)
            grand_total = grand_total - discount_amount
            

            return JsonResponse({
                'success': True,
                'discount_amount': float(discount_amount),
                'grand_total': float(grand_total),
                'message': f"Coupon '{coupon_code}' applied successfully!"
            })
        except Coupons.DoesNotExist:
            return JsonResponse({'success': False, 'message': "Invalid or expired coupon code."})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f"An error occurred: {str(e)}"})

    return JsonResponse({'success': False, 'message': "Invalid request."})


@login_required(login_url='signin')
def quantity_plus(request, item_id):
    item = get_object_or_404(cartitem, pk=item_id)
    cart = item.Cart

    item.quantity += 1
    response_data = {}

    if item.quantity > item.varient.stock:
        response_data['error'] = 'product has only limited stocks'

    elif item.quantity <= 5:
        item.save()
    else:
        response_data['error'] = 'Each customer is limited to a maximum purchase quantity of 5 units'

    response_data['quantity'] = item.quantity
    item_subtotal = item.price * item.quantity
   
    response_data['item_subtotal'] = item_subtotal
    response_data['item_id'] = item_id

    total_price = sum(item.price * item.quantity for item in cartitem.objects.filter(Cart=cart))
   
    response_data['total_price'] = total_price
 
    return JsonResponse(response_data)



@login_required(login_url='signin')
def quantity_minus(request, item_id):
    item = get_object_or_404(cartitem, pk=item_id)
    cart = item.Cart
    item.quantity -= 1
    response_data = {}

    if item.quantity != 0:
        item.save()
    else:
        response_data['error'] = 'Product quantity must be at least 1'

    response_data['quantity'] = item.quantity
    total_price = sum(item.price * item.quantity for item in cartitem.objects.filter(Cart=cart))
    
    response_data['total_price'] = total_price
    return JsonResponse(response_data)


@login_required(login_url='signin')
def order_success(request,id):
    order=get_object_or_404(Orders,id=id)
    Notification.objects.create(
            user=order.user,
            head='Order Placed',
            message=f"#{order.id} has been successfully placed.",

            is_read=False
        )
    return render(request,'order_success.html',{'order':order})


@login_required(login_url='signin')
def wishlist(request):
    user=request.user
    wishlist,created=Wishlist.objects.get_or_create(user=user)
    wishlist_item=WishlistItem.objects.filter(wishlist=wishlist).prefetch_related('Product__varients')

    context={
        'wishlist_item':wishlist_item
    }
       
    return render(request,'wishlist.html',context)


@login_required(login_url='signin')
def add_to_wishlist(request,id):

    Product=get_object_or_404(product,id=id)
    variant_size=request.GET.get('variant_size')
    variant_price=request.GET.get('variant_price')

    varient=ProductVarient.objects.get(size=variant_size,products=Product)
    print(variant_size)
    print(varient)
    price=variant_price
    stock=varient.stock

    
    wishlist,created=Wishlist.objects.get_or_create(user=request.user)
    variant_exists = WishlistItem.objects.filter(
    wishlist=wishlist,
    Product=Product,
    size=variant_size
    ).exists()
    if not variant_exists:

        wishlist_item,item_created=WishlistItem.objects.get_or_create(wishlist=wishlist,
                                                                    Product=Product,
                                                                    size=variant_size,
                                                                    price=price,
                                                                    variant_stock_quantity=stock)

    wishlist_item=WishlistItem.objects.filter(wishlist=wishlist).prefetch_related('Product__varients')
    context={
        'wishlist_item':wishlist_item,
    
    }
    
    return render(request,'wishlist.html',context)


@login_required(login_url='signin')
def remove_wishitem(request,id):
    if request.method=='POST':
        wish_item=get_object_or_404(WishlistItem,id=id)
        wish_item.delete()
        return redirect('wishlist')
    

@login_required(login_url='signin')
def add_to_wishlistcart(request, id):
    if request.method=='POST':

        wishlist_item=get_object_or_404(WishlistItem,id=id)
        Product=wishlist_item.Product
        variant_size=wishlist_item.size
        # Product = get_object_or_404(product, id=id)
        # varient_id=request.POST.get('variant')
        varient=get_object_or_404(ProductVarient,size=variant_size,products=Product)

        # variant_price=request.POST.get('variant_price')
        # print(variant_price)
        
        # Get or create the user's cart
        Cart, created = cart.objects.get_or_create(user=request.user)
        
        # Get or create the cart item for this product in the user's cart
        cart_item, item_created = cartitem.objects.get_or_create(Cart=Cart, Product=Product, varient=varient)
        
        
        # Update quantity and save the cart item
        if not item_created:
            if cart_item.quantity >= 5:
                messages.error(request, "Quantity limit exceeded. You cannot add more than 5 items to the cart.")
                
                return redirect('productsdetail', id=Product.id)
            
            elif cart_item.quantity >= cart_item.varient.stock:
                messages.error(request, "Quantity limit exceeded. Product stock is limited")
                
                return redirect('productsdetail', id=Product.id)

            else:

                cart_item.quantity += 1
        else:
            cart_item.quantity = 1
            cart_item.price = wishlist_item.price
        
        cart_item.save()
        wishlist_item.delete()
        
        
    # Retrieve all items in the user's cart for display
    cart_items = cartitem.objects.filter(Cart=Cart).select_related('Product','varient')
    total_price = sum(item.quantity * item.price for item in cart_items)   
   
    return render(request, 'cart.html', {'cart': Cart, 'cart_items': cart_items, 'total_price': total_price})


@login_required(login_url='signin')
def payment_success(request):
    address_id = request.GET.get('address_id')
    total = request.GET.get('total_price')
    grand_total = request.GET.get('grand_total')
    discount = request.GET.get('discount')
    Address=addresses.objects.get(id=address_id)
    payment_method=request.GET.get('payment_method')

    
    Cart = cart.objects.get(user=request.user)
    Cartitem = cartitem.objects.filter(Cart=Cart)

    order = create_order(
        user=request.user,
        Address=Address,
        total=total,
        grand_total=grand_total,
        discount=discount,
        shipping_price=30,
        tax=10,
        Cartitem=Cartitem,
        payment_method=payment_method,
    )
    Cartitem.delete()
    return redirect('order_success', id=order.id)


@login_required(login_url='signin')
def payment_failed(request):
    return render(request,'payment_failed.html')