import math

from unittest.mock import patch, ANY

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.test import TestCase, Client
from django.urls import reverse

from recipe_app.forms import RecipeForm, IngredientFormSet
from recipe_app.models import Recipe, Ingredient, RecipeIngredient
from recipe_app.views import DEFAULT_PAGINATION, RECIPE_NOT_FOUND_ERROR


class RecipeListViewTests(TestCase):
    num_test_recipes = DEFAULT_PAGINATION + 5

    @classmethod
    def setUp(cls):
        for x in range(cls.num_test_recipes):
            recipe = Recipe.objects.create(
                name=f'Recipe {x}',
                directions=f'These are the directions for Recipe {x}'
            )
            for y in range(x):
                ingredient = Ingredient.objects.create(
                    name=f'Recipe {x} - Ingredient {y}'
                )
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    measurement='1 cup'
                )

    def test_recipe_list_path(self):
        response = self.client.get('/recipes/')
        self.assertEqual(response.status_code, 200)

    def test_recipe_list_route_name(self):
        response = self.client.get(reverse('recipe-list'))
        self.assertEqual(response.status_code, 200)

    def test_recipe_list_has_number_of_pages(self):
        response = self.client.get(reverse('recipe-list'))
        num_pages = response.context['num_pages']

        total_recipes = Recipe.objects.all().count()
        expected_num_pages = math.ceil(total_recipes / DEFAULT_PAGINATION)

        self.assertEqual(num_pages, expected_num_pages)

    def test_recipe_list_default_pagination(self):
        response = self.client.get(reverse('recipe-list'))
        self.assertEqual(
            len(response.context['recipes_list']),
            DEFAULT_PAGINATION
        )

        total_recipes = Recipe.objects.all().count()
        last_page_result_number = total_recipes % DEFAULT_PAGINATION
        response = self.client.get(reverse('recipe-list')+'?page=2')
        self.assertEqual(
            len(response.context['recipes_list']),
            last_page_result_number
        )

    def test_recipe_list_parameterized_pagination(self):
        pagination = 5
        response = self.client.get(
            reverse('recipe-list')+f'?pagination={pagination}'
        )
        self.assertEqual(
            len(response.context['recipes_list']),
            pagination
        )

    def test_recipe_list_includes_current_page_number(self):
        response = self.client.get(reverse('recipe-list'))
        self.assertEqual(response.context['current_page'], 1)

    def test_recipe_list_includes_pagination_value(self):
        response = self.client.get(reverse('recipe-list'))
        self.assertEqual(response.context['pagination'], DEFAULT_PAGINATION)


class RecipeDeleteViewTestCase(TestCase):
    def setUp(self):
        self.recipe_name = 'Spaghetti Carbonara'
        self.recipe = Recipe.objects.create(
            name=self.recipe_name, directions='Cook spaghetti, cook pancetta, mix eggs and cheese')
        self.client = Client()

    def test_recipe_delete_view_with_valid_recipe(self):
        # Ensure the recipe is deleted successfully with a valid recipe id
        response = self.client.post(
            reverse('recipe-delete', args=[self.recipe.id]))
        self.assertEqual(response.status_code, 302)  # redirect to success url
        self.assertFalse(Recipe.objects.filter(name=self.recipe_name).exists())

    def test_recipe_delete_view_with_invalid_recipe(self):
        # Ensure the recipe is not deleted with an invalid recipe id
        response = self.client.post(
            reverse('recipe-delete', args=[self.recipe.id + 1]))
        self.assertEqual(response.status_code, 404)  # recipe not found

    def test_recipe_delete_view_get_request(self):
        # Ensure GET requests are not allowed
        response = self.client.get(
            reverse('recipe-delete', args=[self.recipe.id]))
        self.assertEqual(response.status_code, 405)  # method not allowed

    def test_recipe_delete_view_url(self):
        # Ensure the actual url of the recipe-delete route is /recipes/delete/<recipe_pk>/
        url = reverse('recipe-delete', args=[self.recipe.id])
        self.assertEqual(url, f'/recipes/delete/{self.recipe.id}/')


