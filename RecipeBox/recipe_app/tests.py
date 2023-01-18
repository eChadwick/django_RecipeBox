from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.test import TestCase
from recipe_app.models import Ingredient

# Create your tests here.
class IngredientModelTests(TestCase):

    def test_null_name_fails(self):
        uut = Ingredient()

        with self.assertRaises(ValidationError):
            uut.full_clean()

    def test_too_long_name_fails(self):
        too_long_name = ''
        for i in range(0,201):
            too_long_name = too_long_name + str(i)

        uut = Ingredient(name=too_long_name)

        with self.assertRaises(ValidationError):
            uut.full_clean()

    def test_name_casing(self):
        mixed_case_name = 'iNgReDiEnt NaMe'
        uut = Ingredient(name=mixed_case_name)

        uut.full_clean()
        self.assertEqual(uut.name,mixed_case_name.capitalize())

    def test_duplicate_insert_fails(self):
        ingredient_name = 'Ingredient Name'
        first_ingredient = Ingredient(name=ingredient_name)
        first_ingredient.save()

        duplicate_ingredient = Ingredient(name=ingredient_name)
        with self.assertRaises(IntegrityError):
            duplicate_ingredient.save()
