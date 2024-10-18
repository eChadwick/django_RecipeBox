from unittest.mock import patch, ANY

from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse

from recipe_app.forms.forms import (
    IngredientInclusionFormSet,
    RecipeInclusionForm,
)
from recipe_app.models import (
    Ingredient,
    Recipe,
    RecipeIngredient
)
from recipe_app.views import (
    RECIPE_NOT_FOUND_ERROR,
    TAG_CREATE_FORMSET_PREFIX,
    TAG_SELECT_FORMSET_PREFIX,
    INGREDIENT_LIST_FORMSET_PREFIX
)


@patch('recipe_app.views.render', return_value=HttpResponse())
class RecipeSearchViewTests(TestCase):

    def setUp(self):
        for i in range(1, 6):
            Ingredient.objects.create(name=f'Ingredient {i}')

    def test_get_renders_correct_template(self, mock_render):
        self.client.get(reverse('recipe-search'))

        mock_render.assert_called_with(
            ANY, 'recipe_app/recipe_search.html', ANY
        )

    def test_get_returns_all_elements(self, mock_render):
        self.client.get(reverse('recipe-search'))

        ingredients_list = mock_render.call_args[0][2]['ingredients']
        self.assertIsInstance(ingredients_list, IngredientInclusionFormSet)
        self.assertEqual(len(ingredients_list), 5)
        for i in range(1, 6):
            self.assertIn(
                {
                    'id': i,
                    'name': f'Ingredient {i}'
                },
                ingredients_list.initial
            )

        recipe_name = mock_render.call_args[0][2]['recipe_name']
        self.assertIsInstance(recipe_name, RecipeInclusionForm)

    def test_post_renders_correct_template(self, mock_render):
        post_data = {
            'form-TOTAL_FORMS': '0',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
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
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'csrfmiddlewaretoken': 'irrelevant',
            'form-0-name': ingredient.name,
            'form-0-inclusion': 'neutral',
            'form-0-id': ingredient.pk
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
            'form-TOTAL_FORMS': '3',
            'form-INITIAL_FORMS': '3',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'csrfmiddlewaretoken': 'irrelevant',
            'form-0-name': exclude_ingredient_1.name,
            'form-0-inclusion': 'exclude',
            'form-0-id': exclude_ingredient_1.pk,
            'form-1-name': exclude_ingredient_2.name,
            'form-1-inclusion': 'exclude',
            'form-1-id': exclude_ingredient_2.pk,
            'form-2-name': neutral_ingredient.name,
            'form-2-inclusion': 'neutral',
            'form-2-id': neutral_ingredient.pk
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
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'csrfmiddlewaretoken': 'irrelevant',
            'form-0-name': ingredient_1.name,
            'form-0-inclusion': 'or',
            'form-0-id': ingredient_1.pk,
            'form-1-name': ingredient_2.name,
            'form-1-inclusion': 'or',
            'form-1-id': ingredient_2.pk
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
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'csrfmiddlewaretoken': 'irrelevant',
            'form-0-name': ingredient_1.name,
            'form-0-inclusion': 'and',
            'form-0-id': ingredient_1.pk,
            'form-1-name': ingredient_2.name,
            'form-1-inclusion': 'and',
            'form-1-id': ingredient_2.pk
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
            'form-TOTAL_FORMS': '0',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
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
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'csrfmiddlewaretoken': 'irrelevant',
            'form-0-name': ingredient_1.name,
            'form-0-inclusion': 'or',
            'form-0-id': ingredient_1.pk,
            'form-1-name': ingredient_2.name,
            'form-1-inclusion': 'or',
            'form-1-id': ingredient_2.pk
        }

        self.client.post(reverse('recipe-search'), post_data)

        rendered_recipe_list = mock_render.call_args[0][2]['recipes_list']
        self.assertEqual(len(rendered_recipe_list), 1)
        self.assertIn(recipe, rendered_recipe_list)
