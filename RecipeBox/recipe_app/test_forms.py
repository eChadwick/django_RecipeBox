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
        self.assertEqual(formset.total_form_count(), extra_ingredient_form_count)

class RecipeFormTests(TestCase):

    def test_recipe_name_is_required(self):
        form = RecipeForm({})
        self.assertFalse(form.is_valid())
        self.assertIn(RecipeForm.name_validation_error,form.errors['name'])

