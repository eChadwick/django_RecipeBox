from django.shortcuts import render
from django.http import HttpResponse

from recipe_app.models import Ingredient

# Create your views here.

def index(request):
    return HttpResponse("Recipe Index Page!!!")

def ingredient_list(request):
    ingredients_list = list(Ingredient.objects.all())
    context = {
        'ingredients_list': ingredients_list
    }
    return render(request,'recipe_app/ingredient_list.html', context)
