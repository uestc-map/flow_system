from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
def index(request):
    # return render(request, 'home/index.html')
    return render(request, 'home_new/index.html')