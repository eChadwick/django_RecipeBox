from unittest.mock import patch, ANY

from django.http import HttpResponse
from django.shortcuts import redirect
from django.test import TestCase
from django.urls import reverse

from recipe_app.forms.forms import (
    IngredientFormSet,
    RecipeForm,
    TagCreationFormset
)
from recipe_app.models import (
    Ingredient,
    Recipe,
    RecipeIngredient
)
from recipe_app.views import (
    RECIPE_NOT_FOUND_ERROR,
    INGREDIENT_LIST_FORMSET_PREFIX,
    TAG_CREATE_FORMSET_PREFIX
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
            rendered_ingredients_list.prefix,
            INGREDIENT_LIST_FORMSET_PREFIX
        )
        self.assertEqual(
            rendered_ingredients_list.data,
            {
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '1',
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': self.ingredient.name,
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': self.recipe_ingredient.measurement
            }
        )

        rendered_tag_create = mock_render.call_args[0][2]['tag_create']
        self.assertIsInstance(rendered_tag_create, TagCreationFormset)
        self.assertEqual(
            rendered_tag_create.prefix,
            TAG_CREATE_FORMSET_PREFIX
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
