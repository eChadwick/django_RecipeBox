from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.test import TestCase
from recipe_app.models import Ingredient

# Create your tests here.


class IngredientModelTests(TestCase):

    # Tests that save fails when name is longer than constraint allows
    def test_save_name_length(self):
        too_long_name = ''
        for i in range(0, 201):
            too_long_name = too_long_name + 'a'
        ingredient = Ingredient(name=too_long_name)

        with self.assertRaises(ValidationError):
            ingredient.save()

    # Tests that names are always saved as title case
    def test_save_name_casing(self):
        mixed_case_name = 'iNgEdIeNt nAme'
        new_ingredient = Ingredient(name=mixed_case_name)
        new_ingredient.save()

        saved_ingredient = Ingredient.objects.get(name=mixed_case_name.title())
        self.assertEqual(saved_ingredient.name, mixed_case_name.title())

    # Tests that saving a duplicate name is a no-op
    def test_save_duplicates(self):
        ingredient_name = 'ingredient name'
        first_ingredient = Ingredient(name=ingredient_name)
        first_ingredient.save()
        self.assertIsNotNone(first_ingredient.pk)

        second_ingredient = Ingredient(name=ingredient_name)
        second_ingredient.save()
        self.assertIsNone(second_ingredient.pk)
