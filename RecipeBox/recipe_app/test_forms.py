from django.forms import formset_factory
from django.test import TestCase

from recipe_app.forms import IngredientForm, RecipeForm


class IngredientFormTests(TestCase):

    def test_form_fields_exist(self):
        form = IngredientForm()
        self.assertTrue('name' in form.fields)
        self.assertTrue('measurement' in form.fields)

    def test_form_invalid_with_empty_name_and_measurement_provided(self):
        form_data = {'name': '', 'measurement': '2 cups'}
        form = IngredientForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn(
            'Ingredient name must be entered when measurement is provided', form.errors['__all__'])


class RecipeFormTest(TestCase):
    complete_recipe_data = {
            'name': 'Recipe Name',
            'ingredients': [
                {'name': 'Ingredient 1', 'measurement': '1 cup'},
                {'name': 'Ingredient 3', 'measurement': '2 cups'}
            ],
            'directions': 'Step 1, Step 2'
        }

    def test_recipe_form_with_blank_name_is_invalid(self):
        form_data = self.complete_recipe_data
        form_data.name = ''
        form = RecipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'], ['Recipe name is required'])

    def test_recipe_form_with_missing_name_is_invalid(self):
        form_data = self.complete_recipe_data
        form_data.name = None
        form = RecipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'], ['Recipe name is required'])

    def test_recipe_form_with_blank_ingredients_and_directions_is_invalid(self):
        form_data = self.complete_recipe_data
        form_data.ingredients = []
        form_data.directions = ''
        form = RecipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.non_field_errors(), [
                         'Ingredients OR directions must be provided'])

    def test_recipe_form_with_missing_ingredients_and_directions_is_invalid(self):
        form_data = self.complete_recipe_data
        form_data.ingredients = None
        form_data.directions = None
        form = RecipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.non_field_errors(), [
                         'Ingredients OR directions must be provided'])

    def test_recipe_form_ignores_blank_ingredients(self):
        form_data = self.complete_recipe_data
        form_data['ingredients'][3] = ''
        form = RecipeForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.cleaned_data['ingredients']), 2)
        self.assertEqual(
            form.cleaned_data['ingredients'][0]['name'], 'Ingredient 1')
        self.assertEqual(
            form.cleaned_data['ingredients'][0]['measurement'], '1 cup')
        self.assertEqual(
            form.cleaned_data['ingredients'][1]['name'], 'Ingredient 3')
        self.assertEqual(
            form.cleaned_data['ingredients'][1]['measurement'], '2 cups')

    def test_recipe_form_ingredients_field_is_formset(self):
        form = RecipeForm(self.complete_recipe_data)
        self.assertIsInstance(
            form.fields['ingredients'], formset_factory(IngredientForm, extra=1))

    def test_recipe_form_with_directions_and_empty_ingredients_is_valid(self):
        form_data = self.complete_recipe_data
        form_data['ingredients'] = []
        form = RecipeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_recipe_form_with_directions_and_missing_ingredients_is_valid(self):
        form_data = self.complete_recipe_data
        form_data['ingredients'] = None
        form = RecipeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_recipe_form_with_ingredients_and_empty_directions_is_valid(self):
        form_data = self.complete_recipe_data
        form_data['directions'] = ''
        form = RecipeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_recipe_form_with_ingredients_and_missing_directions_is_valid(self):
        form_data = self.complete_recipe_data
        form_data['directions'] = None
        form = RecipeForm(data=form_data)
        self.assertTrue(form.is_valid())


