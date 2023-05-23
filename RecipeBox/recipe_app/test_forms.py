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


# class RecipeFormTest(TestCase):
#     complete_recipe_data = {
#         'name': 'Recipe Name',
#         'ingredients': [
#                 {'name': 'Ingredient 1', 'measurement': '1 cup'},
#                 {'name': 'Ingredient 3', 'measurement': '2 cups'}
#         ],
#         'directions': 'Step 1, Step 2'
#     }

#     def test_recipe_form_with_blank_name_is_invalid(self):
#         form_data = self.complete_recipe_data
#         form_data['name'] = ''
#         form = RecipeForm(data=form_data)
#         self.assertFalse(form.is_valid())
#         self.assertEqual(form.errors['name'], ['Recipe name is required'])

#     def test_recipe_form_with_missing_name_is_invalid(self):
#         form_data = self.complete_recipe_data
#         form_data['name'] = None
#         form = RecipeForm(data=form_data)
#         self.assertFalse(form.is_valid())
#         self.assertEqual(form.errors['name'], ['Recipe name is required'])

#     def test_recipe_form_ingredients_field_is_formset_when_provided(self):
#         form = RecipeForm(self.complete_recipe_data)
#         self.assertTrue(form.is_valid())
#         self.assertIsInstance(
#             form.cleaned_data['ingredients'], IngredientFormSet)

#     def test_recipe_form_includes_directions_when_provided(self):
#         form = RecipeForm(self.complete_recipe_data)
#         self.assertTrue(form.is_valid())
#         self.assertTrue('directions' in form.cleaned_data)


#     # def test_recipe_must_have_ingredients_or_directions(self):
#     #     def create_and_validate(form_data):
#     #         form = RecipeForm(data=form_data)
#     #         self.assertFalse(form.is_valid())
#     #         self.assertIn('Ingredrients or Directions must be provided',form.non_field_errors())

#     #     form_data = self.complete_recipe_data
#     #     # directions None, ingredients None
#     #     form_data['directions'] = None
#     #     form_data['ingredients'] = None
#     #     create_and_validate(form_data)

#     #     # directions None, ingredients blank
#     #     form_data['ingredients'] = ''
#     #     create_and_validate(form_data)

#     #     # directions blank, ingredients blank
#     #     form_data['directions'] = ''
#     #     create_and_validate(form_data)

#     #     # directions blank, ingredients none
#     #     form_data['ingredients'] = None
#     #     create_and_validate(form_data)


# def test_recipe_form_with_blank_ingredients_and_directions_is_invalid(self):
#     form_data = self.complete_recipe_data
#     form_data.ingredients = []
#     form_data.directions = ''
#     form = RecipeForm(data=form_data)
#     self.assertFalse(form.is_valid())
#     self.assertEqual(form.non_field_errors(), [
#                      'Ingredients OR directions must be provided'])

# def test_recipe_form_with_missing_ingredients_and_directions_is_invalid(self):
#     form_data = self.complete_recipe_data
#     form_data.ingredients = None
#     form_data.directions = None
#     form = RecipeForm(data=form_data)
#     self.assertFalse(form.is_valid())
#     self.assertEqual(form.non_field_errors(), [
#                      'Ingredients OR directions must be provided'])

# def test_recipe_form_ignores_blank_ingredients(self):
#     form_data = self.complete_recipe_data
#     form_data['ingredients'][3] = ''
#     form = RecipeForm(data=form_data)
#     self.assertTrue(form.is_valid())
#     self.assertEqual(len(form.cleaned_data['ingredients']), 2)
#     self.assertEqual(
#         form.cleaned_data['ingredients'][0]['name'], 'Ingredient 1')
#     self.assertEqual(
#         form.cleaned_data['ingredients'][0]['measurement'], '1 cup')
#     self.assertEqual(
#         form.cleaned_data['ingredients'][1]['name'], 'Ingredient 3')
#     self.assertEqual(
#         form.cleaned_data['ingredients'][1]['measurement'], '2 cups')

# def test_recipe_form_with_directions_and_empty_ingredients_is_valid(self):
#     form_data = self.complete_recipe_data
#     form_data['ingredients'] = []
#     form = RecipeForm(data=form_data)
#     self.assertTrue(form.is_valid())

# def test_recipe_form_with_directions_and_missing_ingredients_is_valid(self):
#     form_data = self.complete_recipe_data
#     form_data['ingredients'] = None
#     form = RecipeForm(data=form_data)
#     self.assertTrue(form.is_valid())

# def test_recipe_form_with_ingredients_and_empty_directions_is_valid(self):
#     form_data = self.complete_recipe_data
#     form_data['directions'] = ''
#     form = RecipeForm(data=form_data)
#     self.assertTrue(form.is_valid())

# def test_recipe_form_with_ingredients_and_missing_directions_is_valid(self):
#     form_data = self.complete_recipe_data
#     form_data['directions'] = None
#     form = RecipeForm(data=form_data)
#     self.assertTrue(form.is_valid())
