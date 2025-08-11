from unittest.mock import patch, ANY

from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse

from recipe_app.forms.forms import (
    IngredientInclusionFormSet,
    RecipeInclusionForm
)
from recipe_app.forms.tag_selection_formset import TagSelectionFormset
from recipe_app.models import (
    Ingredient,
    Recipe,
    RecipeIngredient
)
from recipe_app.views import (
    INGREDIENT_LIST_FORMSET_PREFIX,
    TAG_SELECT_FORMSET_PREFIX
)


@patch('recipe_app.views.render', return_value=HttpResponse())
class RecipeSearchViewGetTests(TestCase):

    def test_get_renders_correct_template(self, mock_render):
        self.client.get(reverse('recipe-search'))

        mock_render.assert_called_with(
            ANY, 'recipe_app/recipe_search.html', ANY
        )

    def test_get_returns_all_elements(self, mock_render):
        for i in range(1, 3):
            Ingredient.objects.create(name=f'Ingredient {i}')

        self.client.get(reverse('recipe-search'))

        ingredients_list = mock_render.call_args[0][2]['ingredients']
        self.assertIsInstance(ingredients_list, IngredientInclusionFormSet)
        self.assertEqual(ingredients_list.prefix,
                         INGREDIENT_LIST_FORMSET_PREFIX)
        self.assertEqual(len(ingredients_list), 2)
        for i in range(1, 3):
            self.assertIn(
                {
                    'id': i,
                    'name': f'Ingredient {i}'
                },
                ingredients_list.initial
            )

        recipe_name = mock_render.call_args[0][2]['recipe_name']
        self.assertIsInstance(recipe_name, RecipeInclusionForm)

        tag_select_form = mock_render.call_args[0][2]['tag_select']
        self.assertIsInstance(tag_select_form, TagSelectionFormset)
        self.assertEqual(tag_select_form.prefix, TAG_SELECT_FORMSET_PREFIX)
        self.assertNotIn('on', tag_select_form.data.values())

    def test_get_returns_ingredients_alphabetized(self, mock_render):
        Ingredient.objects.create(name = 'Ingredient B')
        Ingredient.objects.create(name = 'Ingredient A')
        Ingredient.objects.create(name = 'Ingredient C')

        self.client.get(reverse('recipe-search'))
        ingredients_list = mock_render.call_args[0][2]['ingredients']
        ingredient_names = [ ingredient['name'].value() for ingredient in ingredients_list.forms]   
        self.assertEqual(ingredient_names, sorted(ingredient_names))


