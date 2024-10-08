from django.shortcuts import render,redirect
from django.contrib.auth import get_user_model
from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth import login,authenticate,logout
from .models import CustomUser
from .validators import Authentication_check

User = get_user_model()


def register_view(request):
    errors = {}
    if request.method == 'POST':
        form = UserRegisterForm(request.POST or None)
        if form.is_valid():
            new_user_exist = CustomUser.objects.filter(email = form.cleaned_data.get('email')).exists()
            if not new_user_exist :
                #created object for user validation Authentication_check
                user_validation = Authentication_check()
                
                email = form.cleaned_data.get('email')
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password1 = form.cleaned_data.get('password1')
                password2 = form.cleaned_data.get('password2')
                
                #email validation
                email_valid = user_validation.email_validator(email)
                if email_valid:
                    errors['email'] = email_valid
                    
                #first_name validation
                first_name_valid = user_validation.first_name_validator(first_name)
                if first_name_valid:
                    errors['first_name'] = first_name_valid
                
                #last_name validation
                last_name_valid = user_validation.last_name_validator(last_name)
                if last_name_valid:
                    errors['last_name'] = last_name_valid
                    
                #password validation
                password_valid = user_validation.pass_validator(password1)
                if password_valid:
                    errors['password'] = password_valid
                
                #password mismatch checking
                password_mismatch = user_validation.password_mismatch(password1, password2)
                if password_mismatch:
                    errors['password_mismatch'] = password_mismatch
                
                if not errors:
                    new_user = form.save()
                    messages.success(request, f'Hey {first_name}, Your account has been created.')
                    return redirect('login')
            else:
                messages.error(request,'email already exists!')
        else:
            messages.error(request,'Please correct the errors below. ')
    else:
        form = UserRegisterForm()
    context = {
        'form' : form, 'errors': errors
    }
    return render(request,'authentication_app/sign_up.html',context)

def login_view(request):
    # new_user = authenticate(
        #     username = form.cleaned_data.get('email')
        #     , password = form.cleaned_data.get('password1')
        # )
    # login(request, new_user)
    return render(request,'authentication_app/login.html')