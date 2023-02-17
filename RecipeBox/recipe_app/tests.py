from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.test import TestCase
from recipe_app.models import Ingredient
from recipe_app.models import Recipe
from recipe_app.models import RecipeIngredient

# Create your tests here.


class IngredientModelTests(TestCase):

    # Tests that names are always title cased
    def test_name_casing(self):
        mixed_case_name = 'iNgEdIeNt nAme'
        new_ingredient = Ingredient(name=mixed_case_name)

        self.assertEqual(new_ingredient.name, mixed_case_name.title())

    def test__str__(self):
        new_ingredient = Ingredient(pk =1, name='Test')
        expected_string = 'pk: 1, name: Test'

        self.assertEqual(expected_string, new_ingredient.__str__())

    # Tests that saving a duplicate name is a no-op
    def test_save_duplicates(self):
        ingredient_name = 'ingredient name'
        first_ingredient = Ingredient(name=ingredient_name)
        first_ingredient.save()
        self.assertIsNotNone(first_ingredient.pk)

        second_ingredient = Ingredient(name=ingredient_name)
        second_ingredient.save()
        self.assertIsNone(second_ingredient.pk)


class RecipeModelTests(TestCase):

    def test_name_casing(self):
        mixed_case_name = 'rEcIpE nAme'
        recipe = Recipe(name=mixed_case_name)

        self.assertEqual(recipe.name, mixed_case_name.title())

    def test__str__(self):
        test_recipe_name = 'Recipe Name'
        test_directions = 'Do stuff'
        test_pk = 1
        test_ingredient_name1 = 'Ingredient1'
        test_ingredient_measurement1 = 'A bit'
        test_ingredient_name2 = 'Ingredient2'
        test_ingredient_measurement2 = 'A pinch'

        recipe = Recipe(pk=test_pk, name=test_recipe_name, directions=test_directions)
        recipe.save()
        ingredient1 = Ingredient(name=test_ingredient_name1)
        ingredient1.save()
        ingredient2 = Ingredient(name=test_ingredient_name2)
        ingredient2.save()
        recipe_ingredient1 = RecipeIngredient(recipe=recipe, ingredient=ingredient1, measurement=test_ingredient_measurement1)
        recipe_ingredient1.save()
        recipe_ingredient2 = RecipeIngredient(recipe=recipe, ingredient=ingredient2, measurement=test_ingredient_measurement2)
        recipe_ingredient2.save()

        expected_string = (f'pk: {test_pk}, name: {test_recipe_name}, directions: {test_directions},'
                           f' ingredients: {test_ingredient_name1} - {test_ingredient_measurement1}, '
                           f'{test_ingredient_name2} - {test_ingredient_measurement2}'
        )

        self.assertEqual(expected_string,recipe.__str__())

class RecipeIngredientModelTests(TestCase):

    def test__str__(self):
        recipe = Recipe(pk=2, name='Recipe Name')
        ingredient = Ingredient(pk=3, name='Ingredient Name')
        recipe_ingredient = RecipeIngredient(pk=1, recipe=recipe, ingredient=ingredient)
        expected_string = 'pk: 1, recipe_primary_key: 2, ingredient_primary_key: 3'

        self.assertEqual(expected_string, recipe_ingredient.__str__())