from django.db import models

# Create your models here.
class Offer(models.Model):
    offer_title = models.CharField(max_length=255)
    offer_description = models.TextField()
    offer_percentage = models.IntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()