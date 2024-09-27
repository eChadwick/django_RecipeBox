import math

from unittest.mock import patch, ANY

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.test import TestCase, Client
from django.urls import reverse

from recipe_app.forms import (
    IngredientFormSet,
    IngredientInclusionFormSet,
    RecipeForm,
    RecipeInclusionForm,
    TagCreationFormset,
    TagSelectionFormset
)
from recipe_app.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag
)
from recipe_app.views import (
    RECIPE_NOT_FOUND_ERROR,
    TAG_CREATE_FORMSET_PREFIX,
    TAG_SELECT_FORMSET_PREFIX,
    INGREDIENT_LIST_FORMSET_PREFIX
)


@patch('recipe_app.views.render', return_value=HttpResponse())
class RecipeUpdateViewTests(TestCase):

    def setUp(self):
        self.ingredient = Ingredient.objects.create(name='Test Ingredient')

        self.recipe = Recipe.objects.create(
            name='Test Recipe',
            directions='Test Directions'
        )
        self.recipe_ingredient = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient,
            measurement='a bunch'
        )

    def test_get_renders_the_correct_html(self, mock_render):
        self.client.get(reverse('recipe-update', args=[self.recipe.pk]))
        mock_render.assert_called_with(
            ANY, 'recipe_app/recipe_form.html', ANY
        )

    def test_get_passes_request_action(self, mock_render):
        self.client.get(reverse('recipe-update', args=[self.recipe.pk]))
        rendered_context = mock_render.call_args[0][2]
        self.assertEqual(rendered_context['action'], 'update')

    def test_get_passes_recipe_pk(self, mock_render):
        self.client.get(reverse('recipe-update', args=[self.recipe.pk]))
        rendered_context = mock_render.call_args[0][2]
        self.assertEqual(rendered_context['recipe_pk'], self.recipe.pk)

    def test_get_fetches_right_form(self, mock_render):
        self.client.get(reverse('recipe-update', args=[self.recipe.pk]))

        rendered_recipe = mock_render.call_args[0][2]['recipe']
        self.assertEqual(
            rendered_recipe.data,
            {'name': self.recipe.name, 'directions': self.recipe.directions}
        )

        rendered_ingredients_list = mock_render.call_args[0][2]['ingredients_list']
        self.assertIsInstance(rendered_ingredients_list, IngredientFormSet)
        self.assertEqual(
            rendered_ingredients_list.data,
            {
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '1',
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': self.ingredient.name,
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': self.recipe_ingredient.measurement
            }
        )

    def test_post_should_rerender_form_on_recipe_errors(self, mock_render):
        # Empty recipe name is error
        form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': 'Ingredient',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': 'Amount',
            'directions': 'Do things'
        }
        self.client.post(
            reverse('recipe-update', args=[self.recipe.pk]), form_data)

        rendered_template = mock_render.call_args[0][1]
        self.assertEqual(rendered_template, 'recipe_app/recipe_form.html')

        rendered_recipe = mock_render.call_args[0][2]['recipe']
        self.assertEqual(
            rendered_recipe.data,
            {'name': form_data['name'], 'directions': form_data['directions']}
        )

        rendered_ingredients = mock_render.call_args[0][2]['ingredients_list']
        self.assertEqual(
            rendered_ingredients.data,
            {
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement']
            }
        )

    def test_post_should_rerender_form_on_ingredient_errors(self, mock_render):
        form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': 'Recipe Name',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': 'Amount',
            'directions': 'Do things'
        }
        self.client.post(
            reverse('recipe-update', args=[self.recipe.pk]), form_data)

        rendered_template = mock_render.call_args[0][1]
        self.assertEqual(rendered_template, 'recipe_app/recipe_form.html')

        rendered_recipe = mock_render.call_args[0][2]['recipe']
        self.assertEqual(
            rendered_recipe.data,
            {'name': form_data['name'], 'directions': form_data['directions']}
        )

        rendered_ingredients = mock_render.call_args[0][2]['ingredients_list']
        self.assertEqual(
            rendered_ingredients.data,
            {
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement']
            }
        )

    def test_recipe_form_has_error_when_no_directions_or_ingredients(self, mock_render):
        form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': 'Test Recipe',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '2',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': 'Test Ingredient',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': 'a bunch',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-DELETE': 'on',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-name': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-measurement': '',
            'directions': ''
        }

        self.client.post(
            reverse('recipe-update', args=[self.recipe.pk]), form_data)

        rendered_template = mock_render.call_args[0][1]
        self.assertEqual(rendered_template, 'recipe_app/recipe_form.html')

        rendered_recipe = mock_render.call_args[0][2]['recipe']
        self.assertEqual(
            rendered_recipe.data,
            {'name': form_data['name'], 'directions': form_data['directions']}
        )
        self.assertIn(RecipeForm.content_error, rendered_recipe.errors['name'])

        rendered_ingredients = mock_render.call_args[0][2]['ingredients_list']
        self.assertEqual(
            rendered_ingredients.data,
            {
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-DELETE': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-DELETE'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-name': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-name'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-measurement': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-measurement']
            }
        )

    def test_post_should_404_on_recipe_not_found(self, _):
        updated_form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': 'new name',
            'directions': 'new directions',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '2',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '2',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': self.ingredient.name,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': 'updated measurement',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-2-name': 'new ingredient name',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-2-measurement': 'new ingredient measurement'
        }

        response = self.client.post(
            reverse('recipe-update', args=[self.recipe.pk + 1]),
            updated_form_data
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content.decode(), RECIPE_NOT_FOUND_ERROR)

    @patch('recipe_app.views.redirect', wraps=redirect)
    def test_success_updates_recipe_name_and_directions(self, mock_redirect, _):
        updated_form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': 'New Recipe Name',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': 'Test Ingredient',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': 'a bunch',
            'directions': 'New Directions'
        }

        self.client.post(
            reverse('recipe-update', args=[self.recipe.pk]), updated_form_data
        )
        self.recipe = Recipe.objects.get(pk=self.recipe.pk)

        self.assertEqual(self.recipe.name, updated_form_data['name'])
        self.assertEqual(self.recipe.directions,
                         updated_form_data['directions'])

        self.assertTrue(
            Ingredient.objects.filter(pk=self.ingredient.pk).exists()
        )

        self.assertEqual(
            RecipeIngredient.objects.filter(
                recipe=self.recipe.pk,
                ingredient=self.recipe_ingredient.ingredient.pk,
                measurement=updated_form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement']
            ).count(),
            1
        )

        mock_redirect.assert_called_with(
            reverse('recipe-detail', args=[self.recipe.pk]))

    @patch('recipe_app.views.redirect', wraps=redirect)
    def test_success_adds_ingredient(self, mock_redirect, _):
        updated_form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': 'Test Recipe',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '2',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': 'Test Ingredient',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': 'a bunch',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-name': 'New Ingredient',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-measurement': 'new amount',
            'directions': 'Test Directions'
        }

        self.client.post(
            reverse('recipe-update', args=[self.recipe.pk]), updated_form_data
        )
        self.recipe = Recipe.objects.get(pk=self.recipe.pk)

        self.assertTrue(
            Ingredient.objects.filter(pk=self.ingredient.pk).exists()
        )

        self.assertEqual(
            RecipeIngredient.objects.filter(
                recipe=self.recipe.pk,
                ingredient=self.recipe_ingredient.ingredient.pk,
                measurement=updated_form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement']
            ).count(),
            1
        )

        new_ingredient = Ingredient.objects.filter(
            name=updated_form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-name'])
        self.assertTrue(new_ingredient.exists())

        self.assertEqual(
            RecipeIngredient.objects.filter(
                recipe=self.recipe.pk,
                ingredient=new_ingredient[0].pk,
                measurement=updated_form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-measurement']
            ).count(),
            1
        )

        mock_redirect.assert_called_with(
            reverse('recipe-detail', args=[self.recipe.pk]))

    @patch('recipe_app.views.redirect', wraps=redirect)
    def test_success_deletes_ingredient(self, mock_redirect, _):
        updated_form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': 'Test Recipe',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': 'Test Ingredient',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': 'a bunch',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-DELETE': 'on',
            'directions': 'Test Directions'
        }

        self.client.post(
            reverse('recipe-update', args=[self.recipe.pk]), updated_form_data
        )
        self.recipe = Recipe.objects.get(pk=self.recipe.pk)

        self.assertTrue(
            Ingredient.objects.filter(pk=self.ingredient.pk).exists()
        )

        self.assertEqual(
            RecipeIngredient.objects.filter(
                recipe=self.recipe.pk,
            ).count(),
            0
        )

        mock_redirect.assert_called_with(
            reverse('recipe-detail', args=[self.recipe.pk]))

    @patch('recipe_app.views.redirect', wraps=redirect)
    def test_success_updates_ingredient(self, mock_redirect, _):
        updated_form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': 'Test Recipe',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': 'Test Ingredient',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': 'a bit',
            'directions': 'Test Directions'
        }

        self.client.post(
            reverse('recipe-update', args=[self.recipe.pk]), updated_form_data
        )
        self.recipe = Recipe.objects.get(pk=self.recipe.pk)

        self.assertTrue(
            Ingredient.objects.filter(pk=self.ingredient.pk).exists()
        )

        self.assertEqual(
            RecipeIngredient.objects.filter(
                recipe=self.recipe.pk,
                ingredient=self.recipe_ingredient.ingredient.pk,
                measurement=updated_form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement']
            ).count(),
            1
        )

        mock_redirect.assert_called_with(
            reverse('recipe-detail', args=[self.recipe.pk]))


