from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponse

from recipe_app.models import Ingredient, Recipe

DEFAULT_PAGINATION = 25


def index(request):
    return HttpResponse("Recipe Index Page!!!")


def ingredient_list(request):
    ingredients_list = list(Ingredient.objects.all())
    request_pagination = request.GET.get('pagination')
    paginator = Paginator(
        ingredients_list,
        request_pagination if request_pagination != None else DEFAULT_PAGINATION
    )
    requested_page = request.GET.get('page')
    context = {
        'ingredients_list': paginator.get_page(requested_page),
        'num_pages': paginator.num_pages
    }
    return render(request, 'recipe_app/ingredient_list.html', context)


def recipe_list(request):
    pagination = request.GET.get('pagination', DEFAULT_PAGINATION)
    all_recipes = Recipe.objects.all().order_by('name')
    paginator = Paginator(all_recipes, pagination)
    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)
    num_pages = paginator.num_pages

    return render(request, 'recipe_app/recipe_list.html', {
        'recipes_list': page_obj,
        'num_pages': num_pages,
        'pagination': pagination
    })

