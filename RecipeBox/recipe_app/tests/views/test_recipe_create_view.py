from unittest.mock import patch, ANY

from django.http import HttpResponse
from django.shortcuts import redirect
from django.test import TestCase
from django.urls import reverse

from recipe_app.forms.forms import (
    IngredientFormSet,
    RecipeForm,
    TagCreationFormset

)
from recipe_app.forms.tag_selection_formset import TagSelectionFormset

from recipe_app.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag
)
from recipe_app.views import (
    INGREDIENT_LIST_FORMSET_PREFIX,
    TAG_CREATE_FORMSET_PREFIX,
    TAG_SELECT_FORMSET_PREFIX
)


@patch('recipe_app.views.render', return_value=HttpResponse())
class RecipeCreateViewGetTests(TestCase):

    def test_it_renders_the_correct_html(self, mock_render):
        self.client.get(reverse('recipe-create'))
        mock_render.assert_called_with(
            ANY, 'recipe_app/recipe_form.html', ANY
        )

    def test_it_returns_correct_forms(self, mock_render):
        for x in range(5):
            Tag.objects.create(name=f'Tag{x}')

        self.client.get(reverse('recipe-create'))

        rendered_context = mock_render.call_args[0][2]

        rendered_recipe = rendered_context['recipe']
        self.assertIsInstance(rendered_recipe, RecipeForm)
        self.assertFalse(rendered_recipe.is_bound)

        rendered_ingredients_list = rendered_context['ingredients_list']
        self.assertIsInstance(rendered_ingredients_list, IngredientFormSet)
        self.assertFalse(rendered_ingredients_list.is_bound)
        self.assertEqual(
            rendered_ingredients_list.prefix,
            INGREDIENT_LIST_FORMSET_PREFIX
        )

        rendered_tag_create_form = rendered_context['tag_create']
        self.assertIsInstance(rendered_tag_create_form, TagCreationFormset)
        self.assertFalse(rendered_tag_create_form.is_bound)
        self.assertEqual(
            rendered_tag_create_form.prefix,
            TAG_CREATE_FORMSET_PREFIX
        )

        rendered_tag_select_form = rendered_context['tag_select']
        self.assertIsInstance(rendered_tag_select_form, TagSelectionFormset)
        self.assertTrue(rendered_tag_select_form.is_valid())
        self.assertEqual(len(rendered_tag_select_form.forms), 5)
        self.assertEqual(
            rendered_tag_select_form.prefix,
            TAG_SELECT_FORMSET_PREFIX
        )

    def test_it_should_pass_request_action(self, mock_render):
        self.client.get(reverse('recipe-create'))
        rendered_context = mock_render.call_args[0][2]
        self.assertEqual(rendered_context['action'], 'create')


