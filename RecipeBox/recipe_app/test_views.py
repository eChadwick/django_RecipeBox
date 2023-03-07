from django.test import TestCase
from django.urls import reverse
from recipe_app.models import Ingredient


class IngredientViewTests(TestCase):
    num_test_ingredients = 10

    def setUp(self):
        for x in range(self.num_test_ingredients):
            Ingredient.objects.create(name=f'Ingredient {x}')

    def test_ingredients_list_path(self):
        response = self.client.get('/ingredients/')
        self.assertEqual(response.status_code, 200)

    def test_ingredients_list_route_name(self):
        response = self.client.get(reverse('ingredients'))
        self.assertEqual(response.status_code, 200)

    def test_list_all_ingredients(self):
        response = self.client.get(reverse('ingredients'))
        self.assertEqual(
            len(response.context['ingredients_list']),
            self.num_test_ingredients
        )
