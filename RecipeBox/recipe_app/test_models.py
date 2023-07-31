from django.test import TestCase
from django.db.models.deletion import RestrictedError

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
        recipe = Recipe(ga)
        self.assertTrue(recipe._meta.get_field('name'))
        self.assertTrue(recipe._meta.get_field('directions'))
        self.assertEqual(recipe._meta.related_objects[0].name, 'recipeingredient')

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

    def test_cant_delete_ingredient_with_recipe_ingredients(self):
        with self.assertRaises(RestrictedError):
            Ingredient.objects.filter(id=1).delete()

    def test_cascading_delete(self):
        Recipe.objects.filter(id=1).delete()
        ri_count = RecipeIngredient.objects.all().count()
        self.assertEqual(ri_count, 0)
