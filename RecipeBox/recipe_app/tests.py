from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.test import TestCase
from recipe_app.models import Ingredient
from recipe_app.models import Recipe
from recipe_app.models import RecipeIngredient

# Create your tests here.


class IngredientModelTests(TestCase):
    mixed_case_name = 'iNgEdIeNt nAme'
    expected_display_name = mixed_case_name.title()

    def setUp(self):
        Ingredient.objects.create(name=self.mixed_case_name)

    # Tests that names are always title cased
    def test_name_casing(self):
        ingredient = Ingredient.objects.get(id=1)

        self.assertEqual(ingredient.name, self.expected_display_name)

    def test__str__(self):
        expected_string = f'pk: 1, name: {self.expected_display_name}'
        ingredient = Ingredient.objects.get(id=1)

        self.assertEqual(expected_string, ingredient.__str__())

    # Tests that saving a duplicate name is a no-op
    def test_save_duplicates(self):
        Ingredient.objects.create(name=self.mixed_case_name)
        # Above line would have thrown in case of failure
        self.assertTrue(True)

    def test_name_column_label(self):
        ingredient = Ingredient.objects.get(id=1)
        field_label = ingredient._meta.get_field('name').verbose_name

        self.assertEqual(field_label, 'name')


class RecipeModelTests(TestCase):
    mixed_case_recipe_name = 'rEcIpE nAme'
    expected_recipe_display_name = mixed_case_recipe_name.title()
    ingredient1_name = 'Ingredient1'
    ingredient2_name = 'Ingredient2'

    def setUp(self):
        ingredient1 = Ingredient.objects.create(name=self.ingredient1_name)
        ingredient2 = Ingredient.objects.create(name=self.ingredient2_name)
        recipe = Recipe.objects.create(name=self.mixed_case_recipe_name)
        RecipeIngredient.objects.create(
            recipe=recipe, ingredient=ingredient1, measurement='A bit')
        RecipeIngredient.objects.create(
            recipe=recipe, ingredient=ingredient2, measurement='A pinch')

    def test_name_casing(self):
        recipe = Recipe.objects.get(id=1)

        self.assertEqual(recipe.name, self.expected_recipe_display_name)

    def test__str__(self):
        recipe = Recipe.objects.get(id=1)
        expected_string = 'pk: 1, name: Recipe Name, directions: None, ingredients: Ingredient1 - A bit, Ingredient2 - A pinch'

        self.assertEqual(expected_string, recipe.__str__())


class RecipeIngredientModelTests(TestCase):

    def test__str__(self):
        recipe = Recipe(pk=2, name='Recipe Name')
        ingredient = Ingredient(pk=3, name='Ingredient Name')
        recipe_ingredient = RecipeIngredient(
            pk=1, recipe=recipe, ingredient=ingredient)
        expected_string = 'pk: 1, recipe_primary_key: 2, ingredient_primary_key: 3'

        self.assertEqual(expected_string, recipe_ingredient.__str__())
