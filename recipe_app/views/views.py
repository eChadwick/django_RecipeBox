from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseNotFound
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from recipe_app.models import Ingredient, Recipe, RecipeIngredient, Tag
from recipe_app.forms.forms import (
    RecipeForm,
    IngredientFormSet,
    IngredientInclusionFormSet,
    RecipeInclusionForm,
    TagCreationFormset
)
from recipe_app.forms.tag_selection_formset import TagSelectionFormset

DEFAULT_PAGINATION = 25

RECIPE_NOT_FOUND_ERROR = 'Recipe not found'
TAG_CREATE_FORMSET_PREFIX = 'tag-create-form'
TAG_SELECT_FORMSET_PREFIX = 'tag-select-form'
INGREDIENT_LIST_FORMSET_PREFIX = 'ingredient-form'


def index(request):
    return HttpResponse("Recipe Index Page!!!")


def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    recipe_ingredients = recipe.ingredients.through.objects.filter(
        recipe=recipe).all()
    ingredients_list = [{'name': ri.ingredient.name,
                         'measurement': ri.measurement} for ri in recipe_ingredients]
    context = {'recipe': recipe, 'ingredients_list': ingredients_list}
    return render(request, 'recipe_app/recipe_detail.html', context)


def _validate_recipe_form_data(request):
    recipe_data = {
        'name': request.POST['name'],
        'directions': request.POST['directions']
    }
    recipe_form = RecipeForm(recipe_data)
    recipe_form.is_valid()

    ingredients_data = {
        k: v for (k, v) in request.POST.items() if INGREDIENT_LIST_FORMSET_PREFIX in k}
    ingredients_formset = IngredientFormSet(
        ingredients_data, prefix=INGREDIENT_LIST_FORMSET_PREFIX)
    ingredients_formset.is_valid()

    if not recipe_form.data['directions'] and ingredients_formset.is_empty():
        recipe_form.add_error('name', RecipeForm.content_error)

    tag_create_data = {
        k: v for (k, v) in request.POST.items() if TAG_CREATE_FORMSET_PREFIX in k}
    tag_create_formset = TagCreationFormset(
        tag_create_data, prefix=TAG_CREATE_FORMSET_PREFIX)

    tag_select_data = {
        k: v for (k, v) in request.POST.items() if TAG_SELECT_FORMSET_PREFIX in k}
    tag_select_formset = TagCreationFormset(
        tag_select_data, prefix=TAG_SELECT_FORMSET_PREFIX)

    return recipe_form, ingredients_formset, tag_create_formset, tag_select_formset


def recipe_create(request):
    if ('POST' == request.method):
        (recipe_form,
            ingredients_formset,
            tag_create_formset,
            tag_select_formset
         ) = _validate_recipe_form_data(request)

        if (not recipe_form.is_valid() or not ingredients_formset.is_valid()):
            context = {'recipe': recipe_form,
                       'ingredients_list': ingredients_formset,
                       'tag_create': tag_create_formset,
                       'tag_select': tag_select_formset
                       }
            return render(request, 'recipe_app/recipe_form.html', context)

        recipe_model = Recipe(
            name=recipe_form.cleaned_data['name'],
            directions=recipe_form.cleaned_data['directions']
        )
        recipe_model.save()

        for form in ingredients_formset.cleaned_data:
            if not form.get('DELETE') and 'name' in form:
                temp_ingredient = Ingredient(name=form['name'])
                temp_ingredient.save()

                RecipeIngredient(
                    recipe=recipe_model,
                    ingredient=temp_ingredient,
                    measurement=form['measurement']
                ).save()

        if tag_create_formset.is_valid():
            for form in tag_create_formset.cleaned_data:
                recipe_model.tags.create(name=form['tag_name'])

        return redirect(reverse('recipe-detail', args=[recipe_model.pk]))
    else:
        context = {
            'recipe': RecipeForm(),
            'ingredients_list': IngredientFormSet(prefix=INGREDIENT_LIST_FORMSET_PREFIX),
            'tag_create': TagCreationFormset(prefix=TAG_CREATE_FORMSET_PREFIX),
            'tag_select': TagSelectionFormset(prefix=TAG_SELECT_FORMSET_PREFIX),
            'action': 'create'
        }
        return render(request, 'recipe_app/recipe_form.html', context)


def recipe_update(request, pk):
    if 'POST' == request.method:
        recipe_form, ingredients_formset, _, _ = _validate_recipe_form_data(
            request)

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
            ingredients_list_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-{form_count}-name'] = i.name
            ingredients_list_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-{form_count}-measurement'] = ri.measurement
            form_count += 1
        ingredients_list_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS'] = str(
            form_count)
        ingredients_list_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS'] = str(
            form_count)

        ingredients_formset = IngredientFormSet(ingredients_list_data)
        context = {
            'recipe': recipe_form,
            'ingredients_list': ingredients_formset,
            'action': 'update',
            'recipe_pk': recipe.pk
        }
        return render(request, 'recipe_app/recipe_form.html', context)


def recipe_search(request):
    if 'POST' == request.method:
        inclusion_forms = IngredientInclusionFormSet(request.POST)
        exclude_ids = [
            i['id'] for i in inclusion_forms.cleaned_data if i['inclusion'] == 'exclude'
        ]
        or_ids = [
            i['id'] for i in inclusion_forms.cleaned_data if i['inclusion'] == 'or'
        ]
        and_ids = [
            i['id'] for i in inclusion_forms.cleaned_data if i['inclusion'] == 'and'
        ]

        recipe_matches = Recipe.objects.exclude(
            ingredients__id__in=exclude_ids)
        if or_ids:
            recipe_matches = recipe_matches.filter(ingredients__id__in=or_ids)
        if '' != request.POST.dict().get('recipe_name', ''):
            recipe_matches = recipe_matches.filter(
                name__contains=request.POST.dict()['recipe_name'])
        if and_ids:
            for id in and_ids:
                recipe_matches = recipe_matches.filter(ingredients__id=id)

        context = {'recipes_list': recipe_matches.distinct()}
        return render(request, 'recipe_app/recipe_list.html', context)
    else:
        all_ingredients = list(Ingredient.objects.all().values())

        context = {
            'ingredients': IngredientInclusionFormSet(initial=all_ingredients),
            'recipe_name': RecipeInclusionForm()
        }
        return render(request, 'recipe_app/recipe_search.html', context)
