from django.test import TestCase
from django.forms import CharField, BooleanField

from recipe_app.forms import IngredientForm


class IngredientFormTests(TestCase):
    def test_fields(self):
        form = IngredientForm()

        name_field = form.fields['name']
        self.assertIsInstance(name_field, CharField)
        self.assertFalse(name_field.required)
        self.assertEqual(name_field.max_length, 255)
        self.assertEqual('', name_field.label)
        self.assertEqual(
            name_field.widget.attrs['placeholder'],
            IngredientForm.name_field_placeholder
        )

        measurement_field = form.fields['measurement']
        self.assertIsInstance(measurement_field, CharField)
        self.assertFalse(measurement_field.required)
        self.assertEqual(measurement_field.max_length, 255)
        self.assertEqual('', measurement_field.label)
        self.assertEqual(
            measurement_field.widget.attrs['placeholder'],
            IngredientForm.measurement_field_placeholder
        )

        delete_field = form.fields['DELETE']
        self.assertIsInstance(delete_field, BooleanField)
        self.assertEqual('', delete_field.label)
        self.assertEqual(
            delete_field.widget.attrs['onclick'],
            'hideParent(this)'
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
