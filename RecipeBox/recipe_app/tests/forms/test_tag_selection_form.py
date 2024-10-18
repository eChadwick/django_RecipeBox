from django.test import TestCase
from django.forms import (
    CharField,
    IntegerField,
    HiddenInput,
    BooleanField
)

from recipe_app.forms import TagSelectionForm


class TagSelectionFormTests(TestCase):
    def test_fields(self):
        form = TagSelectionForm()

        name_field = form.fields['tag_name']
        self.assertIsInstance(name_field, CharField)
        self.assertEqual(name_field.max_length, 250)

        id_field = form.fields['id']
        self.assertIsInstance(id_field, IntegerField)
        self.assertIsInstance(id_field.widget, HiddenInput)

        include_field = form.fields['include']
        self.assertIsInstance(include_field, BooleanField)
        self.assertFalse(include_field.required)
