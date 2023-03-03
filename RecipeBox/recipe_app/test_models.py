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
    ingredient1_measurement = 'A bit'
    ingredient2_name = 'Ingredient2'
    ingredient2_measurement = 'A pinch'
    directions = 'Do stuff'

    def setUp(self):
        ingredient1 = Ingredient.objects.create(name=self.ingredient1_name)
        ingredient2 = Ingredient.objects.create(name=self.ingredient2_name)
        recipe = Recipe.objects.create(
            name=self.mixed_case_recipe_name,
            directions=self.directions)
        RecipeIngredient.objects.create(
            recipe=recipe, ingredient=ingredient1,
            measurement=self.ingredient1_measurement)
        RecipeIngredient.objects.create(
            recipe=recipe, ingredient=ingredient2,
            measurement=self.ingredient2_measurement)

    def test_name_casing(self):
        recipe = Recipe.objects.get(id=1)

        self.assertEqual(recipe.name, self.expected_recipe_display_name)

    def test__str__(self):
        recipe = Recipe.objects.get(id=1)
        expected_string = (
            f'pk: 1, name: {self.expected_recipe_display_name}, directions: '
            f'{self.directions}, ingredients: {self.ingredient1_name} - '
            f'{self.ingredient1_measurement}, {self.ingredient2_name} - '
            f'{self.ingredient2_measurement}'
        )

        self.assertEqual(expected_string, recipe.__str__())

    def test_field_labels(self):
        recipe = Recipe.objects.get(id=1)
        expected_field_names = {'directions', 'id', 'name'}
        actual_field_names = set()
        for field in recipe._meta.fields:
            actual_field_names.add(field.name)

        self.assertEqual(expected_field_names, actual_field_names)


class RecipeIngredientModelTests(TestCase):
    recipe_name = 'Recipe Name'
    ingredient_name = 'Ingredient Name'
    measurement = 'Some'

    def setUp(self):
        recipe = Recipe.objects.create(name=self.recipe_name)
        ingredient = Ingredient.objects.create(name=self.ingredient_name)
        RecipeIngredient.objects.create(
            recipe=recipe, ingredient=ingredient, measurement=self.measurement)

    def test__str__(self):
        recipe_ingredient = RecipeIngredient.objects.get(id=1)
        expected_string = (
            f'pk: 1, recipe_pk: 1, recipe_name: {self.recipe_name}, '
            f'ingredient_pk: 1, ingredient_name: {self.ingredient_name}, '
            f'measurement: {self.measurement}'
        )
        self.assertEqual(expected_string, recipe_ingredient.__str__())

    def test_field_labels(self):
        recipe_ingredient = RecipeIngredient.objects.get(id=1)
        expected_field_names = {'ingredient', 'id', 'measurement', 'recipe'}
        actual_field_names = set()
        for field in recipe_ingredient._meta.fields:
            actual_field_names.add(field.name)

        self.assertEqual(expected_field_names, actual_field_names)
