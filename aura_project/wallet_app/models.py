from django.db import models
from authentication_app.models import CustomUser
# Create your models here.
class Wallet(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    balance =  models.DecimalField(max_digits=10,decimal_places=2,default=0.00)

    def __str__(self):
        return f"{self.user.first_name}'s Wallet - Balance: {self.balance}"
    
class WalletTransation(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('refund', 'Refund'),
        ('cancellation', 'Cancellation'),
        ('debited', 'Debited'),
        
    ]

    wallet = models.ForeignKey(Wallet,on_delete=models.CASCADE,related_name='transactions')
    transaction_type = models.CharField(max_length=20,choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    created_at =  models.DateField(auto_now_add=True)


    def __str__(self):
        return f"{self.wallet.user.first_name} - {self.transaction_type} - {self.amount}"