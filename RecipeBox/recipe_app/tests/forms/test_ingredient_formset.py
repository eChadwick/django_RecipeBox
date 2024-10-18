from django.test import TestCase

from unittest.mock import patch

from recipe_app.forms import IngredientFormSet, extra_ingredient_form_count


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
        formset = IngredientFormSet({
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-name': '',
            'form-0-measurement': '',
            'form-1-name': 'deleted',
            'form-1-DELETE': 'on'
        })
        self.assertTrue(formset.is_empty())
