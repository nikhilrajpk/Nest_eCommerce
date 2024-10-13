from django.shortcuts import render,redirect

def home(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    name = request.session.get('name','Guest')
    return render(request,'user_app/index.html',{'name':name})