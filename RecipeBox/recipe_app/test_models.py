from django.test import TestCase
from django.db.models import ForeignKey, CASCADE, RESTRICT
from django.db.models.fields import CharField

from recipe_app.models import Ingredient
from recipe_app.models import Recipe
from recipe_app.models import RecipeIngredient

# Create your tests here.


class IngredientModelTests(TestCase):
    mixed_case_name = 'iNgrEdIeNt nAme'
    title_case_name = mixed_case_name.title()

    def test_name_casing(self):
        ingredient = Ingredient(name=self.mixed_case_name)
        self.assertEqual(ingredient.name, self.title_case_name)

    def test_save_duplicates(self):
        Ingredient.objects.create(name=self.mixed_case_name)
        Ingredient.objects.create(name=self.mixed_case_name)
        # Second create would have thrown in case of failure
        self.assertTrue(True)

    def test_field_labels(self):
        ingredient = Ingredient()
        self.assertTrue(ingredient._meta.get_field('name'))


class RecipeModelTests(TestCase):
    mixed_case_name = 'rEcIpE nAme'
    tile_case_name = mixed_case_name.title()

    def test_name_casing(self):
        recipe = Recipe(name=self.mixed_case_name)
        self.assertEqual(recipe.name, self.tile_case_name)

    def test_field_labels(self):
        recipe = Recipe()
        self.assertTrue(recipe._meta.get_field('name'))
        self.assertTrue(recipe._meta.get_field('directions'))
        self.assertEqual(
            recipe._meta.related_objects[0].name, 'recipeingredient')


class RecipeIngredientModelTests(TestCase):

    def test_fields(self):
        recipe_ingredient = RecipeIngredient()

        measurement_field = recipe_ingredient._meta.get_field('measurement')
        self.assertIsInstance(
            measurement_field,
            CharField
        )
        self.assertFalse(
            measurement_field.null
        )

        ingredient_field = recipe_ingredient._meta.get_field('ingredient')
        self.assertIsInstance(
            ingredient_field,
            ForeignKey
        )
        self.assertEqual(
            ingredient_field.remote_field.field.name,
            'ingredient'
        )
        self.assertEqual(
            ingredient_field.remote_field.on_delete,
            RESTRICT
        )

        recipe_field = recipe_ingredient._meta.get_field('recipe')
        self.assertIsInstance(
            recipe_field,
            ForeignKey
        )
        self.assertEqual(
            recipe_field.remote_field.field.name,
            'recipe'
        )
        self.assertEqual(
            recipe_field.remote_field.on_delete,
            CASCADE
        )
