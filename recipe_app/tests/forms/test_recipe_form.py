from django.test import TestCase
from django.forms import CharField

from recipe_app.forms.forms import RecipeForm


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
