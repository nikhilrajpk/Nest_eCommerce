from django.shortcuts import render,redirect
from wallet_app.models import *
# Create your views here.

def wallet(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    
    wallet,created = Wallet.objects.get_or_create(user=request.user)
    # wallet = Wallet.objects.get(user = request.user)
    wallet_transactions = wallet.transactions.all().order_by('-id')
    
    context = {
        'wallet':wallet,
        'wallet_transactions':wallet_transactions,
    }
    return render(request,'wallet_app/wallet.html',context)