from django.shortcuts import render,redirect
from django.contrib.auth import get_user_model
# from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth import login,authenticate,logout
from .models import CustomUser,UserReferral
from wallet_app.models import *
from django.db.models import F
from .validators import Authentication_check

from allauth.socialaccount.models import SocialAccount

from django.views.decorators.cache import never_cache

# Email sending and OTP
from .utils import send_otp
from django.core.mail import EmailMessage
from datetime import datetime,timedelta
from django.utils.timezone import now
import pyotp

User = get_user_model()


def validation_view(request,email,first_name,last_name,password,confirm_password):
    #created object for user validation Authentication_check
    user_validation = Authentication_check()
    
    errors = {}
    
    
    #email validation
    email_valid = user_validation.email_validator(email)
    if email_valid:
        errors['email_error'] = email_valid
        
    #first_name validation
    first_name_valid = user_validation.first_name_validator(first_name)
    if first_name_valid:
        errors['first_name_error'] = first_name_valid
    
    #last_name validation
    last_name_valid = user_validation.last_name_validator(last_name)
    if last_name_valid:
        errors['last_name_error'] = last_name_valid
        
    #password validation
    password_valid = user_validation.pass_validator(password)
    if password_valid:
        errors['password_error'] = password_valid
    
    #password mismatch checking
    password_mismatch = user_validation.password_mismatch(password, confirm_password)
    if password_mismatch:
        errors['password_mismatch'] = password_mismatch
    
    
    
    return errors


