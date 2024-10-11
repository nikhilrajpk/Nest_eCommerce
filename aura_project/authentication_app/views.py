from django.shortcuts import render,redirect
from django.contrib.auth import get_user_model
# from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth import login,authenticate,logout
from .models import CustomUser
from .validators import Authentication_check

from .utils import send_otp
from django.core.mail import EmailMessage
from datetime import datetime
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
    
    if request.method == 'POST':
        email = request.POST.get('email')
        username = email
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        
        # validating the request data
        errors = validation_view(request,email,first_name,last_name,password,confirm_password)    
        
        if errors:
            context = {
                'errors' : errors,
                'email' : email,
                'first_name' : first_name,
                'last_name' : last_name,
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

                print('redirecting to the verify OTP page')
                return redirect('verify_otp')  # Redirect to OTP verification page
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

            print('redirecting to the verify OTP page')
            return redirect('verify_otp')  # Redirect to OTP verification page

    else:
        pass
    
    return render(request, 'authentication_app/sign_up.html')

def verify_otp(request):
    
    if request.method == 'POST':
        
        # combining all the otp
        input_otp_values = [request.POST.get(f'otp{i}') for i in range(1,7)]
        input_otp = ''.join([otp if otp is not None else '' for otp in input_otp_values])
        
        # Retrieving session data
        session_otp = request.session.get('registration_otp')
        session_email = request.session.get('registered_email')
        otp_secret_key = request.session['otp_secret_key']
        otp_valid_until = request.session['otp_valid_date']
        print(session_otp)
        print(session_email)
        print(otp_secret_key)
        print(otp_valid_until)
        
        
        # Ensure all necessary session data exists
        if not all([session_otp,session_email,otp_secret_key,otp_valid_until]):
            messages.error(request,'Session expired or invalid. Please register again.')
            return redirect('sign_up')
        
        valid_until = datetime.fromisoformat(otp_valid_until)
            
        # Checking the OTP is still valid
        if valid_until <= datetime.now():
            messages.error(request,'OTP has been expired. Please request a new one.')
            return redirect('sign_up')
        
        # Verify OTP
        try:
            totp = pyotp.TOTP(otp_secret_key, interval=180)
            
            if not totp.verify(input_otp):
                messages.error(request, 'Invalid OTP. Please try again.')
                return redirect('verify_otp')
            
            # Activate the user
            user = CustomUser.objects.get(email = session_email)
            user.is_active = True
            user.save()
            
            # Clear the OTP session
            del request.session['registration_otp']
            del request.session['registered_email']
            del request.session['otp_secret_key']
            del request.session['otp_valid_date']

            messages.success(request, "Your email has been verified! You can now log in.")
            return redirect('login')

        except CustomUser.DoesNotExist:
            
            messages.error(request, "Invalid user. Please try again.")
            return redirect('sign_up')
    else:
        return render(request, 'authentication_app/verify_otp.html')

def resend_otp_view(request):
    if request.method == 'POST':
        
        # Generating OTP
        otp = send_otp(request)
        
        # Save the OTP to session
        request.session['registration_otp'] = otp
        email = request.session['registered_email']
        
        if not email:
            messages.error(request, 'Session expired. Please register again.')
            return redirect('sign_up')

        # Send the OTP via email
        mail_subject = 'Your OTP for email verification'
        message = f'Your OTP is {otp}. Please enter it to verify your email.'
        try:
            email_message = EmailMessage(mail_subject, message, to=[email])
            email_message.send()
            messages.success(request, 'A new OTP has been sent to your email.')
        except Exception as e:
            messages.error(request, 'Error sending email. Please try again.')
            return redirect('verify_otp')

        print('redirecting to the verify OTP page')
        return redirect('verify_otp')  # Redirect to OTP verification page

    else:
        return render(request, 'authentication_app/verify_otp.html')


def login_view(request):
    # new_user = authenticate(
        #     username = form.cleaned_data.get('email')
        #     , password = form.cleaned_data.get('password1')
        # )
    # login(request, new_user)
    return render(request,'authentication_app/login.html')






# def register_view(request):
#     errors = {}
#     if request.method == 'POST':
        
#         form = UserRegisterForm(request.POST)
#         email = request.POST.get('email')  # Get email directly from POST data
        
#         # Check if the user already exists
#         if CustomUser.objects.filter(email=email).exists():
#             user_obj = CustomUser.objects.get(email=email)
#             print(user_obj, 'this is the user')
#             print(user_obj.is_active, 'User Active Status')  # Debugging print
            
#             if not user_obj.is_active:
#                 # Check if the form is valid before accessing `cleaned_data`
#                 if form.is_valid():
#                     errors = validation_otp_email(request, form)

#                     if not errors:
#                         # Generating OTP
#                         otp = send_otp(request)

#                         # Save the OTP to session
#                         request.session['registration_otp'] = otp
#                         request.session['registered_email'] = email

#                         # Send the OTP via email
#                         mail_subject = 'Your OTP for email verification'
#                         message = f'Your OTP is {otp}. Please enter it to verify your email.'
#                         try:
#                             email_message = EmailMessage(mail_subject, message, to=[email])
#                             email_message.send()
#                         except Exception as e:
#                             messages.error(request, 'Error sending email. Please try again.')
#                             return None

#                         print('redirecting to the verify OTP page')
#                         return redirect('verify_otp')  # Redirect to OTP verification page
                
#             else:
#                 messages.error(request, 'Email already exists!')

#         # If no user exists, validate the form and proceed
#         elif form.is_valid():
#             errors = validation_otp_email(request, form)
            
#             if not errors:
#                 print('Saving the user and sending the email')
#                 # Save the user but keep the account inactive until OTP verification
#                 new_user = form.save(commit=False)
#                 new_user.is_active = False
#                 new_user.save()

#                 # Generating OTP
#                 otp = send_otp(request)

#                 # Save the OTP to session
#                 request.session['registration_otp'] = otp
#                 request.session['registered_email'] = email

#                 # Send the OTP via email
#                 mail_subject = 'Your OTP for email verification'
#                 message = f'Your OTP is {otp}. Please enter it to verify your email.'
#                 try:
#                     email_message = EmailMessage(mail_subject, message, to=[email])
#                     email_message.send()
#                 except Exception as e:
#                     messages.error(request, 'Error sending email. Please try again.')
#                     return None

#                 print('redirecting to the verify OTP page')
#                 return redirect('verify_otp')  # Redirect to OTP verification page

#         else:
#             messages.error(request, 'Form is invalid. Please correct the errors below.')

#     else:
#         form = UserRegisterForm()
    
#     context = {
#         'form': form,
#         'errors': errors
#     }
    
#     return render(request, 'authentication_app/sign_up.html', context)




#created object for user validation Authentication_check
                # user_validation = Authentication_check()
                
                # email = form.cleaned_data.get('email')
                # username = form.cleaned_data.get('username')
                # first_name = form.cleaned_data.get('first_name')
                # last_name = form.cleaned_data.get('last_name')
                # password1 = form.cleaned_data.get('password1')
                # password2 = form.cleaned_data.get('password2')
                
                # #email validation
                # email_valid = user_validation.email_validator(email)
                # if email_valid:
                #     errors['email'] = email_valid
                    
                # #first_name validation
                # first_name_valid = user_validation.first_name_validator(first_name)
                # if first_name_valid:
                #     errors['first_name'] = first_name_valid
                
                # #last_name validation
                # last_name_valid = user_validation.last_name_validator(last_name)
                # if last_name_valid:
                #     errors['last_name'] = last_name_valid
                    
                # #password validation
                # password_valid = user_validation.pass_validator(password1)
                # if password_valid:
                #     errors['password'] = password_valid
                
                # #password mismatch checking
                # password_mismatch = user_validation.password_mismatch(password1, password2)
                # if password_mismatch:
                #     errors['password_mismatch'] = password_mismatch
                
                # if not errors:
                #     # Save the user but keep the account inactive until OTP verification
                #     new_user = form.save()  #commit=False
                #     new_user.is_active = False
                #     new_user.save()
                    
                #     # user_data = CustomUser.objects.get(email = email)
                    
                #     # Generating OTP
                #     otp = send_otp(request)
                    
                #     # Save the OTP to session
                #     request.session['registration_otp'] = otp
                #     request.session['registered_email'] = email
                #     # request.session['registered_user_id'] = user_data.id
                    
                #     # Send the OTP via email
                #     mail_subject = 'Your OTP for email verification'
                #     message = f'Your OTP is {otp}. Please enter it to verify your email.'
                #     try:
                #         email = EmailMessage(mail_subject, message, to=[email])
                #         email.send()
                #     except Exception as e:
                #         messages.error(request, 'Error sending email. Please try again.')

                    
                #     # messages.success(request, "Registration successful! Please check your email for the OTP.")
                #     return redirect('verify_otp')  # Redirect to OTP verification page
                    
                    
                #     # messages.success(request, f'Hey {first_name}, Your account has been created.')
                #     # return redirect('login')