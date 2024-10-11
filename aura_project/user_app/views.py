from django.shortcuts import render,redirect


def home(request):
    name = request.session.get('name','Guest')
    return render(request,'user_app/index.html',{'name':name})