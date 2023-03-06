from django.test import TestCase
from django.urls import reverse
from recipe_app.models import Ingredient

class IngredientViewTests(TestCase):

    def setupTestData(self):
        for x in range(5):
            Ingredient.objects.create(name=f'Ingredient {x}')

    def test_ingredients_list_path(self):
        response = self.client.get('/ingredients/')
        self.assertEqual(response.status_code, 200)

    def test_ingredients_list_name(self):
        response = self.client.get(reverse('ingredients'))
        self.assertEqual(response.status_code, 200)