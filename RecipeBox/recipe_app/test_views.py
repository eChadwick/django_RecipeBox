import math

from django.test import TestCase
from django.urls import reverse

from recipe_app.models import Recipe, Ingredient, RecipeIngredient
from recipe_app.views import DEFAULT_PAGINATION


class IngredientViewTests(TestCase):
    num_test_ingredients = DEFAULT_PAGINATION + 5

    def setUp(self):
        for x in range(self.num_test_ingredients):
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

    def setUp(self):
        for x in range(self.num_test_recipes):
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
        response = self.client.get(reverse('recipes'))
        self.assertEqual(response.status_code, 200)

    def test_recipe_list_has_number_of_pages(self):
        response = self.client.get(reverse('recipes'))
        num_pages = response.context['num_pages']

        total_recipes = Recipe.objects.all().count()
        expected_num_pages = math.ceil(total_recipes / DEFAULT_PAGINATION)

        self.assertEqual(num_pages, expected_num_pages)

    def test_recipe_list_default_pagination(self):
        response = self.client.get(reverse('recipes'))
        self.assertEqual(
            len(response.context['recipes_list']),
            DEFAULT_PAGINATION
        )

        total_recipes = Recipe.objects.all().count()
        last_page_result_number = total_recipes % DEFAULT_PAGINATION
        response = self.client.get(reverse('recipes')+'?page=2')
        self.assertEqual(
            len(response.context['recipes_list']),
            last_page_result_number
        )

    def test_recipe_list_parameterized_pagination(self):
        pagination = 5
        response = self.client.get(
            reverse('recipes')+f'?pagination={pagination}'
        )
        self.assertEqual(
            len(response.context['recipes_list']),
            pagination
        )
