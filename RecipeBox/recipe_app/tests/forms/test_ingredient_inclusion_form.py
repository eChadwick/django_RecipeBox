from django.test import TestCase
from django.forms import (
    CharField,
    TextInput,
    IntegerField,
    HiddenInput,
    ChoiceField,
    RadioSelect
)


from recipe_app.forms import IngredientInclusionForm


class IngredientInclusionFormTests(TestCase):

    def test_form_fields(self):
        form = IngredientInclusionForm()

        name_field = form.fields['name']
        self.assertIsInstance(name_field, CharField)
        self.assertEqual(name_field.max_length, 255)
        self.assertEqual(name_field.label, '')

        name_field_widget = name_field.widget
        self.assertIsInstance(name_field_widget, TextInput)
        self.assertEqual(
            name_field_widget.attrs['readonly'],
            'readonly'
        )

        id_field = form.fields['id']
        self.assertIsInstance(id_field, IntegerField)
        self.assertIsInstance(id_field.widget, HiddenInput)

        inclusion_field = form.fields['inclusion']
        self.assertIsInstance(inclusion_field, ChoiceField)
        self.assertEqual(
            inclusion_field.choices,
            IngredientInclusionForm.radio_button_options
        )
        self.assertEqual(
            inclusion_field.initial,
            IngredientInclusionForm.default_inclusion_option
        )
        self.assertIsInstance(
            inclusion_field.widget,
            RadioSelect
        )
        self.assertEqual(
            inclusion_field.label,
            ''
        )
