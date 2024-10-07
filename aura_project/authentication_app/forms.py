from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class UserRegisterForm(UserCreationForm):
    # username = forms.CharField(widget=forms.TextInput(attrs={"placeholder":'Username'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control','placeholder':'Email'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'First name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Last name'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Confirm Password'}))
    
    class Meta:
        model = CustomUser
        fields = ['email','first_name','last_name']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
        }