@patch('recipe_app.views.render', return_value=HttpResponse())
class RecipeSearchViewPostTests(TestCase):

    def test_post_renders_correct_template(self, mock_render):
        post_data = {
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            'csrfmiddlewaretoken': 'irrelevant'
        }
        self.client.post(reverse('recipe-search'), post_data)

        mock_render.assert_called_with(
            ANY, 'recipe_app/recipe_list.html', ANY
        )

    def test_post_handles_neutral_inclusion(self, mock_render):
        recipe_no_ingredients = Recipe.objects.create(
            name='No ingredients', directions='things')

        ingredient = Ingredient.objects.create(name='Ingredient 1')
        recipe_with_ingredients = Recipe.objects.create(
            name='Yes ingredients', directions='stuff')
        RecipeIngredient.objects.create(
            recipe=recipe_with_ingredients,
            ingredient=ingredient
        )

        post_data = {
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            'csrfmiddlewaretoken': 'irrelevant',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': ingredient.name,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-inclusion': 'neutral',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-id': ingredient.pk
        }
        self.client.post(reverse('recipe-search'), post_data)

        rendered_recipe_list = mock_render.call_args[0][2]['recipes_list']
        self.assertEqual(len(rendered_recipe_list), 2)
        self.assertIn(recipe_no_ingredients, rendered_recipe_list)
        self.assertIn(recipe_with_ingredients, rendered_recipe_list)

    def test_excludes(self, mock_render):
        exclude_ingredient_1 = Ingredient.objects.create(
            name='Exclude Ingredient 1')
        exclude_recipe_1 = Recipe.objects.create(name='Exclude Recipe 1')
        RecipeIngredient.objects.create(
            recipe=exclude_recipe_1,
            ingredient=exclude_ingredient_1
        )

        exclude_ingredient_2 = Ingredient.objects.create(
            name='Exclude Ingredient 2')
        exclude_recipe_2 = Recipe.objects.create(name='Exclude Recipe 2')
        RecipeIngredient.objects.create(
            recipe=exclude_recipe_2,
            ingredient=exclude_ingredient_2
        )

        neutral_ingredient = Ingredient.objects.create(
            name='Neutral Ingredient')
        neutral_recipe = Recipe.objects.create(name='Neutral Recipe')

        post_data = {
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '3',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '3',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            'csrfmiddlewaretoken': 'irrelevant',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': exclude_ingredient_1.name,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-inclusion': 'exclude',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-id': exclude_ingredient_1.pk,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-name': exclude_ingredient_2.name,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-inclusion': 'exclude',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-id': exclude_ingredient_2.pk,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-2-name': neutral_ingredient.name,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-2-inclusion': 'neutral',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-2-id': neutral_ingredient.pk
        }

        self.client.post(reverse('recipe-search'), post_data)

        rendered_recipe_list = mock_render.call_args[0][2]['recipes_list']
        self.assertEqual(len(rendered_recipe_list), 1)
        self.assertIn(neutral_recipe, rendered_recipe_list)
        self.assertNotIn(exclude_recipe_1, rendered_recipe_list)
        self.assertNotIn(exclude_recipe_2, rendered_recipe_list)

    def test_or_includes(self, mock_render):
        ingredient_1 = Ingredient.objects.create(name='Ingredient 1')
        ingredient_2 = Ingredient.objects.create(name='Ingredient 2')

        include_recipe_1 = Recipe.objects.create(
            name='Include Recipe 1'
        )
        RecipeIngredient.objects.create(
            recipe=include_recipe_1,
            ingredient=ingredient_1
        )

        include_recipe_2 = Recipe.objects.create(
            name='Include Recipe 2'
        )
        RecipeIngredient.objects.create(
            recipe=include_recipe_2,
            ingredient=ingredient_2
        )

        exclude_recipe = Recipe.objects.create(
            name='Exclude Recipe'
        )

        post_data = {
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '2',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '2',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            'csrfmiddlewaretoken': 'irrelevant',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': ingredient_1.name,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-inclusion': 'or',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-id': ingredient_1.pk,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-name': ingredient_2.name,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-inclusion': 'or',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-id': ingredient_2.pk
        }

        self.client.post(reverse('recipe-search'), post_data)

        rendered_recipe_list = mock_render.call_args[0][2]['recipes_list']
        self.assertEqual(len(rendered_recipe_list), 2)
        self.assertIn(include_recipe_1, rendered_recipe_list)
        self.assertIn(include_recipe_2, rendered_recipe_list)
        self.assertNotIn(exclude_recipe, rendered_recipe_list)

    def test_and_includes(self, mock_render):
        ingredient_1 = Ingredient.objects.create(name='Ingredient 1')
        ingredient_2 = Ingredient.objects.create(name='Ingredient 2')

        include_recipe = Recipe.objects.create(
            name='Include Recipe'
        )
        RecipeIngredient.objects.create(
            recipe=include_recipe,
            ingredient=ingredient_1
        )
        RecipeIngredient.objects.create(
            recipe=include_recipe,
            ingredient=ingredient_2
        )

        exclude_recipe_1 = Recipe.objects.create(
            name='Exclude Recipe 1'
        )
        RecipeIngredient.objects.create(
            recipe=exclude_recipe_1,
            ingredient=ingredient_1
        )

        exclude_recipe_2 = Recipe.objects.create(
            name='Exclude Recipe 2'
        )

        post_data = {
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '2',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '2',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            'csrfmiddlewaretoken': 'irrelevant',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': ingredient_1.name,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-inclusion': 'and',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-id': ingredient_1.pk,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-name': ingredient_2.name,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-inclusion': 'and',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-id': ingredient_2.pk
        }

        self.client.post(reverse('recipe-search'), post_data)

        rendered_recipe_list = mock_render.call_args[0][2]['recipes_list']
        self.assertEqual(len(rendered_recipe_list), 1)
        self.assertIn(include_recipe, rendered_recipe_list)
        self.assertNotIn(exclude_recipe_1, rendered_recipe_list)
        self.assertNotIn(exclude_recipe_2, rendered_recipe_list)

    def test_recipe_name_handling(self, mock_render):
        include_recipe_1 = Recipe.objects.create(
            name='Chicken 1', directions='do stuff')
        include_recipe_2 = Recipe.objects.create(
            name='Chicken 2', directions='do other stuff')
        exclude_recipe = Recipe.objects.create(
            name='Beef', directions='dont do stuff')

        post_data = {
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            'csrfmiddlewaretoken': 'irrelevant',
            'recipe_name': 'Chicken'
        }
        self.client.post(reverse('recipe-search'), post_data)

        rendered_recipe_list = mock_render.call_args[0][2]['recipes_list']
        self.assertEqual(len(rendered_recipe_list), 2)
        self.assertIn(include_recipe_1, rendered_recipe_list)
        self.assertIn(include_recipe_2, rendered_recipe_list)
        self.assertNotIn(exclude_recipe, rendered_recipe_list)

    def test_or_includes_are_distinct(self, mock_render):
        ingredient_1 = Ingredient.objects.create(name='Ingredient 1')
        ingredient_2 = Ingredient.objects.create(name='Ingredient 2')

        recipe = Recipe.objects.create(
            name='Recipe Name'
        )
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient_1
        )
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient_2
        )

        post_data = {
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '2',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '2',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            'csrfmiddlewaretoken': 'irrelevant',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': ingredient_1.name,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-inclusion': 'or',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-id': ingredient_1.pk,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-name': ingredient_2.name,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-inclusion': 'or',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-id': ingredient_2.pk
        }

        self.client.post(reverse('recipe-search'), post_data)

        rendered_recipe_list = mock_render.call_args[0][2]['recipes_list']
        self.assertEqual(len(rendered_recipe_list), 1)
        self.assertIn(recipe, rendered_recipe_list)

    def test_tag_filtering(self, mock_render):
        recipe1 = Recipe.objects.create(name='Recipe1', directions='a')
        recipe1.tags.create(name='Tag1')

        recipe2 = Recipe.objects.create(name='Recipe2', directions='b')
        recipe2.tags.create(name='Tag2')

        recipe3 = Recipe.objects.create(name='Recipe3', directions='c')
        recipe3.tags.add(recipe1.tags.all()[0])
        recipe3.tags.add(recipe2.tags.all()[0])

        post_data = {
            'recipe_name': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{TAG_SELECT_FORMSET_PREFIX}-TOTAL_FORMS': '2',
            f'{TAG_SELECT_FORMSET_PREFIX}-INITIAL_FORMS': '2',
            f'{TAG_SELECT_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{TAG_SELECT_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            'csrfmiddlewaretoken': 'irrelevant',
            f'{TAG_SELECT_FORMSET_PREFIX}-0-tag_name': 'Tag1',
            f'{TAG_SELECT_FORMSET_PREFIX}-0-include': 'on',
            f'{TAG_SELECT_FORMSET_PREFIX}-0-id': '1',
            f'{TAG_SELECT_FORMSET_PREFIX}-1-tag_name': 'Tag2',
            f'{TAG_SELECT_FORMSET_PREFIX}-1-include': 'on',
            f'{TAG_SELECT_FORMSET_PREFIX}-1-id': '2'
        }

        self.client.post(reverse('recipe-search'), post_data)

        rendered_recipe_list = mock_render.call_args[0][2]['recipes_list']
        self.assertEqual(len(rendered_recipe_list), 1)
        self.assertIn(recipe3, rendered_recipe_list)

    def test_search_empty_ingredients_table_doesnt_error(self, mock_render):
        self.client.post(reverse('recipe-search'))
        self.assertTrue(True) # If we got here the test passed

    def test_result_ordering(self, mock_render):
        Recipe.objects.create(name = 'Recipe B', directions='jfkj')
        Recipe.objects.create(name = 'Recipe C', directions='jfkj')
        Recipe.objects.create(name = 'Recipe A', directions='jfkj')

        post_data = {
            'recipe_name': '',
            'ingredient-form-TOTAL_FORMS': '0', 
            'ingredient-form-INITIAL_FORMS': '0', 
            'ingredient-form-MIN_NUM_FORMS': '0', 
            'ingredient-form-MAX_NUM_FORMS': '1000', 
            'tag-select-form-TOTAL_FORMS': '0', 
            'tag-select-form-INITIAL_FORMS': '0', 
            'tag-select-form-MIN_NUM_FORMS': '', 
            'tag-select-form-MAX_NUM_FORMS': '', 
            'csrfmiddlewaretoken': 'irrelevant'}
        
        self.client.post(reverse('recipe-search'), post_data)
        rendered_recipe_list = mock_render.call_args[0][2]['recipes_list']
        rendered_recipe_names = [recipe.name for recipe in rendered_recipe_list]

        self.assertTrue(rendered_recipe_names == sorted(rendered_recipe_names))
