import math

from unittest.mock import patch, ANY

from django.http import HttpResponse
from django.shortcuts import render
from django.test import TestCase, Client
from django.urls import reverse

from recipe_app.forms import RecipeForm, IngredientFormSet
from recipe_app.models import Recipe, Ingredient, RecipeIngredient
from recipe_app.views import DEFAULT_PAGINATION


class IngredientViewTests(TestCase):
    num_test_ingredients = DEFAULT_PAGINATION + 5

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for x in range(cls.num_test_ingredients):
            Ingredient.objects.create(name=f'Ingredient {x}')

    def test_ingredients_list_path(self):
        response = self.client.get('/ingredients/')
        self.assertEqual(response.status_code, 200)

    def test_ingredients_list_route_name(self):
        response = self.client.get(reverse('ingredients'))
        self.assertEqual(response.status_code, 200)

    def test_ingredients_list_has_number_of_pages(self):
        response = self.client.get(reverse('ingredients'))
        num_pages = response.context['num_pages']

        total_ingredients = Ingredient.objects.all().count()
        expected_num_pages = math.ceil(total_ingredients / DEFAULT_PAGINATION)

        self.assertEqual(num_pages, expected_num_pages)

    def test_ingredients_list_default_pagination(self):
        response = self.client.get(reverse('ingredients'))
        self.assertEqual(
            len(response.context['ingredients_list']),
            DEFAULT_PAGINATION
        )

        total_ingredients = Ingredient.objects.all().count()
        last_page_result_number = total_ingredients % DEFAULT_PAGINATION
        response = self.client.get(reverse('ingredients')+'?page=2')
        self.assertEqual(
            len(response.context['ingredients_list']),
            last_page_result_number
        )

    def test_ingredients_parameterized_pagination(self):
        pagination = 5
        response = self.client.get(
            reverse('ingredients')+f'?pagination={pagination}'
        )
        self.assertEqual(
            len(response.context['ingredients_list']),
            pagination
        )


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
    form_data = {
            'name': 'recipe name',
            'directions': 'do stuff',
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-0-name': 'ingredient name',
            'form-0-measurement': 'a pinch'
        }

    def test_get_renders_the_correct_html(self, mock_render):
        self.client.get(reverse('recipe-create'))
        mock_render.assert_called_with(
            ANY, 'recipe_app/recipe_form.html', ANY
        )

    def test_get_should_return_unbound_forms(self, mock_render):
        self.client.get(reverse('recipe-create'))
        rendered_context = mock_render.call_args[0][2]
        self.assertFalse(rendered_context['recipe'].is_bound)
        self.assertFalse(rendered_context['ingredients'].is_bound)

    @patch('recipe_app.forms.RecipeForm.is_valid', return_value=False)
    def test_post_should_rerender_form_on_recipe_errors(self, mock_is_valid, mock_render):
        self.client.post(reverse('recipe-create'), self.form_data)

        rendered_template = mock_render.call_args[0][1]
        self.assertEqual(rendered_template, 'recipe_app/recipe_form.html')

        rendered_recipe = mock_render.call_args[0][2]['recipe']
        self.assertEqual = (rendered_recipe, RecipeForm(self.form_data))

        rendered_ingredients = mock_render.call_args[0][2]['ingredients']
        self.assertEqual = (rendered_ingredients, IngredientFormSet(self.form_data))

    @patch('recipe_app.forms.IngredientFormSet.is_valid', return_value=False)
    def test_post_should_rerender_form_on_ingredient_errors(self, mock_is_valid, mock_render):
        self.client.post(reverse('recipe-create'), self.form_data)

        rendered_template = mock_render.call_args[0][1]
        self.assertEqual(rendered_template, 'recipe_app/recipe_form.html')

        rendered_recipe = mock_render.call_args[0][2]['recipe']
        self.assertEqual = (rendered_recipe, RecipeForm(self.form_data))

        rendered_ingredients = mock_render.call_args[0][2]['ingredients']
        self.assertEqual = (rendered_ingredients, IngredientFormSet(self.form_data))