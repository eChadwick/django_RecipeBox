from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponse

from recipe_app.models import Ingredient

DEFAULT_PAGINATION = 25


def index(request):
    return HttpResponse("Recipe Index Page!!!")


def ingredient_list(request):
    ingredients_list = list(Ingredient.objects.all())
    paginator = Paginator(ingredients_list, DEFAULT_PAGINATION)
    context = {
        'ingredients_list': ingredients_list,
        'num_pages': paginator.num_pages
    }
    return render(request, 'recipe_app/ingredient_list.html', context)
