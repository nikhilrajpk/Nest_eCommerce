from django.shortcuts import render,redirect
from django.contrib.auth import get_user_model
from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth import login,authenticate,logout
from .models import CustomUser
User = get_user_model()


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST or None)
        print('inside')
        if form.is_valid():
            new_user_exist = CustomUser.objects.filter(email = form.cleaned_data.get('email')).exists()
            print(new_user_exist)
            if not new_user_exist :
                new_user = form.save()
                first_name = form.cleaned_data.get('first_name')
                messages.success(request, f'Hey {first_name}, Your account has been created.')
                return redirect(login_view)
            else:
                messages.error(request,'email already exists!')
        else:
            messages.error(request,'Please correct the errors below. ')
    else:
        form = UserRegisterForm()
    context = {
        'form' : form
    }
    return render(request,'authentication_app/sign_up.html',context)

def login_view(request):
    # new_user = authenticate(
        #     username = form.cleaned_data.get('email')
        #     , password = form.cleaned_data.get('password1')
        # )
    # login(request, new_user)
    return render(request,'authentication_app/login.html')