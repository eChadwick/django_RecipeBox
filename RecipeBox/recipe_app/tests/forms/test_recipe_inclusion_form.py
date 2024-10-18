from django.test import TestCase
from django.forms import CharField

from recipe_app.forms import RecipeInclusionForm


class RecipeInclusionFormTests(TestCase):
    def test_fields(self):
        form = RecipeInclusionForm()
        name_field = form.fields['recipe_name']
        self.assertIsInstance(name_field, CharField)
        self.assertEqual(name_field.max_length, 10000)
        self.assertEqual(name_field.required, False)
