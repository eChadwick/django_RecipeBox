from django.test import TestCase
from django.db.models import ForeignKey, ManyToManyField, CASCADE, RESTRICT
from django.db.models.fields import CharField

from recipe_app.models import Ingredient, Recipe, RecipeIngredient


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

    def test_fields(self):
        ingredient = Ingredient()

        name_field = ingredient._meta.get_field('name')
        self.assertIsInstance(name_field, CharField)
        self.assertFalse(name_field.null)
        self.assertTrue(name_field.unique)
        self.assertEqual(200, name_field.max_length)
        self.assertTrue(name_field.blank)


class RecipeModelTests(TestCase):
    mixed_case_name = 'rEcIpE nAme'
    tile_case_name = mixed_case_name.title()

    def test_name_casing(self):
        recipe = Recipe(name=self.mixed_case_name)
        self.assertEqual(recipe.name, self.tile_case_name)

    def test_fields(self):
        recipe = Recipe()

        name_field = recipe._meta.get_field('name')
        self.assertIsInstance(name_field, CharField)
        self.assertFalse(name_field.null)
        self.assertTrue(name_field.unique)
        self.assertEqual(200, name_field.max_length)
        self.assertTrue(name_field.blank)

        directions_field = recipe._meta.get_field('directions')
        self.assertIsInstance(directions_field, CharField)
        self.assertTrue(directions_field.null)
        self.assertEqual(5000, directions_field.max_length)
        self.assertTrue(directions_field.blank)

        ingredient_field = recipe._meta.get_field('ingredients')
        self.assertIsInstance(ingredient_field, ManyToManyField)
        self.assertIs(
            ingredient_field.remote_field.through,
            RecipeIngredient
        )
        self.assertEqual(
            ingredient_field.remote_field.related_name,
            'ingredients'
        )


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
        self.assertEqual(
            measurement_field.max_length,
            200
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