class RecipeDetailViewTestCase(TestCase):
    def setUp(self):
        self.ingredient1 = Ingredient.objects.create(name='salt')
        self.ingredient2 = Ingredient.objects.create(name='pepper')
        self.recipe = Recipe.objects.create(
            name='Pasta With Salt And Pepper',
            directions='Cook pasta, add salt and pepper to taste.'
        )
        self.recipe_ingredient1 = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient1,
            measurement='1 tsp'
        )
        self.recipe_ingredient2 = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient2,
            measurement='1 tsp'
        )

    def test_recipe_detail_view(self):
        url = reverse('recipe-detail', args=[self.recipe.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['recipe'].name, self.recipe.name)
        self.assertEqual(
            response.context['recipe'].directions, self.recipe.directions)
        expected_ingredient_list = [
            {'name': self.ingredient1.name,
                'measurement': self.recipe_ingredient1.measurement},
            {'name': self.ingredient2.name,
                'measurement': self.recipe_ingredient2.measurement}
        ]
        self.assertEqual(
            response.context['ingredients_list'], expected_ingredient_list)

    def test_recipe_detail_view_invalid_recipe(self):
        url = reverse('recipe-detail', args=[self.recipe.pk + 1])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


@patch('recipe_app.views.render', return_value=HttpResponse())
class RecipeCreateViewTests(TestCase):

    def test_get_renders_the_correct_html(self, mock_render):
        self.client.get(reverse('recipe-create'))
        mock_render.assert_called_with(
            ANY, 'recipe_app/recipe_form.html', ANY
        )

    def test_get_should_return_unbound_forms(self, mock_render):
        self.client.get(reverse('recipe-create'))
        rendered_context = mock_render.call_args[0][2]
        self.assertFalse(rendered_context['recipe'].is_bound)
        self.assertFalse(rendered_context['ingredients_list'].is_bound)

    def test_get_should_pass_request_action(self, mock_render):
        self.client.get(reverse('recipe-create'))
        rendered_context = mock_render.call_args[0][2]
        self.assertEqual(rendered_context['action'], 'create')

    @patch('recipe_app.forms.RecipeForm.is_valid', return_value=False)
    def test_post_should_rerender_form_on_recipe_errors(self, mock_is_valid, mock_render):
        form_data = {
            'name': 'Test Name',
            'form-0-name': 'Ingredient 1',
            'form-0-measurement': 'Amount 1',
            'directions': 'Do things'
        }
        self.client.post(reverse('recipe-create'), form_data)

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
                'form-0-name': form_data['form-0-name'],
                'form-0-measurement': form_data['form-0-measurement']
            }
        )

    @patch('recipe_app.forms.IngredientFormSet.is_valid', return_value=False)
    def test_post_should_rerender_form_on_ingredient_errors(self, mock_is_valid, mock_render):
        form_data = {
            'name': 'Test Name',
            'form-0-name': 'Ingredient 1',
            'form-0-measurement': 'Amount 1',
            'directions': 'Do things'
        }
        self.client.post(reverse('recipe-create'), form_data)

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
                'form-0-name': form_data['form-0-name'],
                'form-0-measurement': form_data['form-0-measurement']
            }
        )

    def test_recipe_form_has_error_when_no_directions_or_ingredients(self, mock_render):
        form_data = {
            'name': 'Test Name',
            'form-0-name': '',
            'form-0-measurement': '',
            'directions': ''
        }
        self.client.post(reverse('recipe-create'), form_data)

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
                'form-0-name': form_data['form-0-name'],
                'form-0-measurement': form_data['form-0-measurement']
            }
        )

    @patch('recipe_app.views.redirect', wraps=redirect)
    def test_success(self, mock_redirect, mock_render):
        form_data = {
            'name': 'Recipe Name',
            'directions': 'directions',
            'form-TOTAL_FORMS': '3',
            'form-INITIAL_FORMS': '1',
            'form-0-name': 'form-0-name',
            'form-0-measurement': 'form-0-measurement',
            'form-0-DELETE': '',
            'form-1-name': 'form-1-name',
            'form-1-measurement': 'form-1-measurement',
            'form-1-DELETE': '',
            'form-2-name': 'dont create this',
            'form-2-measurement': 'doesnt matter',
            'form-2-DELETE': 'on'
        }

        self.client.post(reverse('recipe-create'), form_data)

        recipe = Recipe.objects.filter(name__iexact=form_data['name'])
        self.assertTrue(recipe)
        self.assertEqual(recipe[0].name, form_data['name'])
        self.assertEqual(recipe[0].directions, form_data['directions'])

        ingredient1 = Ingredient.objects.filter(
            name__iexact=form_data['form-0-name'])
        self.assertTrue(ingredient1)

        ingredient2 = Ingredient.objects.filter(
            name__iexact=form_data['form-1-name'])
        self.assertTrue(ingredient2)

        self.assertEqual(RecipeIngredient.objects.filter(
            recipe=recipe[0],
            ingredient=ingredient1[0],
            measurement=form_data['form-0-measurement']).count(),
            1
        )

        self.assertFalse(
            Ingredient.objects.filter(
                name__iexact=form_data['form-2-name']).exists()
        )

        self.assertEqual(RecipeIngredient.objects.filter(
            recipe=recipe[0],
            ingredient=ingredient2[0],
            measurement=form_data['form-1-measurement']).count(),
            1
        )

        mock_redirect.assert_called_with(
            reverse('recipe-detail', args=[recipe[0].pk]))