@patch('recipe_app.views.render', return_value=HttpResponse())
class RecipeCreateViewPostTests(TestCase):

    def test_it_should_rerender_form_on_recipe_errors(self, mock_render):
        # Empty name constitues error
        form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': 'Ingredient ',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': 'Amount',
            'directions': 'Do things',
            f'{TAG_CREATE_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{TAG_CREATE_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name': 'New Tag',
            f'{TAG_SELECT_FORMSET_PREFIX}-TOTAL_FORMS': '2',
            f'{TAG_SELECT_FORMSET_PREFIX}-INITIAL_FORMS': '2',
            f'{TAG_SELECT_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{TAG_SELECT_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{TAG_SELECT_FORMSET_PREFIX}-0-tag_name': 'Tag1',
            f'{TAG_SELECT_FORMSET_PREFIX}-0-include': 'on',
            f'{TAG_SELECT_FORMSET_PREFIX}-0-id': '1',
            f'{TAG_SELECT_FORMSET_PREFIX}-1-tag_name': 'Tag2',
            f'{TAG_SELECT_FORMSET_PREFIX}-1-id': '2'
        }
        self.client.post(reverse('recipe-create'), form_data)

        rendered_template = mock_render.call_args[0][1]
        self.assertEqual(rendered_template, 'recipe_app/recipe_form.html')

        rendered_recipe = mock_render.call_args[0][2]['recipe']
        self.assertIsInstance(
            rendered_recipe,
            RecipeForm
        )
        self.assertEqual(
            rendered_recipe.data,
            {
                'name': form_data['name'],
                'directions': form_data['directions']
            }
        )

        rendered_ingredients = mock_render.call_args[0][2]['ingredients_list']
        self.assertIsInstance(
            rendered_ingredients,
            IngredientFormSet
        )
        self.assertEqual(
            rendered_ingredients.data,
            {
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement']
            }
        )

        rendered_tag_create = mock_render.call_args[0][2]['tag_create']
        self.assertIsInstance(
            rendered_tag_create,
            TagCreationFormset
        )
        self.assertEqual(
            rendered_tag_create.data,
            {
                f'{TAG_CREATE_FORMSET_PREFIX}-TOTAL_FORMS': form_data[f'{TAG_CREATE_FORMSET_PREFIX}-TOTAL_FORMS'],
                f'{TAG_CREATE_FORMSET_PREFIX}-INITIAL_FORMS': form_data[f'{TAG_CREATE_FORMSET_PREFIX}-INITIAL_FORMS'],
                f'{TAG_CREATE_FORMSET_PREFIX}-MIN_NUM_FORMS': form_data[f'{TAG_CREATE_FORMSET_PREFIX}-MIN_NUM_FORMS'],
                f'{TAG_CREATE_FORMSET_PREFIX}-MAX_NUM_FORMS': form_data[f'{TAG_CREATE_FORMSET_PREFIX}-MAX_NUM_FORMS'],
                f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name': form_data[f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name']
            }
        )

        rendered_tag_select = mock_render.call_args[0][2]['tag_select']
        self.assertIsInstance(
            rendered_tag_select,
            TagSelectionFormset
        )
        self.assertEqual(
            rendered_tag_select.data,
            {
                f'{TAG_SELECT_FORMSET_PREFIX}-TOTAL_FORMS': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-TOTAL_FORMS'],
                f'{TAG_SELECT_FORMSET_PREFIX}-INITIAL_FORMS': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-INITIAL_FORMS'],
                f'{TAG_SELECT_FORMSET_PREFIX}-MIN_NUM_FORMS': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-MIN_NUM_FORMS'],
                f'{TAG_SELECT_FORMSET_PREFIX}-MAX_NUM_FORMS': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-MAX_NUM_FORMS'],
                f'{TAG_SELECT_FORMSET_PREFIX}-0-tag_name': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-0-tag_name'],
                f'{TAG_SELECT_FORMSET_PREFIX}-0-include': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-0-include'],
                f'{TAG_SELECT_FORMSET_PREFIX}-0-id': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-0-id'],
                f'{TAG_SELECT_FORMSET_PREFIX}-1-tag_name': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-1-tag_name'],
                f'{TAG_SELECT_FORMSET_PREFIX}-1-id': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-1-id']
            }
        )

    def test_it_should_rerender_form_on_ingredient_errors(self, mock_render):
        # Empty ingredient name is error when measurement is not empty
        form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': 'Recipe Name',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': 'Amount',
            'directions': 'Do things',
            f'{TAG_CREATE_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{TAG_CREATE_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name': 'New Tag',
            f'{TAG_SELECT_FORMSET_PREFIX}-TOTAL_FORMS': '2',
            f'{TAG_SELECT_FORMSET_PREFIX}-INITIAL_FORMS': '2',
            f'{TAG_SELECT_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{TAG_SELECT_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{TAG_SELECT_FORMSET_PREFIX}-0-tag_name': 'Tag1',
            f'{TAG_SELECT_FORMSET_PREFIX}-0-include': 'on',
            f'{TAG_SELECT_FORMSET_PREFIX}-0-id': '1',
            f'{TAG_SELECT_FORMSET_PREFIX}-1-tag_name': 'Tag2',
            f'{TAG_SELECT_FORMSET_PREFIX}-1-id': '2'
        }
        self.client.post(reverse('recipe-create'), form_data)

        rendered_template = mock_render.call_args[0][1]
        self.assertEqual(rendered_template, 'recipe_app/recipe_form.html')

        rendered_recipe = mock_render.call_args[0][2]['recipe']
        self.assertIsInstance(
            rendered_recipe,
            RecipeForm
        )
        self.assertEqual(
            rendered_recipe.data,
            {
                'name': form_data['name'],
                'directions': form_data['directions']
            }
        )

        rendered_ingredients = mock_render.call_args[0][2]['ingredients_list']
        self.assertIsInstance(
            rendered_ingredients,
            IngredientFormSet
        )
        self.assertEqual(
            rendered_ingredients.data,
            {
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement']
            }
        )

        rendered_tag_create = mock_render.call_args[0][2]['tag_create']
        self.assertIsInstance(
            rendered_tag_create,
            TagCreationFormset
        )
        self.assertEqual(
            rendered_tag_create.data,
            {
                f'{TAG_CREATE_FORMSET_PREFIX}-TOTAL_FORMS': form_data[f'{TAG_CREATE_FORMSET_PREFIX}-TOTAL_FORMS'],
                f'{TAG_CREATE_FORMSET_PREFIX}-INITIAL_FORMS': form_data[f'{TAG_CREATE_FORMSET_PREFIX}-INITIAL_FORMS'],
                f'{TAG_CREATE_FORMSET_PREFIX}-MIN_NUM_FORMS': form_data[f'{TAG_CREATE_FORMSET_PREFIX}-MIN_NUM_FORMS'],
                f'{TAG_CREATE_FORMSET_PREFIX}-MAX_NUM_FORMS': form_data[f'{TAG_CREATE_FORMSET_PREFIX}-MAX_NUM_FORMS'],
                f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name': form_data[f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name']
            }
        )

        rendered_tag_select = mock_render.call_args[0][2]['tag_select']
        self.assertIsInstance(
            rendered_tag_select,
            TagSelectionFormset
        )
        self.assertEqual(
            rendered_tag_select.data,
            {
                f'{TAG_SELECT_FORMSET_PREFIX}-TOTAL_FORMS': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-TOTAL_FORMS'],
                f'{TAG_SELECT_FORMSET_PREFIX}-INITIAL_FORMS': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-INITIAL_FORMS'],
                f'{TAG_SELECT_FORMSET_PREFIX}-MIN_NUM_FORMS': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-MIN_NUM_FORMS'],
                f'{TAG_SELECT_FORMSET_PREFIX}-MAX_NUM_FORMS': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-MAX_NUM_FORMS'],
                f'{TAG_SELECT_FORMSET_PREFIX}-0-tag_name': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-0-tag_name'],
                f'{TAG_SELECT_FORMSET_PREFIX}-0-include': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-0-include'],
                f'{TAG_SELECT_FORMSET_PREFIX}-0-id': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-0-id'],
                f'{TAG_SELECT_FORMSET_PREFIX}-1-tag_name': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-1-tag_name'],
                f'{TAG_SELECT_FORMSET_PREFIX}-1-id': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-1-id']
            }
        )

    def test_recipe_form_has_error_when_no_directions_or_ingredients(self, mock_render):
        form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': 'Recipe Name',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': '',
            'directions': '',
            f'{TAG_CREATE_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{TAG_CREATE_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name': 'New Tag',
            f'{TAG_SELECT_FORMSET_PREFIX}-TOTAL_FORMS': '2',
            f'{TAG_SELECT_FORMSET_PREFIX}-INITIAL_FORMS': '2',
            f'{TAG_SELECT_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{TAG_SELECT_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{TAG_SELECT_FORMSET_PREFIX}-0-tag_name': 'Tag1',
            f'{TAG_SELECT_FORMSET_PREFIX}-0-include': 'on',
            f'{TAG_SELECT_FORMSET_PREFIX}-0-id': '1',
            f'{TAG_SELECT_FORMSET_PREFIX}-1-tag_name': 'Tag2',
            f'{TAG_SELECT_FORMSET_PREFIX}-1-id': '2'
        }
        self.client.post(reverse('recipe-create'), form_data)

        rendered_template = mock_render.call_args[0][1]
        self.assertEqual(rendered_template, 'recipe_app/recipe_form.html')

        rendered_recipe = mock_render.call_args[0][2]['recipe']
        self.assertIsInstance(
            rendered_recipe,
            RecipeForm
        )
        self.assertEqual(
            rendered_recipe.data,
            {
                'name': form_data['name'],
                'directions': form_data['directions']
            }
        )
        self.assertIn(RecipeForm.content_error, rendered_recipe.errors['name'])

        rendered_ingredients = mock_render.call_args[0][2]['ingredients_list']
        self.assertIsInstance(
            rendered_ingredients,
            IngredientFormSet
        )
        self.assertEqual(
            rendered_ingredients.data,
            {
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement']
            }
        )

        rendered_tag_create = mock_render.call_args[0][2]['tag_create']
        self.assertIsInstance(
            rendered_tag_create,
            TagCreationFormset
        )
        self.assertEqual(
            rendered_tag_create.data,
            {
                f'{TAG_CREATE_FORMSET_PREFIX}-TOTAL_FORMS': form_data[f'{TAG_CREATE_FORMSET_PREFIX}-TOTAL_FORMS'],
                f'{TAG_CREATE_FORMSET_PREFIX}-INITIAL_FORMS': form_data[f'{TAG_CREATE_FORMSET_PREFIX}-INITIAL_FORMS'],
                f'{TAG_CREATE_FORMSET_PREFIX}-MIN_NUM_FORMS': form_data[f'{TAG_CREATE_FORMSET_PREFIX}-MIN_NUM_FORMS'],
                f'{TAG_CREATE_FORMSET_PREFIX}-MAX_NUM_FORMS': form_data[f'{TAG_CREATE_FORMSET_PREFIX}-MAX_NUM_FORMS'],
                f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name': form_data[f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name']
            }
        )

        rendered_tag_select = mock_render.call_args[0][2]['tag_select']
        self.assertIsInstance(
            rendered_tag_select,
            TagSelectionFormset
        )
        self.assertEqual(
            rendered_tag_select.data,
            {
                f'{TAG_SELECT_FORMSET_PREFIX}-TOTAL_FORMS': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-TOTAL_FORMS'],
                f'{TAG_SELECT_FORMSET_PREFIX}-INITIAL_FORMS': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-INITIAL_FORMS'],
                f'{TAG_SELECT_FORMSET_PREFIX}-MIN_NUM_FORMS': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-MIN_NUM_FORMS'],
                f'{TAG_SELECT_FORMSET_PREFIX}-MAX_NUM_FORMS': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-MAX_NUM_FORMS'],
                f'{TAG_SELECT_FORMSET_PREFIX}-0-tag_name': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-0-tag_name'],
                f'{TAG_SELECT_FORMSET_PREFIX}-0-include': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-0-include'],
                f'{TAG_SELECT_FORMSET_PREFIX}-0-id': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-0-id'],
                f'{TAG_SELECT_FORMSET_PREFIX}-1-tag_name': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-1-tag_name'],
                f'{TAG_SELECT_FORMSET_PREFIX}-1-id': form_data[f'{TAG_SELECT_FORMSET_PREFIX}-1-id']
            }
        )

    @patch('recipe_app.views.redirect', wraps=redirect)
    def test_success_with_name_and_directions(self, mock_redirect, _):
        form_data = {'csrfmiddlewaretoken': 'irrelevant',
                     'name': 'oooppp',
                     f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
                     f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '0',
                     f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
                     f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
                     f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': '',
                     f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': '',
                     'directions': 'jkjk'}
        self.client.post(reverse('recipe-create'), form_data)
        mock_redirect.assert_called()

    @patch('recipe_app.views.redirect', wraps=redirect)
    def test_success_with_name_and_ingredients(self, mock_redirect, _):
        form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': 'Test name',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': 'Ingredient 1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': 'a bit',
            'directions': ''
        }
        self.client.post(reverse('recipe-create'), form_data)
        mock_redirect.assert_called()

    def test_success_ingores_empty_ingredients(self, _):
        form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': 'Test ',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '2',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': 'Delete',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': 'ignored ',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-DELETE': 'on',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-name': 'Keep this',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-measurement': 'a bit',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-2-name': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-2-measurement': '',
            'directions': ''
        }
        self.client.post(reverse('recipe-create'), form_data)

        self.assertFalse(
            RecipeIngredient.objects.filter(
                measurement=form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement']
            ).exists()
        )

        self.assertFalse(
            Ingredient.objects.filter(
                name__iexact=form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name']
            ).exists()
        )

        self.assertFalse(
            RecipeIngredient.objects.filter(
                measurement=form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-2-measurement']
            ).exists()
        )

        self.assertFalse(
            Ingredient.objects.filter(
                name__iexact=form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-2-name']
            ).exists()
        )

    @patch('recipe_app.views.redirect', wraps=redirect)
    def test_success_with_directions_and_many_ingredients(self, mock_redirect, _):
        form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': 'Another Test',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '2',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': 'first ingredient',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': 'a bit',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-name': 'second ingredient',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-measurement': 'a bunch',
            'directions': 'Do stuff'
        }

        self.client.post(reverse('recipe-create'), form_data)

        recipe = Recipe.objects.filter(name__iexact=form_data['name'])
        self.assertTrue(recipe)
        self.assertEqual(recipe[0].name, form_data['name'])
        self.assertEqual(recipe[0].directions, form_data['directions'])

        ingredient0 = Ingredient.objects.filter(
            name__iexact=form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name'])
        self.assertTrue(ingredient0)

        ingredient1 = Ingredient.objects.filter(
            name__iexact=form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-name'])
        self.assertTrue(ingredient1)

        self.assertTrue(RecipeIngredient.objects.filter(
            recipe=recipe[0],
            ingredient=ingredient0[0],
            measurement=form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement']).exists()
        )

        self.assertTrue(RecipeIngredient.objects.filter(
            recipe=recipe[0],
            ingredient=ingredient1[0],
            measurement=form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-measurement']).exists()
        )

        mock_redirect.assert_called_with(
            reverse('recipe-detail', args=[recipe[0].pk]))

    @patch('recipe_app.views.redirect', wraps=redirect)
    def test_success_with_tag_create(self, mock_redirect, _):
        form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': 'Oooppp',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': '',
            'directions': 'jkjk',
            f'{TAG_CREATE_FORMSET_PREFIX}-TOTAL_FORMS': '2',
            f'{TAG_CREATE_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name': 'New Tag',
            f'{TAG_CREATE_FORMSET_PREFIX}-1-tag_name': 'Other New Tag'
        }

        self.client.post(reverse('recipe-create'), form_data)

        recipe = Recipe.objects.filter(name__iexact=form_data['name'])
        self.assertTrue(recipe)
        self.assertEqual(recipe[0].name, form_data['name'])
        self.assertEqual(recipe[0].directions, form_data['directions'])

        recipe_tags = recipe[0].tags.all()
        self.assertEqual(len(recipe_tags), 2)
        self.assertEqual(
            recipe_tags[0].name,
            form_data[f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name']
        )
        self.assertEqual(
            recipe_tags[1].name,
            form_data[f'{TAG_CREATE_FORMSET_PREFIX}-1-tag_name']
        )

        mock_redirect.assert_called_with(
            reverse('recipe-detail', args=[recipe[0].pk]))

    @patch('recipe_app.views.redirect', wraps=redirect)
    def test_success_with_empty_tag_create_form(self, mock_redirect, _):
        form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': 'Oooppp',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': '',
            'directions': 'jkjk',
            f'{TAG_CREATE_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{TAG_CREATE_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name': '',
        }

        self.client.post(reverse('recipe-create'), form_data)

        recipe = Recipe.objects.filter(name__iexact=form_data['name'])
        self.assertTrue(recipe)
        self.assertEqual(recipe[0].name, form_data['name'])
        self.assertEqual(recipe[0].directions, form_data['directions'])

        mock_redirect.assert_called_with(
            reverse('recipe-detail', args=[recipe[0].pk]))

    @patch('recipe_app.views.redirect', wraps=redirect)
    def test_success_with_empty_tag_select_form(self, mock_redirect, _):
        form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': 'Oooppp',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': '',
            'directions': 'jkjk',
            f'{TAG_SELECT_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{TAG_SELECT_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{TAG_SELECT_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{TAG_SELECT_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{TAG_SELECT_FORMSET_PREFIX}-0-tag_name': '',
            f'{TAG_SELECT_FORMSET_PREFIX}-0-id': '',
        }

        self.client.post(reverse('recipe-create'), form_data)

        recipe = Recipe.objects.filter(name__iexact=form_data['name'])
        self.assertTrue(recipe)
        self.assertEqual(recipe[0].name, form_data['name'])
        self.assertEqual(recipe[0].directions, form_data['directions'])

        mock_redirect.assert_called_with(
            reverse('recipe-detail', args=[recipe[0].pk]))

    def test_success_with_tag_select(self, _):
        Tag1 = Tag.objects.create(name='Tag1')
        Tag2 = Tag.objects.create(name='Tag2')

        form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': 'Oooppp',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': '',
            'directions': 'jkjk',
            f'{TAG_SELECT_FORMSET_PREFIX}-TOTAL_FORMS': '2',
            f'{TAG_SELECT_FORMSET_PREFIX}-INITIAL_FORMS': '2',
            f'{TAG_SELECT_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{TAG_SELECT_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{TAG_SELECT_FORMSET_PREFIX}-0-tag_name': Tag1.name,
            f'{TAG_SELECT_FORMSET_PREFIX}-0-include': 'on',
            f'{TAG_SELECT_FORMSET_PREFIX}-0-id': Tag1.id,
            f'{TAG_SELECT_FORMSET_PREFIX}-1-tag_name': Tag2.name,
            f'{TAG_SELECT_FORMSET_PREFIX}-1-id': Tag2.id
        }

        self.client.post(reverse('recipe-create'), form_data)

        recipe = Recipe.objects.filter(name__iexact=form_data['name'])
        self.assertTrue(recipe)

        recipe_tags = recipe[0].tags.all()
        self.assertEqual(
            len(recipe_tags),
            1
        )
        self.assertEqual(
            recipe_tags[0].name,
            form_data[f'{TAG_SELECT_FORMSET_PREFIX}-0-tag_name']
        )
