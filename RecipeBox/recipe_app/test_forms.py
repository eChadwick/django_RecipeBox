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
        self.assertEqual(
            name_field.widget.attrs['placeholder'],
            IngredientForm.name_field_placeholder
        )

        measurement_field = form.fields['measurement']
        self.assertIsInstance(measurement_field, CharField)
        self.assertFalse(measurement_field.required)
        self.assertEqual(measurement_field.max_length, 255)
        self.assertEqual(
            measurement_field.widget.attrs['placeholder'],
            IngredientForm.measurement_field_placeholder
        )

    def test_equality_operator(self):
        form_data = {'name': 'test name', 'measurement': 'a bit'}
        form1 = IngredientForm(form_data)
        form2 = IngredientForm(form_data)
        self.assertEqual(form1, form2)

    def test_has_error_when_name_missing_and_measurement_entered(self):
        form = IngredientForm({'measurement': 'a bit'})

        self.assertFalse(form.is_valid())
        self.assertIn(IngredientForm.name_error, form.errors['name'])


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

        name_field = form.fields['name']
        self.assertIsInstance(name_field, CharField)
        self.assertEqual(name_field.max_length, 255)
        self.assertFalse(name_field.required)
        self.assertEqual(
            name_field.widget.attrs['placeholder'],
            RecipeForm.name_field_placeholder
        )

        directions_field = form.fields['directions']
        self.assertIsInstance(directions_field, CharField)
        self.assertEqual(directions_field.max_length, 10000)
        self.assertFalse(directions_field.required)
        self.assertEqual(
            directions_field.widget.attrs['placeholder'],
            RecipeForm.directions_field_placeholder
        )

    def test_equality_operator(self):
        form_data = {'name': 'test name', 'directions': 'do stuff'}
        form1 = RecipeForm(form_data)
        form2 = RecipeForm(form_data)
        self.assertEqual(form1, form2)

    def test_form_has_error_when_name_missing(self):
        form = RecipeForm({})

        self.assertFalse(form.is_valid())
        self.assertIn(RecipeForm.name_error, form.errors['name'])
