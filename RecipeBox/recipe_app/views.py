from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from recipe_app.models import Ingredient, Recipe
from recipe_app.forms import RecipeForm, IngredientFormSet

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
        'current_page': page_num or 1,
        'num_pages': num_pages,
        'pagination': pagination
    })


@require_http_methods(['POST'])
def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    recipe.delete()
    return redirect(reverse('recipe-list'))


def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    recipe_ingredients = recipe.ingredients.through.objects.filter(
        recipe=recipe).all()
    ingredients_list = [{'name': ri.ingredient.name,
                         'measurement': ri.measurement} for ri in recipe_ingredients]
    context = {'recipe': recipe, 'ingredients_list': ingredients_list}
    return render(request, 'recipe_app/recipe_detail.html', context)

def recipe_create(request):
    if('POST' == request.method):
        recipe = RecipeForm(request.POST)
        ingredients = IngredientFormSet(request.POST)
        if(not recipe.is_valid() or not ingredients.is_valid()):
            context = {'recipe': recipe, 'ingredients': ingredients}
            return render(request, 'recipe_app/recipe_form.html', context)

    else:
        context = {'recipe': RecipeForm(), 'ingredients': IngredientFormSet()}
        return render(request, 'recipe_app/recipe_form.html', context)