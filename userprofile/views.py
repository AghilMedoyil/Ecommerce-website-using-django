from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User
from . models import customer,addresses
from django.contrib import messages
from cart.models import Orders,order_item
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors


# Create your views here.
@login_required
def profile_view(request):
    user=request.user
    Customer, created = customer.objects.get_or_create(user=user)

    if request.method=='POST':
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        

        user.first_name=first_name
        user.last_name=last_name
        

        user.save()
        
  
        return render(request,'userprofile/user_profile.html',{'user':user})
    
    return render(request,'userprofile/user_profile.html',{'user':user})
def orders_list(request):
    user=request.user
    orders = Orders.objects.filter(user=user).order_by('-order_time')
   
    return render(request,'userprofile/orders_list.html',{'orders':orders})

def export_invoice(request, order_id):
    # Get the specific order based on the order ID
    order = get_object_or_404(Orders, id=order_id, user=request.user)

    # Only allow generating an invoice for orders with certain statuses
    if order.order_status not in ['pending', 'Dispatch','Delivered']:
        return HttpResponse("Invoice cannot be generated for this order status.", status=400)

    # Create the response with a PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_Order_{order_id}.pdf"'

    # Create a SimpleDocTemplate for the PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)

    # Prepare the data for the table
    data = [
        ['Product', 'Variant', 'Quantity', 'Price', 'Total']
    ]

    # Add the order item details to the table
    for item in order.items.all():
        data.append([
            item.product.title,  # Product name
            item.varient.size if item.varient else "N/A",  # Variant name
            item.product_quantity,  # Quantity
            f'₹{item.product_price}',  # Price per item
            f'₹{item.product_price * item.product_quantity}',  # Total price for this item
        ])

    # Add the total order amount and other order details
    data.append(['', '', '', 'Subtotal', f'₹{order.total_price}'])
    data.append(['', '', '', 'Discount', f'₹{order.discount}'])
    data.append(['', '', '', 'Grand Total', f'₹{order.grand_total}'])

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

    # Build the PDF document with the table
    doc.build([table])

    return response
def view_order(request,id):
    orders=get_object_or_404(Orders,id=id)
    Order_item=order_item.objects.filter(order=orders)

    return render(request,'userprofile/view_order.html',{'order_item':Order_item,'order':orders})

def request_cancel(request,id):
    
    if request.method=='POST':
        
        
        order_item=get_object_or_404(Orders,id=id)
        order_item.cancellation_reason=request.POST.get('cancellation_reason')
        order_item.cancellation_requested=True
        order_item.cancellation_status='Pending'
        order_item.save()
        return redirect('orders_list')
def manage_address(request):
    address=addresses.objects.filter(user=request.user)
   
    return render(request,'userprofile/manage_addresses.html',{'address':address})

def change_pass(request):
    return render(request,'userprofile/change_pass.html')

def edit_address(request,id):
    Address=get_object_or_404(addresses,id=id)
    if request.method=='POST':
        address1=request.POST.get('ad-1')
        address2=request.POST.get('ad-2')
        city=request.POST.get('city')
        district=request.POST.get('district')
        state=request.POST.get('state')
        pincode=request.POST.get('pincode')
        # Clear any old messages
        storage = messages.get_messages(request)
        storage.used = True

        if not pincode.isdigit():
            messages.error(request, "Pincode must be a valid number.")
            return render(request,'userprofile/edit_address.html',{'address':Address})
            
        if len(pincode)!=6:
            messages.error(request,"pincode should be exactly 6 digits.")
            return render(request,'userprofile/edit_address.html',{'address':Address})
            

        Address.address1=address1
        Address.address2=address2
        Address.city=city
        Address.district=district
        Address.state=state
        Address.pincode=pincode

        Address.save()

        return redirect('manage_address')

    return render(request,'userprofile/edit_address.html',{'address':Address})
def add_address(request):
    user=request.user
    
    # Address=addresses.objects.get(Customer=Customer)
    if request.method == 'POST':
        errors={}
        address1=request.POST.get('ad-1')
        address2=request.POST.get('ad-2')
        city=request.POST.get('city')
        district=request.POST.get('district')
        state=request.POST.get('state')
        pincode=request.POST.get('pincode')

        # Clear any old messages
        storage = messages.get_messages(request)
        storage.used = True

        if not pincode.isdigit():
            messages.error(request, "Pincode must be a valid number.")
            return redirect('add_address')  
        
        if len(pincode)!=6:
            messages.error(request,"pincode should be exactly 6 digits.")
            return redirect('add_address')

        address,created=addresses.objects.get_or_create(
            user=request.user,
            address1=address1,
            address2=address2,
            city=city,
            district=district,
            state=state,
            pincode=pincode,
        )
        

        # if address in Address:
        #     errors['message']='this address is already there'
        next_param=request.GET.get('next')
        if next_param == 'checkout':
            return redirect('checkout')

        return redirect ('manage_address')
    

        
    Address=addresses.objects.all()    


    return render(request,'userprofile/add_address.html',{'address':Address})
def delete_address(request,id):
    Address=get_object_or_404(addresses,id=id)
    if request.method=='POST':
        Address.delete()
        return redirect('manage_address')

    


    

