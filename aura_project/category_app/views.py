from django.shortcuts import render

# Create your views here.

def category_view(request):
    return render(request,'category_app/category.html')