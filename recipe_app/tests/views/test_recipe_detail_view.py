from django.test import TestCase
from django.urls import reverse

from recipe_app.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag
)


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

        self.tag = Tag.objects.create(name='RecipeTag')
        self.recipe.tags.add(self.tag)

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

        self.assertEqual(len(response.context['recipe'].tags.all()), 1)
        self.assertEqual(response.context['recipe'].tags.all()[0], self.tag)

    def test_recipe_detail_view_invalid_recipe(self):
        url = reverse('recipe-detail', args=[self.recipe.pk + 1])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
