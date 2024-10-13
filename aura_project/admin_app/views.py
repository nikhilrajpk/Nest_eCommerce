from django.shortcuts import render,redirect
from authentication_app.models import CustomUser
from django.db.models import Q
# Create your views here.

def admin_home(request):
    if request.user.is_authenticated and request.user.is_staff: 
        return render(request,'admin_app/admin_home.html')
    else:
        return redirect('user_app:home')
    
def users(request):
    if request.user.is_authenticated and request.user.is_staff:
        query = request.GET.get('search_query')
        if query:
            users = CustomUser.objects.all().exclude(is_staff = True).filter(Q(first_name__icontains = query) | Q(email__icontains = query))
        else:
            users = CustomUser.objects.all().exclude(is_staff = True)
        return render(request,'admin_app/users.html',{'users':users,'query':query})
    
    else:
        return redirect('user_app:home')
    

def user_block(request,id):
    print('user_block')
    if request.method == 'POST':
        user = CustomUser.objects.get(id = id)
        print(user)
        if user.is_block:
            print(user.is_block)
            user.is_block = False
            user.save()
        elif not user.is_block:
            user.is_block = True
            user.save()
    return redirect('admin_app:users')