@patch('recipe_app.views.render', return_value=HttpResponse())
class RecipeSearchViewTests(TestCase):

    def setUp(self):
        for i in range(1, 6):
            Ingredient.objects.create(name=f'Ingredient {i}')

    def test_get_renders_correct_template(self, mock_render):
        self.client.get(reverse('recipe-search'))

        mock_render.assert_called_with(
            ANY, 'recipe_app/recipe_search.html', ANY
        )

    def test_get_returns_all_elements(self, mock_render):
        self.client.get(reverse('recipe-search'))

        ingredients_list = mock_render.call_args[0][2]['ingredients']
        self.assertIsInstance(ingredients_list, IngredientInclusionFormSet)
        self.assertEqual(len(ingredients_list), 5)
        for i in range(1, 6):
            self.assertIn(
                {
                    'id': i,
                    'name': f'Ingredient {i}'
                },
                ingredients_list.initial
            )

        recipe_name = mock_render.call_args[0][2]['recipe_name']
        self.assertIsInstance(recipe_name, RecipeInclusionForm)

    def test_post_renders_correct_template(self, mock_render):
        post_data = {
            'form-TOTAL_FORMS': '0',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'csrfmiddlewaretoken': 'irrelevant'
        }
        self.client.post(reverse('recipe-search'), post_data)

        mock_render.assert_called_with(
            ANY, 'recipe_app/recipe_list.html', ANY
        )

    def test_post_handles_neutral_inclusion(self, mock_render):
        recipe_no_ingredients = Recipe.objects.create(
            name='No ingredients', directions='things')

        ingredient = Ingredient.objects.create(name='Ingredient 1')
        recipe_with_ingredients = Recipe.objects.create(
            name='Yes ingredients', directions='stuff')
        RecipeIngredient.objects.create(
            recipe=recipe_with_ingredients,
            ingredient=ingredient
        )

        post_data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'csrfmiddlewaretoken': 'irrelevant',
            'form-0-name': ingredient.name,
            'form-0-inclusion': 'neutral',
            'form-0-id': ingredient.pk
        }
        self.client.post(reverse('recipe-search'), post_data)

        rendered_recipe_list = mock_render.call_args[0][2]['recipes_list']
        self.assertEqual(len(rendered_recipe_list), 2)
        self.assertIn(recipe_no_ingredients, rendered_recipe_list)
        self.assertIn(recipe_with_ingredients, rendered_recipe_list)

    def test_excludes(self, mock_render):
        exclude_ingredient_1 = Ingredient.objects.create(
            name='Exclude Ingredient 1')
        exclude_recipe_1 = Recipe.objects.create(name='Exclude Recipe 1')
        RecipeIngredient.objects.create(
            recipe=exclude_recipe_1,
            ingredient=exclude_ingredient_1
        )

        exclude_ingredient_2 = Ingredient.objects.create(
            name='Exclude Ingredient 2')
        exclude_recipe_2 = Recipe.objects.create(name='Exclude Recipe 2')
        RecipeIngredient.objects.create(
            recipe=exclude_recipe_2,
            ingredient=exclude_ingredient_2
        )

        neutral_ingredient = Ingredient.objects.create(
            name='Neutral Ingredient')
        neutral_recipe = Recipe.objects.create(name='Neutral Recipe')

        post_data = {
            'form-TOTAL_FORMS': '3',
            'form-INITIAL_FORMS': '3',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'csrfmiddlewaretoken': 'irrelevant',
            'form-0-name': exclude_ingredient_1.name,
            'form-0-inclusion': 'exclude',
            'form-0-id': exclude_ingredient_1.pk,
            'form-1-name': exclude_ingredient_2.name,
            'form-1-inclusion': 'exclude',
            'form-1-id': exclude_ingredient_2.pk,
            'form-2-name': neutral_ingredient.name,
            'form-2-inclusion': 'neutral',
            'form-2-id': neutral_ingredient.pk
        }

        self.client.post(reverse('recipe-search'), post_data)

        rendered_recipe_list = mock_render.call_args[0][2]['recipes_list']
        self.assertEqual(len(rendered_recipe_list), 1)
        self.assertIn(neutral_recipe, rendered_recipe_list)
        self.assertNotIn(exclude_recipe_1, rendered_recipe_list)
        self.assertNotIn(exclude_recipe_2, rendered_recipe_list)

    def test_or_includes(self, mock_render):
        ingredient_1 = Ingredient.objects.create(name='Ingredient 1')
        ingredient_2 = Ingredient.objects.create(name='Ingredient 2')

        include_recipe_1 = Recipe.objects.create(
            name='Include Recipe 1'
        )
        RecipeIngredient.objects.create(
            recipe=include_recipe_1,
            ingredient=ingredient_1
        )

        include_recipe_2 = Recipe.objects.create(
            name='Include Recipe 2'
        )
        RecipeIngredient.objects.create(
            recipe=include_recipe_2,
            ingredient=ingredient_2
        )

        exclude_recipe = Recipe.objects.create(
            name='Exclude Recipe'
        )

        post_data = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'csrfmiddlewaretoken': 'irrelevant',
            'form-0-name': ingredient_1.name,
            'form-0-inclusion': 'or',
            'form-0-id': ingredient_1.pk,
            'form-1-name': ingredient_2.name,
            'form-1-inclusion': 'or',
            'form-1-id': ingredient_2.pk
        }

        self.client.post(reverse('recipe-search'), post_data)

        rendered_recipe_list = mock_render.call_args[0][2]['recipes_list']
        self.assertEqual(len(rendered_recipe_list), 2)
        self.assertIn(include_recipe_1, rendered_recipe_list)
        self.assertIn(include_recipe_2, rendered_recipe_list)
        self.assertNotIn(exclude_recipe, rendered_recipe_list)

    def test_and_includes(self, mock_render):
        ingredient_1 = Ingredient.objects.create(name='Ingredient 1')
        ingredient_2 = Ingredient.objects.create(name='Ingredient 2')

        include_recipe = Recipe.objects.create(
            name='Include Recipe'
        )
        RecipeIngredient.objects.create(
            recipe=include_recipe,
            ingredient=ingredient_1
        )
        RecipeIngredient.objects.create(
            recipe=include_recipe,
            ingredient=ingredient_2
        )

        exclude_recipe_1 = Recipe.objects.create(
            name='Exclude Recipe 1'
        )
        RecipeIngredient.objects.create(
            recipe=exclude_recipe_1,
            ingredient=ingredient_1
        )

        exclude_recipe_2 = Recipe.objects.create(
            name='Exclude Recipe 2'
        )

        post_data = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'csrfmiddlewaretoken': 'irrelevant',
            'form-0-name': ingredient_1.name,
            'form-0-inclusion': 'and',
            'form-0-id': ingredient_1.pk,
            'form-1-name': ingredient_2.name,
            'form-1-inclusion': 'and',
            'form-1-id': ingredient_2.pk
        }

        self.client.post(reverse('recipe-search'), post_data)

        rendered_recipe_list = mock_render.call_args[0][2]['recipes_list']
        self.assertEqual(len(rendered_recipe_list), 1)
        self.assertIn(include_recipe, rendered_recipe_list)
        self.assertNotIn(exclude_recipe_1, rendered_recipe_list)
        self.assertNotIn(exclude_recipe_2, rendered_recipe_list)

    def test_recipe_name_handling(self, mock_render):
        include_recipe_1 = Recipe.objects.create(
            name='Chicken 1', directions='do stuff')
        include_recipe_2 = Recipe.objects.create(
            name='Chicken 2', directions='do other stuff')
        exclude_recipe = Recipe.objects.create(
            name='Beef', directions='dont do stuff')

        post_data = {
            'form-TOTAL_FORMS': '0',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'csrfmiddlewaretoken': 'irrelevant',
            'recipe_name': 'Chicken'
        }
        self.client.post(reverse('recipe-search'), post_data)

        rendered_recipe_list = mock_render.call_args[0][2]['recipes_list']
        self.assertEqual(len(rendered_recipe_list), 2)
        self.assertIn(include_recipe_1, rendered_recipe_list)
        self.assertIn(include_recipe_2, rendered_recipe_list)
        self.assertNotIn(exclude_recipe, rendered_recipe_list)

    def test_or_includes_are_distinct(self, mock_render):
        ingredient_1 = Ingredient.objects.create(name='Ingredient 1')
        ingredient_2 = Ingredient.objects.create(name='Ingredient 2')

        recipe = Recipe.objects.create(
            name='Recipe Name'
        )
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient_1
        )
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient_2
        )

        post_data = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'csrfmiddlewaretoken': 'irrelevant',
            'form-0-name': ingredient_1.name,
            'form-0-inclusion': 'or',
            'form-0-id': ingredient_1.pk,
            'form-1-name': ingredient_2.name,
            'form-1-inclusion': 'or',
            'form-1-id': ingredient_2.pk
        }

        self.client.post(reverse('recipe-search'), post_data)

        rendered_recipe_list = mock_render.call_args[0][2]['recipes_list']
        self.assertEqual(len(rendered_recipe_list), 1)
        self.assertIn(recipe, rendered_recipe_list)
