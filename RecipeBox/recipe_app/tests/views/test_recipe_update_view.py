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
    RECIPE_NOT_FOUND_ERROR,
    INGREDIENT_LIST_FORMSET_PREFIX,
    TAG_CREATE_FORMSET_PREFIX,
    TAG_SELECT_FORMSET_PREFIX
)


@patch('recipe_app.views.render', return_value=HttpResponse())
class RecipeUpdateViewTests(TestCase):

    def test_get_renders_the_correct_html(self, mock_render):
        recipe = Recipe.objects.create(
            name='Test Recipe 1',
            directions='Test Directions'
        )
        self.client.get(reverse('recipe-update', args=[recipe.pk]))
        mock_render.assert_called_with(
            ANY, 'recipe_app/recipe_form.html', ANY
        )

    def test_get_passes_request_action(self, mock_render):
        recipe = Recipe.objects.create(
            name='Test Recipe 1',
            directions='Test Directions'
        )
        self.client.get(reverse('recipe-update', args=[recipe.pk]))
        rendered_context = mock_render.call_args[0][2]
        self.assertEqual(rendered_context['action'], 'update')

    def test_get_passes_recipe_pk(self, mock_render):
        recipe = Recipe.objects.create(
            name='Test Recipe 1',
            directions='Test Directions'
        )
        self.client.get(reverse('recipe-update', args=[recipe.pk]))
        rendered_context = mock_render.call_args[0][2]
        self.assertEqual(rendered_context['recipe_pk'], recipe.pk)

    def test_get_fetches_right_form(self, mock_render):
        ingredient = Ingredient.objects.create(name='Test Ingredient')
        recipe = Recipe.objects.create(
            name='Test Recipe 1',
            directions='Test Directions'
        )
        recipe.tags.add(Tag.objects.get_or_create(name='Tag1')[0])
        unincluded_tag = Tag.objects.create(name='Tag2')
        recipe_ingredient = RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            measurement='a bunch'
        )

        self.client.get(reverse('recipe-update', args=[recipe.pk]))

        rendered_recipe = mock_render.call_args[0][2]['recipe']
        self.assertEqual(
            rendered_recipe.data,
            {'name': recipe.name, 'directions': recipe.directions}
        )

        rendered_ingredients_list = mock_render.call_args[0][2]['ingredients_list']
        self.assertIsInstance(rendered_ingredients_list, IngredientFormSet)
        self.assertEqual(
            rendered_ingredients_list.prefix,
            INGREDIENT_LIST_FORMSET_PREFIX
        )
        self.assertEqual(
            rendered_ingredients_list.data,
            {
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '1',
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': ingredient.name,
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': recipe_ingredient.measurement
            }
        )

        rendered_tag_create = mock_render.call_args[0][2]['tag_create']
        self.assertIsInstance(rendered_tag_create, TagCreationFormset)
        self.assertEqual(
            rendered_tag_create.prefix,
            TAG_CREATE_FORMSET_PREFIX
        )

        rendered_tag_select = mock_render.call_args[0][2]['tag_select']
        self.assertIsInstance(rendered_tag_select, TagSelectionFormset)
        self.assertEqual(
            rendered_tag_select.prefix,
            TAG_SELECT_FORMSET_PREFIX
        )
        self.assertEqual(
            rendered_tag_select.data,
            {
                'tag-select-form-TOTAL_FORMS': '2',
                'tag-select-form-INITIAL_FORMS': '2',
                'tag-select-form-MIN_NUM_FORMS': '',
                'tag-select-form-MAX_NUM_FORMS': '',
                'tag-select-form-0-tag_name': recipe.tags.all()[0].name,
                'tag-select-form-0-id': str(recipe.tags.all()[0].id),
                'tag-select-form-0-include': True,
                'tag-select-form-1-tag_name': unincluded_tag.name,
                'tag-select-form-1-id': str(unincluded_tag.id)
            }
        )

    def test_post_should_rerender_form_on_recipe_errors(self, mock_render):
        recipe = Recipe.objects.create(
            name='Test Recipe 1',
            directions='Test Directions'
        )

        # Empty recipe name is error
        form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': 'Ingredient',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': 'Amount',
            'directions': 'Do things',
            f'{TAG_CREATE_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{TAG_CREATE_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name': 'New Tag'
        }
        self.client.post(
            reverse('recipe-update', args=[recipe.pk]), form_data)

        rendered_template = mock_render.call_args[0][1]
        self.assertEqual(rendered_template, 'recipe_app/recipe_form.html')

        rendered_recipe = mock_render.call_args[0][2]['recipe']
        self.assertEqual(
            rendered_recipe.data,
            {'name': form_data['name'], 'directions': form_data['directions']}
        )

        rendered_ingredients = mock_render.call_args[0][2]['ingredients_list']
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

    def test_post_should_rerender_form_on_ingredient_errors(self, mock_render):
        recipe = Recipe.objects.create(
            name='Test Recipe 1',
            directions='Test Directions'
        )

        form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': 'Recipe Name',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': 'Amount',
            'directions': 'Do things',
            f'{TAG_CREATE_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{TAG_CREATE_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name': 'New Tag'
        }
        self.client.post(
            reverse('recipe-update', args=[recipe.pk]), form_data)

        rendered_template = mock_render.call_args[0][1]
        self.assertEqual(rendered_template, 'recipe_app/recipe_form.html')

        rendered_recipe = mock_render.call_args[0][2]['recipe']
        self.assertEqual(
            rendered_recipe.data,
            {'name': form_data['name'], 'directions': form_data['directions']}
        )

        rendered_ingredients = mock_render.call_args[0][2]['ingredients_list']
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

    def test_recipe_form_has_error_when_no_directions_or_ingredients(self, mock_render):
        recipe = Recipe.objects.create(
            name='Test Recipe 1',
            directions='Test Directions'
        )

        form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': 'Test Recipe',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '2',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': 'Test Ingredient',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': 'a bunch',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-DELETE': 'on',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-name': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-measurement': '',
            'directions': '',
            f'{TAG_CREATE_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{TAG_CREATE_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name': 'New Tag'
        }

        self.client.post(
            reverse('recipe-update', args=[recipe.pk]), form_data)

        rendered_template = mock_render.call_args[0][1]
        self.assertEqual(rendered_template, 'recipe_app/recipe_form.html')

        rendered_recipe = mock_render.call_args[0][2]['recipe']
        self.assertEqual(
            rendered_recipe.data,
            {'name': form_data['name'], 'directions': form_data['directions']}
        )
        self.assertIn(RecipeForm.content_error, rendered_recipe.errors['name'])

        rendered_ingredients = mock_render.call_args[0][2]['ingredients_list']
        self.assertEqual(
            rendered_ingredients.data,
            {
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-DELETE': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-DELETE'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-name': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-name'],
                f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-measurement': form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-measurement']
            }
        )

        rendered_tag_create = mock_render.call_args[0][2]['tag_create']
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

    def test_post_should_404_on_recipe_not_found(self, _):
        updated_form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': 'new name',
            'directions': 'new directions',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '2',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '2',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': 'ingredient name',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': 'updated measurement',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-2-name': 'new ingredient name',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-2-measurement': 'new ingredient measurement'
        }

        response = self.client.post(
            reverse('recipe-update', args=[1234]),
            updated_form_data
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content.decode(), RECIPE_NOT_FOUND_ERROR)

    @patch('recipe_app.views.redirect', wraps=redirect)
    def test_success_updates_recipe_name_and_directions(self, mock_redirect, _):
        ingredient = Ingredient.objects.create(name='Test Ingredient')
        recipe = Recipe.objects.create(
            name='Test Recipe 1',
            directions='Test Directions'
        )
        recipe_ingredient = RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            measurement='a bunch'
        )

        updated_form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': 'New Recipe Name',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': 'Test Ingredient',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': 'a bunch',
            'directions': 'New Directions',
            f'{TAG_CREATE_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{TAG_CREATE_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name': ''
        }

        self.client.post(
            reverse('recipe-update', args=[recipe.pk]), updated_form_data
        )
        recipe = Recipe.objects.get(pk=recipe.pk)

        self.assertEqual(recipe.name, updated_form_data['name'])
        self.assertEqual(recipe.directions,
                         updated_form_data['directions'])

        self.assertTrue(
            Ingredient.objects.filter(pk=ingredient.pk).exists()
        )

        self.assertEqual(
            RecipeIngredient.objects.filter(
                recipe=recipe.pk,
                ingredient=recipe_ingredient.ingredient.pk,
                measurement=updated_form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement']
            ).count(),
            1
        )

        mock_redirect.assert_called_with(
            reverse('recipe-detail', args=[recipe.pk]))

    @patch('recipe_app.views.redirect', wraps=redirect)
    def test_success_adds_ingredient(self, mock_redirect, _):
        ingredient = Ingredient.objects.create(name='Test Ingredient')
        recipe = Recipe.objects.create(
            name='Test Recipe 1',
            directions='Test Directions'
        )
        recipe_ingredient = RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            measurement='a bunch'
        )

        updated_form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': recipe.name,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '2',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': 'Test Ingredient',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': 'a bunch',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-name': 'New Ingredient',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-measurement': 'new amount',
            'directions': 'Test Directions',
            f'{TAG_CREATE_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{TAG_CREATE_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name': ''
        }

        self.client.post(
            reverse('recipe-update', args=[recipe.pk]), updated_form_data
        )
        recipe = Recipe.objects.get(pk=recipe.pk)

        self.assertTrue(
            Ingredient.objects.filter(pk=ingredient.pk).exists()
        )

        self.assertEqual(
            RecipeIngredient.objects.filter(
                recipe=recipe.pk,
                ingredient=recipe_ingredient.ingredient.pk,
                measurement=updated_form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement']
            ).count(),
            1
        )

        new_ingredient = Ingredient.objects.filter(
            name=updated_form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-name'])
        self.assertTrue(new_ingredient.exists())

        self.assertEqual(
            RecipeIngredient.objects.filter(
                recipe=recipe.pk,
                ingredient=new_ingredient[0].pk,
                measurement=updated_form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-measurement']
            ).count(),
            1
        )

        mock_redirect.assert_called_with(
            reverse('recipe-detail', args=[recipe.pk]))

    @patch('recipe_app.views.redirect', wraps=redirect)
    def test_success_deletes_ingredient(self, mock_redirect, _):
        ingredient = Ingredient.objects.create(name='Test Ingredient')
        recipe = Recipe.objects.create(
            name='Test Recipe 1',
            directions='Test Directions'
        )
        recipe.tags.add(Tag.objects.get_or_create(name='Tag1')[0])
        unincluded_tag = Tag.objects.create(name='Tag2')
        recipe_ingredient = RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            measurement='a bunch'
        )

        updated_form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': recipe.name,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': 'Test Ingredient',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': 'a bunch',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-DELETE': 'on',
            'directions': 'Test Directions',
            f'{TAG_CREATE_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{TAG_CREATE_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name': ''
        }

        self.client.post(
            reverse('recipe-update', args=[recipe.pk]), updated_form_data
        )
        recipe = Recipe.objects.get(pk=recipe.pk)

        self.assertTrue(
            Ingredient.objects.filter(pk=ingredient.pk).exists()
        )

        self.assertEqual(
            RecipeIngredient.objects.filter(
                recipe=recipe.pk,
            ).count(),
            0
        )

        mock_redirect.assert_called_with(
            reverse('recipe-detail', args=[recipe.pk]))

    @patch('recipe_app.views.redirect', wraps=redirect)
    def test_success_updates_ingredient(self, mock_redirect, _):
        ingredient = Ingredient.objects.create(name='Test Ingredient')
        recipe = Recipe.objects.create(
            name='Test Recipe 1',
            directions='Test Directions'
        )
        recipe.tags.add(Tag.objects.get_or_create(name='Tag1')[0])
        unincluded_tag = Tag.objects.create(name='Tag2')
        recipe_ingredient = RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            measurement='a bunch'
        )

        updated_form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': recipe.name,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': 'Test Ingredient',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': 'a bit',
            'directions': 'Test Directions',
            f'{TAG_CREATE_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{TAG_CREATE_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name': ''
        }

        self.client.post(
            reverse('recipe-update', args=[recipe.pk]), updated_form_data
        )
        recipe = Recipe.objects.get(pk=recipe.pk)

        self.assertTrue(
            Ingredient.objects.filter(pk=ingredient.pk).exists()
        )

        self.assertEqual(
            RecipeIngredient.objects.filter(
                recipe=recipe.pk,
                ingredient=recipe_ingredient.ingredient.pk,
                measurement=updated_form_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement']
            ).count(),
            1
        )

        mock_redirect.assert_called_with(
            reverse('recipe-detail', args=[recipe.pk]))

    @patch('recipe_app.views.redirect', wraps=redirect)
    def test_success_with_tag_create(self, mock_redirect, _):
        recipe = Recipe.objects.create(name='Name', directions='Directions')

        form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': 'Name',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': '',
            'directions': 'Directions',
            f'{TAG_CREATE_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{TAG_CREATE_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name': 'New Tag'
        }

        self.client.post(
            reverse('recipe-update', args=[recipe.id]),
            data=form_data
        )

        self.assertIn(
            form_data[f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name'],
            recipe.tags.values_list('name', flat=True)
        )

        mock_redirect.assert_called_with(
            reverse('recipe-detail', args=[recipe.pk]))

    def test_success_tag_create_reuses_existing_tags(self, _):
        recipe = Recipe.objects.create(name='Name', directions='Directions')
        tag = Tag.objects.create(name='TagName')

        form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': recipe.name,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': '',
            'directions': recipe.directions,
            f'{TAG_CREATE_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{TAG_CREATE_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name': tag.name
        }

        self.client.post(
            reverse('recipe-update', args=[recipe.id]),
            data=form_data
        )

        self.assertEqual(
            recipe.tags.all()[0].id,
            tag.id
        )

    def test_success_tag_create_doesnt_duplicate_tags(self, _):
        tag = Tag.objects.create(name='TagName')
        recipe = Recipe.objects.create(name='Name', directions='Directions')
        recipe.tags.add(tag.id)

        form_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': recipe.name,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': '',
            'directions': recipe.directions,
            f'{TAG_CREATE_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{TAG_CREATE_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name': tag.name
        }

        self.client.post(
            reverse('recipe-update', args=[recipe.id]),
            data=form_data
        )

        self.assertEqual(
            len(recipe.tags.all()),
            1
        )
