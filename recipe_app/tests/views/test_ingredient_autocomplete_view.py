from django.test import TestCase
from django.urls import reverse
from recipe_app.models import Ingredient
from recipe_app.views import INGREDIENT_SUGGESTION_PAGINATION

class IngredientAutoCompleteViewTests(TestCase):
    def test_endpoint(self):
        Ingredient.objects.create(name='Honey Mustard')
        Ingredient.objects.create(name='Mustard Seed')
        Ingredient.objects.create(name='Carrot')

        results = self.client.get(reverse('ingredient-autocomplete'), {'query': ''}).json()
        self.assertEqual(len(results), 3)

        query = 'must'
        results = self.client.get(reverse('ingredient-autocomplete'), {'query': query}).json()
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIn(query, result.lower())

    def test_pagination(self):
        for i in range(INGREDIENT_SUGGESTION_PAGINATION + 1):
            Ingredient.objects.create(name=f'Ingredient{i}')

        results = self.client.get(reverse('ingredient-autocomplete')).json()
        self.assertEqual(len(results), INGREDIENT_SUGGESTION_PAGINATION)