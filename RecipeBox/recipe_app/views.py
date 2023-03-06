from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    return HttpResponse("Recipe Index Page!!!")

def ingredient_list(request):
    return HttpResponse('Ingredients List Page')