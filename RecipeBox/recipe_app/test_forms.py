from django.test import TestCase
from ..forms import RecipeForm

class RecipeFormTest(TestCase):

    def test_recipe_form_has_required_fields(self):
        form = RecipeForm()
        self.assertTrue('name' in form.fields)
        self.assertTrue('ingredients' in form.fields)
        self.assertTrue('directions' in form.fields)

    def test_recipe_form_with_blank_name(self):
        form_data = {'name': '', 'ingredients': 'Ingredient 1, Ingredient 2', 'directions': 'Step 1, Step 2'}
        form = RecipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'], ['Recipe name is required'])

    def test_recipe_form_with_blank_ingredients_and_directions(self):
        form_data = {'name': 'Recipe Name', 'ingredients': '', 'directions': ''}
        form = RecipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.non_field_errors(), ['Ingredients OR directions must be provided'])

    def test_recipe_form_with_invalid_ingredient_format(self):
        form_data = {
            'name': 'Recipe Name',
            'ingredients': [
                {'name': 'Ingredient 1', 'measurement': '1 cup'},
                {'name': 'Ingredient 2'},
                {'measurement': '2 cups'}
            ],
            'directions': 'Step 1, Step 2'
        }
        form = RecipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['ingredients'][1], 'Invalid ingredient format')
        self.assertEqual(form.errors['ingredients'][2], 'Invalid ingredient format')

    def test_recipe_form_with_blank_ingredient(self):
        form_data = {
            'name': 'Recipe Name',
            'ingredients': [
                {'name': 'Ingredient 1', 'measurement': '1 cup'},
                {'name': '', 'measurement': ''},
                {'name': 'Ingredient 3', 'measurement': '2 cups'}
            ],
            'directions': 'Step 1, Step 2'
        }
        form = RecipeForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.cleaned_data['ingredients']), 2)
        self.assertEqual(form.cleaned_data['ingredients'][0]['name'], 'Ingredient 1')
        self.assertEqual(form.cleaned_data['ingredients'][0]['measurement'], '1 cup')
        self.assertEqual(form.cleaned_data['ingredients'][1]['name'], 'Ingredient 3')
        self.assertEqual(form.cleaned_data['ingredients'][1]['measurement'], '2 cups')

    def test_recipe_form_with_measurement_but_no_name(self):
        form_data = {
            'name': 'Recipe Name',
            'ingredients': [
                {'name': 'Ingredient 1', 'measurement': '1 cup'},
                {'name': '', 'measurement': '2 cups'},
                {'name': 'Ingredient 3', 'measurement': '3 cups'}
            ],
            'directions': 'Step 1, Step 2'
        }
        form = RecipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['ingredients'][1], 'Ingredient name cannot be blank when measurement is entered')
