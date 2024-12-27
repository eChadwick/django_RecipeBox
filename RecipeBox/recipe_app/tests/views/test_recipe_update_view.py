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
class RecipeUpdateView_GetTests(TestCase):

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


@patch('recipe_app.views.render', return_value=HttpResponse())
class RecipeUpdateView_Post_Error_Tests(TestCase):

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
            'directions': recipe.directions,
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
            'name': recipe.name,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': 'Amount',
            'directions': recipe.directions,
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
            'name': recipe.name,
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
class RecipeUpdateView_Post_Success_Tests(TestCase):

    def setUp(self):
        self.ingredient = Ingredient.objects.create(name='Test Ingredient')
        self.recipe = Recipe.objects.create(
            name='Test Recipe',
            directions='Test Directions'
        )
        self.recipe.tags.create(name='Tag1')
        self.recipe_ingredient = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient,
            measurement='a bunch'
        )

        self.post_data = {
            'csrfmiddlewaretoken': 'irrelevant',
            'name': self.recipe.name,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-INITIAL_FORMS': '1',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-name': self.ingredient.name,
            f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement': self.recipe_ingredient.measurement,
            'directions': self.recipe.directions,
            f'{TAG_CREATE_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{TAG_CREATE_FORMSET_PREFIX}-INITIAL_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MIN_NUM_FORMS': '0',
            f'{TAG_CREATE_FORMSET_PREFIX}-MAX_NUM_FORMS': '1000',
            f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name': '',
            f'{TAG_SELECT_FORMSET_PREFIX}-TOTAL_FORMS': '1',
            f'{TAG_SELECT_FORMSET_PREFIX}-INITIAL_FORMS': '1',
            f'{TAG_SELECT_FORMSET_PREFIX}-MIN_NUM_FORMS': '',
            f'{TAG_SELECT_FORMSET_PREFIX}-MAX_NUM_FORMS': '',
            f'{TAG_SELECT_FORMSET_PREFIX}-0-tag_name': self.recipe.tags.all().last().name,
            f'{TAG_SELECT_FORMSET_PREFIX}-0-include': 'on',
            f'{TAG_SELECT_FORMSET_PREFIX}-0-id': self.recipe.tags.all().last().id
        }

    def test_success_updates_recipe_name_and_directions(self, mock_redirect):

        self.post_data['name'] = 'New Recipe Name'
        self.post_data['directions'] = 'New Directions'

        self.client.post(
            reverse('recipe-update', args=[self.recipe.pk]), self.post_data
        )

        updated_recipe = Recipe.objects.get(pk=self.recipe.pk)

        self.assertEqual(updated_recipe.name, self.post_data['name'])
        self.assertEqual(updated_recipe.directions,
                         self.post_data['directions'])

        mock_redirect.assert_called_with(
            reverse('recipe-detail', args=[updated_recipe.pk]))

    def test_success_adds_ingredient(self, mock_redirect):
        self.post_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-name'] = 'New Ingredient'
        self.post_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-measurement'] = 'new amount'
        self.post_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS'] = str(
            int(self.post_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-TOTAL_FORMS']) + 1)

        self.client.post(
            reverse('recipe-update', args=[self.recipe.pk]), self.post_data
        )

        self.assertTrue(
            Ingredient.objects.filter(pk=self.ingredient.pk).exists()
        )

        self.assertEqual(
            RecipeIngredient.objects.filter(
                recipe=self.recipe.pk,
                ingredient=self.recipe_ingredient.ingredient.pk,
                measurement=self.post_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement']
            ).count(),
            1
        )

        new_ingredient = Ingredient.objects.filter(
            name=self.post_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-name'])
        self.assertTrue(new_ingredient.exists())

        self.assertEqual(
            RecipeIngredient.objects.filter(
                recipe=self.recipe.pk,
                ingredient=new_ingredient[0].pk,
                measurement=self.post_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-1-measurement']
            ).count(),
            1
        )

        mock_redirect.assert_called_with(
            reverse('recipe-detail', args=[self.recipe.pk]))

    def test_success_deletes_ingredient(self, mock_redirect):
        self.post_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-DELETE'] = 'on'

        self.client.post(
            reverse('recipe-update', args=[self.recipe.pk]), self.post_data
        )

        self.assertTrue(
            Ingredient.objects.filter(pk=self.ingredient.pk).exists()
        )

        self.assertEqual(
            RecipeIngredient.objects.filter(
                recipe=self.recipe.pk,
            ).count(),
            0
        )

        mock_redirect.assert_called_with(
            reverse('recipe-detail', args=[self.recipe.pk]))

    def test_success_updates_ingredient(self, mock_redirect):
        self.post_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement'] = 'New Measurement'

        self.client.post(
            reverse('recipe-update', args=[self.recipe.pk]), self.post_data
        )

        self.assertTrue(
            Ingredient.objects.filter(pk=self.ingredient.pk).exists()
        )

        self.assertEqual(
            RecipeIngredient.objects.filter(
                recipe=self.recipe.pk,
                ingredient=self.recipe_ingredient.ingredient.pk,
                measurement=self.post_data[f'{INGREDIENT_LIST_FORMSET_PREFIX}-0-measurement']
            ).count(),
            1
        )

        mock_redirect.assert_called_with(
            reverse('recipe-detail', args=[self.recipe.pk]))

    def test_success_with_tag_create(self, mock_redirect):
        self.post_data[f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name'] = 'New Tag'

        self.client.post(
            reverse('recipe-update', args=[self.recipe.id]), data=self.post_data
        )

        self.assertEqual(
            len(self.recipe.tags.all()),
            2
        )
        self.assertIn(
            self.post_data[f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name'],
            self.recipe.tags.values_list('name', flat=True)
        )

        mock_redirect.assert_called_with(
            reverse('recipe-detail', args=[self.recipe.pk]))

    def test_success_tag_create_reuses_existing_tags(self, _):
        existing_tag = Tag.objects.create(name='TagName')
        self.post_data[f'{TAG_CREATE_FORMSET_PREFIX}-0-tag_name'] = existing_tag.name

        self.client.post(
            reverse('recipe-update', args=[self.recipe.id]), data=self.post_data
        )

        self.assertEqual(
            len(self.recipe.tags.all()),
            2
        )
        self.assertEqual(
            self.recipe.tags.all().last().id,
            existing_tag.id
        )

    def test_success_with_tag_select(self, mock_redirect):
        extra_tag1 = Tag.objects.create(name='Extra Tag1')
        extra_tag2 = Tag.objects.create(name='Extra Tag2')

        self.post_data[f'{TAG_SELECT_FORMSET_PREFIX}-1-tag_name'] = extra_tag1.name
        self.post_data[f'{TAG_SELECT_FORMSET_PREFIX}-1-include'] = 'on'
        self.post_data[f'{TAG_SELECT_FORMSET_PREFIX}-1-id'] = extra_tag1.id

        self.post_data[f'{TAG_SELECT_FORMSET_PREFIX}-2-tag_name'] = extra_tag2.name
        self.post_data[f'{TAG_SELECT_FORMSET_PREFIX}-2-id'] = extra_tag2.id

        self.post_data[f'{TAG_SELECT_FORMSET_PREFIX}-TOTAL_FORMS'] = str(
            int(self.post_data[f'{TAG_SELECT_FORMSET_PREFIX}-TOTAL_FORMS']) + 2)
        self.post_data[f'{TAG_SELECT_FORMSET_PREFIX}-INITIAL_FORMS'] = self.post_data[f'{TAG_SELECT_FORMSET_PREFIX}-TOTAL_FORMS']

        self.client.post(
            reverse('recipe-update', args=[self.recipe.id]), data=self.post_data
        )

        self.assertEqual(
            len(self.recipe.tags.all()),
            2
        )

        self.assertEqual(
            self.recipe.tags.all().last().id,
            extra_tag1.id
        )

        mock_redirect.assert_called_with(
            reverse('recipe-detail', args=[self.recipe.pk]))
