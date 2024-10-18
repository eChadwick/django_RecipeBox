from django.test import TestCase

from recipe_app.forms import IngredientInclusionFormSet, IngredientInclusionForm


class IngredientInclusionFormSetTests(TestCase):

    def test_formset_settings(self):
        formset = IngredientInclusionFormSet()

        self.assertEqual(
            formset.extra,
            0
        )

        self.assertEqual(
            formset.form,
            IngredientInclusionForm
        )
