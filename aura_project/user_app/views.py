from django.shortcuts import render,redirect


def home(request):
    return render(request,'user_app/index.html')