@patch('recipe_app.views.render', return_value=HttpResponse())
class RecipeUpdateViewTests(TestCase):

    def setUp(self):
        self.ingredient1 = Ingredient.objects.create(name='Test Ingredient 1')
        self.ingredient2 = Ingredient.objects.create(name='Test Ingredient 2')
        self.recipe = Recipe.objects.create(
            name='Test Recipe',
            directions='Test Directions'
        )
        self.recipe_ingredient1 = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient1,
            measurement='a bunch'
        )
        self.recipe_ingredient2 = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient2,
            measurement='a bit'
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
                'form-TOTAL_FORMS': '2',
                'form-INITIAL_FORMS': '2',
                'form-0-name': self.ingredient1.name,
                'form-0-measurement': self.recipe_ingredient1.measurement,
                'form-1-name': self.ingredient2.name,
                'form-1-measurement': self.recipe_ingredient2.measurement
            }
        )

    @patch('recipe_app.forms.RecipeForm.is_valid', return_value=False)
    def test_post_should_rerender_form_on_recipe_errors(self, mock_is_valid, mock_render):
        form_data = {
            'name': 'Test Name',
            'form-0-name': 'Ingredient 1',
            'form-0-measurement': 'Amount 1',
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
                'form-0-name': form_data['form-0-name'],
                'form-0-measurement': form_data['form-0-measurement']
            }
        )

    @patch('recipe_app.forms.IngredientFormSet.is_valid', return_value=False)
    def test_post_should_rerender_form_on_ingredient_errors(self, mock_is_valid, mock_render):
        form_data = {
            'name': 'Test Name',
            'form-0-name': 'Ingredient 1',
            'form-0-measurement': 'Amount 1',
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
                'form-0-name': form_data['form-0-name'],
                'form-0-measurement': form_data['form-0-measurement']
            }
        )

    def test_recipe_form_has_error_when_no_directions_or_ingredients(self, mock_render):
        form_data = {
            'name': 'Test Name',
            'form-0-name': '',
            'form-0-measurement': '',
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
                'form-0-name': form_data['form-0-name'],
                'form-0-measurement': form_data['form-0-measurement']
            }
        )

    def test_post_should_404_on_recipe_not_found(self, _):
        updated_form_data = {
            'name': 'new name',
            'directions': 'new directions',
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-0-name': self.ingredient1.name,
            'form-0-measurement': 'updated measurement',
            'form-2-name': 'new ingredient name',
            'form-2-measurement': 'new ingredient measurement'
        }

        response = self.client.post(
            reverse('recipe-update', args=[self.recipe.pk + 1]),
            updated_form_data
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content.decode(), RECIPE_NOT_FOUND_ERROR)

    @patch('recipe_app.views.redirect', wraps=redirect)
    def test_success(self, mock_redirect, _):
        updated_form_data = {
            'name': 'New Name',
            'directions': 'new directions',
            'form-TOTAL_FORMS': '3',
            'form-INITIAL_FORMS': '2',
            'form-0-name': self.ingredient1.name,
            'form-0-measurement': 'updated measurgdement',
            'form-0-DELETE': '',
            'form-1-name': self.ingredient2.name,
            'form-1-measurement': 'deleted measurement',
            'form-1-DELETE': 'on',
            'form-2-name': 'New Ingredient Name',
            'form-2-measurement': 'new ingredient measurement',
            'form-2-DELETE': ''
        }

        self.client.post(
            reverse('recipe-update', args=[self.recipe.pk]), updated_form_data
        )
        self.recipe = Recipe.objects.get(pk=self.recipe.pk)

        self.assertEqual(self.recipe.name, updated_form_data['name'])
        self.assertEqual(self.recipe.directions,
                         updated_form_data['directions'])

        self.assertTrue(
            Ingredient.objects.filter(pk=self.ingredient1.pk).exists()
        )
        self.assertTrue(
            Ingredient.objects.filter(pk=self.ingredient2.pk).exists()
        )

        new_ingredient = Ingredient.objects.filter(
            name=updated_form_data['form-2-name'])
        self.assertTrue(new_ingredient.exists())

        self.assertEqual(
            RecipeIngredient.objects.filter(
                recipe=self.recipe.pk,
                ingredient=self.recipe_ingredient1.ingredient.pk,
                measurement=updated_form_data['form-0-measurement']
            ).count(),
            1
        )

        self.assertFalse(
            RecipeIngredient.objects.filter(
                recipe=self.recipe.pk,
                ingredient=self.recipe_ingredient2.ingredient.pk
            ).exists()
        )

        self.assertEqual(
            RecipeIngredient.objects.filter(
                recipe=self.recipe.pk,
                ingredient=new_ingredient[0].pk,
                measurement=updated_form_data['form-2-measurement']
            ).count(),
            1
        )

        mock_redirect.assert_called_with(
            reverse('recipe-detail', args=[self.recipe.pk]))
