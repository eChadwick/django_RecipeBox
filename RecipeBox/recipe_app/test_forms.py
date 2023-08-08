from django.forms import CharField
from django.test import TestCase

from recipe_app.forms import IngredientForm, RecipeForm, IngredientFormSet, extra_ingredient_form_count
from recipe_app.models import Recipe, Ingredient


class IngredientFormTests(TestCase):
    def test_fields(self):
        form = IngredientForm()
        self.assertIs(
            type(form.instance),
            Ingredient
        )
        self.assertIn('name', form.fields)

        measurement_field = form.fields['measurement']
        self.assertIsInstance(measurement_field, CharField)
        self.assertFalse(measurement_field.required)
        self.assertEqual(measurement_field.max_length, 255)

    def test_equality_operator(self):
        form_data = {'name': 'test name', 'measurement': 'a bit'}
        form1 = IngredientForm(form_data)
        form2 = IngredientForm(form_data)
        self.assertEqual(form1, form2)


class IngredientFormsetTests(TestCase):

    def test_extra_formset_count(self):
        formset = IngredientFormSet()
        self.assertEqual(
            formset.total_form_count(),
            extra_ingredient_form_count
        )


class RecipeFormTests(TestCase):

    def test_fields(self):
        form = RecipeForm()
        self.assertIs(
            type(form.instance),
            Recipe
        )
        self.assertIn('name', form.fields)
        self.assertIn('directions', form.fields)