def register_view(request):
    if request.user.is_authenticated:
        return redirect('user_app:home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        username = email
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        referral_code = request.POST.get('referral_code')
        
        
        # Setting the token to access the verify_otp view
        request.session['otp_verification_allowed'] = True
        
        # validating the request data
        errors = validation_view(request,email,first_name,last_name,password,confirm_password)    
        
        if referral_code:
            try:
                # Check if referral code exists in the UserReferral model
                referral = UserReferral.objects.get(referral_code=referral_code)
                request.session['referral_code'] = referral_code
            except UserReferral.DoesNotExist:
                # If referral code is invalid, add an error message
                errors['referral_error'] = "Invalid referral code. Please check and try again."

            
        if errors:
            context = {
                'errors' : errors,
                'email' : email,
                'first_name' : first_name,
                'last_name' : last_name,
                'referral_code' : referral_code,
            }
            
            return render(request,'authentication_app/sign_up.html', context)
        
        # checking the user is already exist or not
        elif CustomUser.objects.filter(email = email).exists():
            
            user_obj = CustomUser.objects.get(email = email)
            
            if not user_obj.is_active:  # If user is not active 
                # Generating OTP
                otp = send_otp(request)
                
                # Save the OTP to session
                request.session['registration_otp'] = otp
                request.session['registered_email'] = email

                # Send the OTP via email
                mail_subject = 'Your OTP for email verification'
                message = f'Your OTP is {otp}. Please enter it to verify your email.'
                try:
                    email_message = EmailMessage(mail_subject, message, to=[email])
                    email_message.send()
                except Exception as e:
                    messages.error(request, 'Error sending email. Please try again.')
                    return None

                
                return redirect('authentication_app:verify_otp')  # Redirect to OTP verification page
            else:
                messages.error(request, 'Email already exists!')
        
        else:
            # Saving the user with field is_active as False
            user = CustomUser(email = email,username = username, first_name = first_name, last_name = last_name)
            user.set_password(password)
            user.is_active = False
            user.save()
            
            # Generating OTP
            otp = send_otp(request)
            
            # Save the OTP to session
            request.session['registration_otp'] = otp
            request.session['registered_email'] = email

            # Send the OTP via email
            mail_subject = 'Your OTP for email verification'
            message = f'Your OTP is {otp}. Please enter it to verify your email.'
            try:
                email_message = EmailMessage(mail_subject, message, to=[email])
                email_message.send()
                messages.success(request, 'OTP has been sent to your email.')
            except Exception as e:
                messages.error(request, 'Error sending email. Please try again.')
                return None

            
            return redirect('authentication_app:verify_otp')  # Redirect to OTP verification page

    else:
        pass
    
    return render(request, 'authentication_app/sign_up.html')

@never_cache
def verify_otp(request):
    if request.user.is_authenticated:
        return redirect('user_app:home')
    
    # Checking the token to allow to the OTP page
    if not request.session.get('otp_verification_allowed'):
        return redirect('authentication_app:sign_up')
    
    if request.method == 'POST':
        
        # combining all the otp
        input_otp_values = [request.POST.get(f'otp{i}') for i in range(1,7)]
        input_otp = ''.join([otp if otp is not None else '' for otp in input_otp_values])
        
        # Retrieving session data
        session_otp = request.session.get('registration_otp')
        session_email = request.session.get('registered_email')
        otp_secret_key = request.session['otp_secret_key']
        otp_valid_until = request.session['otp_valid_date']
        referral_code = request.session['referral_code']
        
        
        
        # Ensure all necessary session data exists
        if not all([session_otp,session_email,otp_secret_key,otp_valid_until]):
            messages.error(request,'Session expired or invalid. Please register again.')
            return redirect('authentication_app:sign_up')
        
        valid_until = datetime.fromisoformat(otp_valid_until)
            
        # Checking the OTP is still valid
        if valid_until <= datetime.now():
            messages.error(request,'OTP has been expired. Please request a new one.')
            return redirect('authentication_app:sign_up')
        
        # Verify OTP
        try:
            totp = pyotp.TOTP(otp_secret_key, interval=180)
            
            if not totp.verify(input_otp):
                messages.error(request, 'Invalid OTP. Please try again.')
                return redirect('authentication_app:verify_otp')
            
            # Activate the user
            user = CustomUser.objects.get(email = session_email)
            user.is_active = True
            user.save()
            
            # Creating referral code for the new user.
            new_referral_code = generate_referral_code(user.id)
            
            UserReferral.objects.create(
                user=user,
                referral_code = new_referral_code,
            )
            
            if referral_code:
                try:
                    # If signup is using a referral code, credit both users
                    # Creating/Updating wallet for the new user
                    wallet, created = Wallet.objects.get_or_create(user=user)
                    
                    WalletTransation.objects.create(
                        wallet=wallet,
                        transaction_type='referral',
                        amount=1000,  # Amount for the referral reward
                    )
                    wallet.balance = F('balance') + 1000
                    wallet.save()

                    # Credit referrer’s wallet
                    referred_user = UserReferral.objects.get(referral_code=referral_code)
                    referrer_wallet, created = Wallet.objects.get_or_create(user=referred_user.user)
                    WalletTransation.objects.create(
                        wallet=referrer_wallet,
                        transaction_type='referral',
                        amount=1000,
                    )
                    referrer_wallet.balance = F('balance') + 1000
                    referrer_wallet.save()

                except UserReferral.DoesNotExist:
                    messages.error(request, "Invalid referral code.")
            
            # Clear the OTP session
            del request.session['registration_otp']
            del request.session['registered_email']
            del request.session['otp_secret_key']
            del request.session['otp_valid_date']
            del request.session['referral_code']
            
            # Clearing the otp_verification_allowed 
            del request.session['otp_verification_allowed']

            messages.success(request, "Your email has been verified! You can now log in.")
            return redirect('authentication_app:login')

        except CustomUser.DoesNotExist:
            
            messages.error(request, "Invalid user. Please try again.")
            return redirect('authentication_app:sign_up')
    else:
        expiry_time = now() + timedelta(minutes=3)
        context = {'expiry_time': expiry_time}
        return render(request, 'authentication_app/verify_otp.html',context)
    
    
import hashlib

def generate_referral_code(user_id, salt="my_secret_salt"):
    hash_input = f"{user_id}{salt}".encode()
    code = hashlib.md5(hash_input).hexdigest()[:6].upper()  # Take first 8 characters
    return code


@never_cache
def resend_otp_view(request):
    if request.user.is_authenticated:
        return redirect('user_app:home')
    
    if request.method == 'POST':
        
        # Generating OTP
        otp = send_otp(request)
        
        # Save the OTP to session
        request.session['registration_otp'] = otp
        email = request.session['registered_email']
        
        if not email:
            messages.error(request, 'Session expired. Please register again.')
            return redirect('authentication_app:sign_up')

        # Send the OTP via email
        mail_subject = 'Your OTP for email verification'
        message = f'Your OTP is {otp}. Please enter it to verify your email.'
        try:
            email_message = EmailMessage(mail_subject, message, to=[email])
            email_message.send()
            messages.success(request, 'A new OTP has been sent to your email.')
        except Exception as e:
            messages.error(request, 'Error sending email. Please try again.')
            return redirect('authentication_app:verify_otp')

        print('redirecting to the verify OTP page')
        return redirect('authentication_app:verify_otp')  # Redirect to OTP verification page

    else:
        return render(request, 'authentication_app/verify_otp.html')

@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect('user_app:home')
    
    if 'account_blocked' in request.session:  # Check for blocked account
        messages.error(request, "Your account is blocked by the admin. Please contact support.")
        del request.session['account_blocked']  # Clear session after displaying the message

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        try:
            # Check if the user exists
            user = CustomUser.objects.get(email=email)

            # Check if the user is blocked
            if user.is_block:
                messages.error(request, "Your account is blocked by the admin. Please contact support.")
                return render(request, 'authentication_app/login.html', {'email': email})

            # Check if the user is signed in via Google
            if SocialAccount.objects.filter(user=user, provider='google').exists():
                # If a Google user tries to log in using email/password
                if password:
                    messages.error(request, "Your account is linked to Google. Please sign in using Google.")
                    return render(request, 'authentication_app/login.html', {'email': email})

            # Check if the user is inactive
            if not user.is_active:
                messages.error(request, "You need to verify your email using OTP.")
                return redirect('authentication_app:sign_up')

        except CustomUser.DoesNotExist:
            # If the email does not match any user
            messages.error(request, "The email you entered does not exist!")
            return render(request, 'authentication_app/login.html', {'email': email})

        # Authenticate the user using email/password
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Log in the user
            login(request, user)
            if remember_me:
                request.session.set_expiry(1209600)  # 2 weeks
            else:
                request.session.set_expiry(0)  # Session expires when the browser is closed

            # Redirect based on user role
            if user.is_staff:
                return redirect('admin_app:admin_home')
            else:
                return redirect('user_app:home')
        else:
            # If authentication fails
            messages.error(request, "Email or Password is incorrect!")
            return render(request, 'authentication_app/login.html', {'email': email})
    else:
        return render(request, 'authentication_app/login.html')
    

def social_login_error_view(request, exception):
    messages.error(request, "An error occurred while attempting to login via your third-party account.")
    return redirect('authentication_app:login')


def logout_view(request):
    logout(request)
    
    return redirect('authentication_app:login')

# Forgot password starts

def forgot_password_view(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')
        request.session['reset_pass_email'] = email
        # Check the email is already exists in the database or not
        if CustomUser.objects.filter(email = email).exists():
            # Generating OTP
            otp = send_otp(request)
            
            # Save the OTP to session
            request.session['registration_otp'] = otp
            
            # Send the OTP via email
            mail_subject = 'Your OTP for email verification'
            message = f'Your OTP is {otp}. Please enter it to verify your email.'
            try:
                email_message = EmailMessage(mail_subject, message, to=[email])
                email_message.send()
                messages.success(request, 'A new OTP has been sent to your email.')
            except Exception as e:
                messages.error(request, 'Error sending email. Please try again.')
                return redirect('authentication_app:forgot_password')
            
            # setting the token to access the verify_otp_reset_password page
            request.session['verify_otp_reset_password_token'] = True
            
            # Redirecting to the OTP page
            return redirect('authentication_app:reset_password_otp')
        
        else:
            messages.error(request, 'Email does not exists!')
        
    return render(request,'authentication_app/forgot_pass_email_form.html')
    
    

def verify_otp_reset_password(request):
    # checking the token to the entry
    if not request.session.get('verify_otp_reset_password_token'):
        return redirect('authentication_app:forgot_password')
    
    if request.method == 'POST':
        
        # combining all the otp
        input_otp_values = [request.POST.get(f'otp{i}') for i in range(1,7)]
        input_otp = ''.join([otp if otp is not None else '' for otp in input_otp_values])
        
        # Retrieving session data
        session_otp = request.session.get('registration_otp')
        email = request.session.get('reset_pass_email')
        otp_secret_key = request.session['otp_secret_key']
        otp_valid_until = request.session['otp_valid_date']
        
        
        
        # Ensure all necessary session data exists
        if not all([session_otp,email,otp_secret_key,otp_valid_until]):
            messages.error(request,'Session expired or invalid. Please register again.')
            return redirect('authentication_app:forgot_password')
        
        valid_until = datetime.fromisoformat(otp_valid_until)
            
        # Checking the OTP is still valid
        if valid_until <= datetime.now():
            messages.error(request,'OTP has been expired. Please request a new one.')
            return redirect('authentication_app:forgot_password')
        
        # Verify OTP
        try:
            totp = pyotp.TOTP(otp_secret_key, interval=180)
            
            if not totp.verify(input_otp):
                messages.error(request, 'Invalid OTP. Please try again.')
                return redirect('authentication_app:reset_password_otp')
            
            
            # Clear the OTP session
            del request.session['registration_otp']
            
            del request.session['otp_secret_key']
            del request.session['otp_valid_date']
            
            # Clearing the verify_otp_reset_password token
            del request.session['verify_otp_reset_password_token']

            messages.success(request, "Change your password")
            return redirect('authentication_app:reset_password')

        except CustomUser.DoesNotExist:
            
            messages.error(request, "Invalid user. Please try again.")
            return redirect('authentication_app:forgot_password')
    else:
        expiry_time = now() + timedelta(minutes=3)
        context = {'expiry_time': expiry_time}
        return render(request,'authentication_app/verify_otp_reset_pass.html',context)


def reset_pass_resend_otp(request):
    if request.method == 'POST':
        
        # Generating OTP
        otp = send_otp(request)
        
        # Save the OTP to session
        request.session['registration_otp'] = otp
        email = request.session['reset_pass_email']
        
        if not email:
            messages.error(request, 'Session expired. Please register again.')
            return redirect('authentication_app:forgot_password')

        # Send the OTP via email
        mail_subject = 'Your OTP for email verification'
        message = f'Your OTP is {otp}. Please enter it to verify your email.'
        try:
            email_message = EmailMessage(mail_subject, message, to=[email])
            email_message.send()
            messages.success(request, 'A new OTP has been sent to your email.')
        except Exception as e:
            messages.error(request, 'Error sending email. Please try again.')
            return redirect('authentication_app:forgot_password')

        
        return redirect('authentication_app:reset_password_otp')  # Redirect to OTP verification page

    else:
        return render(request, 'authentication_app/verify_otp_reset_pass.html')


def reset_password_view(request):
    errors = {}
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # validating the password by Authentication_check class methods
        pass_auth = Authentication_check()
        
        #password validation
        password_valid = pass_auth.pass_validator(password)
        if password_valid:
            errors['password_error'] = password_valid
        
        #password mismatch checking
        password_mismatch = pass_auth.password_mismatch(password, confirm_password)
        if password_mismatch:
            errors['password_mismatch'] = password_mismatch

        if not errors:
            email = request.session['reset_pass_email']
            user = CustomUser.objects.get(email = email)
            user.set_password(password)
            user.save()
            
            del request.session['reset_pass_email']
            
            messages.success(request,'Password changed successfully')
            return redirect('authentication_app:login')
        return render(request,'authentication_app/reset_password_form.html',{'errors': errors})
    else:
        return render(request,'authentication_app/reset_password_form.html')

