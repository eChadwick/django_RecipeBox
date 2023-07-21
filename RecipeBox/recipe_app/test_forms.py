from unittest.mock import MagicMock

from django.forms import formset_factory
from django.test import TestCase

from recipe_app.forms import IngredientForm, RecipeForm, IngredientFormSet, extra_ingredient_form_count


class IngredientFormTests(TestCase):

    def test_ingredient_name_required(self):

        form = IngredientForm({})
        self.assertFalse(form.is_valid())
        self.assertIn(IngredientForm.name_validation_error,
                      form.errors['name'])


class IngredientFormsetTests(TestCase):

    def test_formset_has_one_extra(self):
        formset = IngredientFormSet()
        self.assertEqual(formset.total_form_count(),
                         extra_ingredient_form_count)


class RecipeFormTests(TestCase):

    def test_recipe_name_is_required(self):
        form = RecipeForm({})
        self.assertFalse(form.is_valid())
        self.assertIn(RecipeForm.name_validation_error, form.errors['name'])

    def test_form_instantiates_bound_formset_when_data_passed(self):
        ingredients = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-0-name': 'ingredient',
            'form-0-measurement': 'measurement',
        }
        recipe_form = RecipeForm(
            {'name': 'test name', 'ingredients': ingredients})

        self.assertTrue(recipe_form.ingredients.is_bound)
        self.assertIsInstance(recipe_form.ingredients, IngredientFormSet)
        self.assertEqual(
            recipe_form.ingredients.cleaned_data[0]['name'], ingredients['form-0-name'])
        self.assertEqual(
            recipe_form.ingredients.cleaned_data[0]['measurement'], ingredients['form-0-measurement'])

    def test_form_instantiates_unbound_formset_when_no_data_passed(self):
        form = RecipeForm()
        self.assertFalse(form.ingredients.is_bound)
        self.assertIsInstance(form.ingredients, IngredientFormSet)

    def test_form_validates_ingredients_on_clean(self):
        form = RecipeForm({})
        form.ingredients.is_valid = MagicMock()
        form.is_valid()
        form.ingredients.is_valid.assert_called()

    def test_form_invalid_when_ingredients_invalid(self):
        form = RecipeForm({})
        form.ingredients.is_valid = MagicMock(return_value=False)
        self.assertFalse(form.is_valid())
        self.assertIn(RecipeForm.ingredient_error, form.non_field_errors())
