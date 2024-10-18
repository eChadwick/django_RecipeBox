from django.test import TestCase
from django.forms import CharField

from recipe_app.forms import TagCreationForm


class TagCreationFormTests(TestCase):
    def test_fields(self):
        form = TagCreationForm()
        name_field = form.fields['tag_name']
        self.assertIsInstance(name_field, CharField)
        self.assertEqual(name_field.max_length, 250)
        self.assertEqual(name_field.required, True)
