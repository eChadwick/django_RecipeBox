from unittest.mock import patch

from django.forms import CharField
from django.test import TestCase

from recipe_app.forms import IngredientForm, RecipeForm, IngredientFormSet, extra_ingredient_form_count
from recipe_app.models import Recipe


class IngredientFormTests(TestCase):
    def test_fields(self):
        form = IngredientForm()

        name_field = form.fields['name']
        self.assertIsInstance(name_field, CharField)
        self.assertFalse(name_field.required)
        self.assertEqual(name_field.max_length, 255)
        self.assertEqual('Ingredient Name', form.fields['name'].label)

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

    @patch('recipe_app.forms.IngredientForm.__eq__', return_value=True)
    def test_equal(self, mock_eq):
        IngredientFormSet1 = IngredientFormSet({})
        IngredientFormSet2 = IngredientFormSet({})
        self.assertEqual(IngredientFormSet1, IngredientFormSet2)

    @patch('recipe_app.forms.IngredientForm.__eq__', return_value=True)
    def test_not_equal(self, mock_eq):
        IngredientFormSet1 = IngredientFormSet({})
        IngredientFormSet2 = IngredientFormSet({
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-0-name': 'name'
        })
        self.assertNotEqual(IngredientFormSet1, IngredientFormSet2)

    def test_not_empty(self):
        formset = IngredientFormSet({
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-0-name': 'name'
        })
        self.assertFalse(formset.is_empty())

    def test_empty(self):
        formset = IngredientFormSet({})
        self.assertTrue(formset.is_empty())


class RecipeFormTests(TestCase):

    def test_fields(self):
        form = RecipeForm()
        self.assertIs(
            type(form.instance),
            Recipe
        )
        self.assertIn('name', form.fields)
        self.assertEqual('Recipe Name', form.fields['name'].label)
        self.assertIn('directions', form.fields)

    def test_equality_operator(self):
        form_data = {'name': 'test name', 'directions': 'do stuff'}
        form1 = RecipeForm(form_data)
        form2 = RecipeForm(form_data)
        self.assertEqual(form1, form2)
