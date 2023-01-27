from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.test import TestCase
from recipe_app.models import Ingredient
from recipe_app.models import Recipe

# Create your tests here.


class IngredientModelTests(TestCase):

    # Tests that names are always title cased
    def test_name_casing(self):
        mixed_case_name = 'iNgEdIeNt nAme'
        new_ingredient = Ingredient(name=mixed_case_name)

        self.assertEqual(new_ingredient.name, mixed_case_name.title())

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

    def test_save_title_cases_names(self):
        mixed_case_name = 'rEcIpE nAme'
        recipe = Recipe(name=mixed_case_name)
        recipe.save()

        saved_recipe = Recipe.objects.get(name=mixed_case_name.title())
        self.assertEqual(saved_recipe.name, mixed_case_name.title())

    def test_save_noops_on_duplicate_names(self):
        recipe_name = 'recipe name'
        first_recipe = Recipe(name=recipe_name)
        first_recipe.save()
        self.assertIsNotNone(first_recipe.pk)

        second_recipe = Recipe(name=recipe_name)
        second_recipe.save()
        self.assertIsNone(second_recipe.pk)
