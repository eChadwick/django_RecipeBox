from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseNotFound
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from recipe_app.models import Ingredient, Recipe, RecipeIngredient
from recipe_app.forms import RecipeForm, IngredientFormSet

DEFAULT_PAGINATION = 25

RECIPE_NOT_FOUND_ERROR = 'Recipe not found'


def index(request):
    return HttpResponse("Recipe Index Page!!!")


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


def validate_recipe_form_data(request):
    recipe_data = {
        'name': request.POST['name'],
        'directions': request.POST['directions']
    }
    recipe_form = RecipeForm(recipe_data)
    recipe_form.is_valid()

    ingredients_data = {
        k: v for (k, v) in request.POST.items() if 'form-' in k}
    ingredients_formset = IngredientFormSet(ingredients_data)
    ingredients_formset.is_valid()

    if not recipe_form.data['directions'] and ingredients_formset.is_empty():
        recipe_form.add_error('name', RecipeForm.content_error)

    return recipe_form, ingredients_formset


def recipe_create(request):
    if ('POST' == request.method):
        recipe_form, ingredients_formset = validate_recipe_form_data(request)

        if (not recipe_form.is_valid() or not ingredients_formset.is_valid()):
            context = {'recipe': recipe_form,
                       'ingredients_list': ingredients_formset}
            return render(request, 'recipe_app/recipe_form.html', context)

        recipe_model = Recipe(
            name=recipe_form.cleaned_data['name'],
            directions=recipe_form.cleaned_data['directions']
        )
        recipe_model.save()

        for form in ingredients_formset.cleaned_data:
            if 'DELETE' not in form and 'name' in form:
                temp_ingredient = Ingredient(name=form['name'])
                temp_ingredient.save()

                RecipeIngredient(
                    recipe=recipe_model,
                    ingredient=temp_ingredient,
                    measurement=form['measurement']
                ).save()

        return redirect(reverse('recipe-detail', args=[recipe_model.pk]))
    else:
        context = {
            'recipe': RecipeForm(),
            'ingredients_list': IngredientFormSet(),
            'action': 'create'
        }
        return render(request, 'recipe_app/recipe_form.html', context)


def recipe_update(request, pk):
    if 'POST' == request.method:
        recipe_form, ingredients_formset = validate_recipe_form_data(request)

        if (not recipe_form.is_valid() or not ingredients_formset.is_valid()):
            context = {'recipe': recipe_form,
                       'ingredients_list': ingredients_formset}
            return render(request, 'recipe_app/recipe_form.html', context)

        recipe_model = Recipe.objects.filter(pk=pk)

        if not recipe_model.exists():
            return HttpResponseNotFound(RECIPE_NOT_FOUND_ERROR)

        recipe_model.update(
            name=recipe_form.cleaned_data['name'],
            directions=recipe_form.cleaned_data['directions']
        )

        for ri in RecipeIngredient.objects.filter(recipe=pk).all():
            ri.delete()

        for entry in ingredients_formset.cleaned_data:
            ingredient = Ingredient.objects.get_or_create(name=entry['name'])
            if not entry['DELETE']:
                RecipeIngredient.objects.create(
                    recipe=recipe_model[0],
                    ingredient=ingredient[0],
                    measurement=entry['measurement']
                )

        return redirect(reverse('recipe-detail', args=[pk]))

    else:
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe_form = RecipeForm({
            'name': recipe.name,
            'directions': recipe.directions
        })

        ingredients_list_data = {}
        form_count = 0
        for i, ri in zip(recipe.ingredients.all(), recipe.recipeingredient_set.all()):
            ingredients_list_data[f'form-{form_count}-name'] = i.name
            ingredients_list_data[f'form-{form_count}-measurement'] = ri.measurement
            form_count += 1
        ingredients_list_data['form-TOTAL_FORMS'] = str(form_count)
        ingredients_list_data['form-INITIAL_FORMS'] = str(form_count)

        ingredients_formset = IngredientFormSet(ingredients_list_data)
        context = {
            'recipe': recipe_form,
            'ingredients_list': ingredients_formset,
            'action': 'update',
            'recipe_pk': recipe.pk
        }
        return render(request, 'recipe_app/recipe_form.html', context)
