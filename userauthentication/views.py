from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import get_user_model,authenticate,login,logout
from django.views.decorators.cache import never_cache
import re
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
import random
import time
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

OTP_VALIDITY_DURATION = 300

def generate_otp(email):
    return random.randint(100000, 999999)  # Generate a 6-digit OTP

def demo_login(request):
    # Authenticate demo user
    demo_user = authenticate(email='demo@gmail.com', password='demo@1234')
    
    if demo_user is not None:
        login(request, demo_user)  # Log the demo user in
        return redirect('home')  # Redirect to home or dashboard page
    
# Create your views here.
@never_cache
def signin_view(request):
    if request.method == 'POST':
        username=request.POST['username']
        password=request.POST['pass1']
        User=authenticate(username=username,password=password)

             # Clear any old messages
        storage = messages.get_messages(request)
        storage.used = True

        if User is not None:
            login(request,User)
            if User.is_staff:
                return redirect('product_list')
            else:
                if User.is_active:
                    return redirect('home')
                    
                else:
                    messages.error(request,'user is blocked')
                    return render(request,'login.html')
                    
        
        else:
            messages.error(request,'incorect username or password')
            return render(request,'login.html')
    else:
        return render(request,'login.html')
    

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def signup_view(request):
    User = get_user_model()
        # Clear any old messages
    storage = messages.get_messages(request)
    storage.used = True
    if request.method == 'POST':
        username=request.POST['username']
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']

        if not is_valid_email(email):
            messages.error(request, 'Invalid email format')
            return render(request, 'signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request,'email already exists')
            return render(request,'signup.html')
        if User.objects.filter(username=username).exists():
            messages.error(request,'username already exists')
            return render(request,'signup.html')


        if pass1!=pass2:
            messages.error(request,'passwords do not match')
            return render(request,'signup.html')
        else:
             # Generate OTP
            otp = generate_otp(email)
            request.session['otp'] = otp
            request.session['otp_time'] = time.time()

            request.session['email'] = email
            request.session['username'] = username

            request.session['pass1'] = pass1


            # Send OTP via email
            send_mail(
                'Your OTP Code',
                f'Your OTP code is: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            # Redirect to OTP verification page
            return redirect('verify_otp')  # Ensure you have this URL mapped
            
    return render(request,'signup.html')

def verify_otp(request):
    User = get_user_model()
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')  # Retrieve OTP from session
        otp_time = request.session.get('otp_time')
        email = request.session.get('email')  # Retrieve email from session
        username = request.session.get('username')
        password=request.session.get('pass1')
        print(email)

        current_time = time.time()
        # Check if the OTP matches
        if session_otp and int(entered_otp) == session_otp and (current_time - otp_time) < OTP_VALIDITY_DURATION:
            # Create user if OTP is valid
            user = User(email=email,username=username)
            user.set_password(password)  # Set the password
            user.save()
            print(email)

            # Clear OTP from session
            del request.session['otp']
            del request.session['email']
            del request.session['username']


            messages.success(request, 'Signup successful! You can now log in.')
            return redirect('signin')
        else:
            # OTP is either invalid or expired
            if (current_time - otp_time) >= OTP_VALIDITY_DURATION:
                messages.error(request, 'OTP has expired. Please request a new OTP.')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'verify_otp.html')

def resend_otp(request):
    email = request.session.get('email')  # Get the email from session
    if email:
        # Generate and send a new OTP
        otp = generate_otp(email)
        request.session['otp'] = otp  # Update the OTP in the session
        request.session['otp_time'] = time.time()  # Reset the timer
         # Send OTP via email
        send_mail(
            'Your OTP Code',
            f'Your OTP code is: {otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        messages.success(request, 'OTP resent to your email!')

    return redirect('verify_otp')

@login_required(login_url='signin')
def signout(request):   
    logout(request)
        # Clear any old messages
    storage = messages.get_messages(request)
    storage.used = True
    messages.success(request, 'Successfully logged out')
    return redirect('signin')

def forgotten_password(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')

        # Check if the user with the provided email exists
        try:
            user = User.objects.get(email=email)

            # Check if the user is active
            if user.is_active:
                 # Generate OTP
                otp = generate_otp(email)
                request.session['otp'] = otp
                request.session['otp_time'] = time.time()

                request.session['email'] = email
                


                # Send OTP via email
                send_mail(
                    'Your OTP Code',
                    f'Your OTP code is: {otp}',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                    # Redirect to the OTP verification page
                return redirect('verify_forgot_otp',id=user.id)
            else:
                messages.error(request, 'The user is blocked.')
                return render(request, 'forgot_password.html')

        except User.DoesNotExist:
            # User with the email does not exist
            messages.error(request, 'The provided email does not exist.')
            return render(request, 'forgot_password.html')

    # If GET request, render the password reset form
    return render(request, 'forgot_password.html')

def verify_forgot_otp(request,id):
    User = get_user_model()
    user=User.objects.get(id=id)
    
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')  # Retrieve OTP from session
        otp_time = request.session.get('otp_time')
        email = request.session.get('email')  # Retrieve email from session
        user=User.objects.get(email=email)

        current_time = time.time()
        # Check if the OTP matches
        if session_otp and int(entered_otp) == session_otp and (current_time - otp_time) < OTP_VALIDITY_DURATION:
            

            # Clear OTP from session
            del request.session['otp']
            del request.session['email']

            
            return redirect('password_reset',id=user.id)
        else:
            # OTP is either invalid or expired
            if (current_time - otp_time) >= OTP_VALIDITY_DURATION:
                messages.error(request, 'OTP has expired. Please request a new OTP.')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'verify_forgot_otp.html')

def password_reset(request,id):
    user=User.objects.get(id=id)

    if request.method=='POST':
        password1=request.POST.get('pass1')
        password2=request.POST.get('pass2')

        if password1==password2:
            user.set_password(password1)
            user.save()

            messages.success(request, 'Password reset successfully.')
            return redirect('signin')
        
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request,'password_change.html',{'user': user})

def reset_resend_otp(request):
    email = request.session.get('email')  # Get the email from session
    if email:
        # Generate and send a new OTP
        otp = generate_otp(email)
        request.session['otp'] = otp  # Update the OTP in the session
        request.session['otp_time'] = time.time()  # Reset the timer
         # Send OTP via email
        send_mail(
            'Your OTP Code',
            f'Your OTP code is: {otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        messages.success(request, 'OTP resent to your email!')

    return redirect('verify_forgot_otp')





    

