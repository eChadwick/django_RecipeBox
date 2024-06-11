from unittest.mock import patch

from django.forms import (
    CharField,
    BooleanField,
    IntegerField,
    HiddenInput,
    ChoiceField,
    RadioSelect,
    TextInput
)

from django.test import TestCase

from recipe_app.forms import (
    IngredientForm,
    RecipeForm,
    IngredientFormSet,
    extra_ingredient_form_count,
    IngredientInclusionForm,
    IngredientInclusionFormSet,
    RecipeInclusionForm,
    TagCreationForm,
    TagCreationFormset,
    TagSelectionForm,
    TagSelectionFormset
)
from recipe_app.models import Recipe


class IngredientFormTests(TestCase):
    def test_fields(self):
        form = IngredientForm()

        name_field = form.fields['name']
        self.assertIsInstance(name_field, CharField)
        self.assertFalse(name_field.required)
        self.assertEqual(name_field.max_length, 255)
        self.assertEqual('', name_field.label)
        self.assertEqual(
            name_field.widget.attrs['placeholder'],
            IngredientForm.name_field_placeholder
        )

        measurement_field = form.fields['measurement']
        self.assertIsInstance(measurement_field, CharField)
        self.assertFalse(measurement_field.required)
        self.assertEqual(measurement_field.max_length, 255)
        self.assertEqual('', measurement_field.label)
        self.assertEqual(
            measurement_field.widget.attrs['placeholder'],
            IngredientForm.measurement_field_placeholder
        )

        delete_field = form.fields['DELETE']
        self.assertIsInstance(delete_field, BooleanField)
        self.assertEqual('', delete_field.label)
        self.assertEqual(
            delete_field.widget.attrs['onclick'],
            'hideParent(this)'
        )

    def test_equality_operator(self):
        form_data = {'name': 'test name', 'measurement': 'a bit'}
        form1 = IngredientForm(form_data)
        form2 = IngredientForm(form_data)
        self.assertEqual(form1, form2)

    def test_has_error_when_name_missing_and_measurement_entered(self):
        form = IngredientForm({'measurement': 'a bit'})

        self.assertFalse(form.is_valid())
        self.assertIn(IngredientForm.name_error, form.errors['name'])


class IngredientFormsetTests(TestCase):

    def test_extra_formset_count(self):
        formset = IngredientFormSet()
        self.assertEqual(
            formset.total_form_count(),
            extra_ingredient_form_count
        )

    @patch('recipe_app.forms.IngredientForm.__eq__', return_value=True)
    def test_equal(self, mock_eq):
        IngredientFormSet1 = IngredientFormSet({})
        IngredientFormSet2 = IngredientFormSet({})
        self.assertEqual(IngredientFormSet1, IngredientFormSet2)

    @patch('recipe_app.forms.IngredientForm.__eq__', return_value=True)
    def test_not_equal(self, mock_eq):
        IngredientFormSet1 = IngredientFormSet({})
        IngredientFormSet2 = IngredientFormSet({
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-0-name': 'name'
        })
        self.assertNotEqual(IngredientFormSet1, IngredientFormSet2)

    def test_not_empty(self):
        formset = IngredientFormSet({
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-0-name': 'name'
        })
        self.assertFalse(formset.is_empty())

    def test_empty(self):
        formset = IngredientFormSet({
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-name': '',
            'form-0-measurement': '',
            'form-1-name': 'deleted',
            'form-1-DELETE': 'on'
        })
        self.assertTrue(formset.is_empty())


class RecipeFormTests(TestCase):

    def test_fields(self):
        form = RecipeForm()

        name_field = form.fields['name']
        self.assertIsInstance(name_field, CharField)
        self.assertEqual(name_field.max_length, 255)
        self.assertFalse(name_field.required)
        self.assertEqual(
            name_field.widget.attrs['placeholder'],
            RecipeForm.name_field_placeholder
        )

        directions_field = form.fields['directions']
        self.assertIsInstance(directions_field, CharField)
        self.assertEqual(directions_field.max_length, 10000)
        self.assertFalse(directions_field.required)
        self.assertEqual(
            directions_field.widget.attrs['placeholder'],
            RecipeForm.directions_field_placeholder
        )

    def test_equality_operator(self):
        form_data = {'name': 'test name', 'directions': 'do stuff'}
        form1 = RecipeForm(form_data)
        form2 = RecipeForm(form_data)
        self.assertEqual(form1, form2)

    def test_form_has_error_when_name_missing(self):
        form = RecipeForm({})

        self.assertFalse(form.is_valid())
        self.assertIn(RecipeForm.name_error, form.errors['name'])


class IngredientInclusionFormTests(TestCase):

    def test_form_fields(self):
        form = IngredientInclusionForm()

        name_field = form.fields['name']
        self.assertIsInstance(name_field, CharField)
        self.assertEqual(name_field.max_length, 255)
        self.assertEqual(name_field.label, '')

        name_field_widget = name_field.widget
        self.assertIsInstance(name_field_widget, TextInput)
        self.assertEqual(
            name_field_widget.attrs['readonly'],
            'readonly'
        )

        id_field = form.fields['id']
        self.assertIsInstance(id_field, IntegerField)
        self.assertIsInstance(id_field.widget, HiddenInput)

        inclusion_field = form.fields['inclusion']
        self.assertIsInstance(inclusion_field, ChoiceField)
        self.assertEqual(
            inclusion_field.choices,
            IngredientInclusionForm.radio_button_options
        )
        self.assertEqual(
            inclusion_field.initial,
            IngredientInclusionForm.default_inclusion_option
        )
        self.assertIsInstance(
            inclusion_field.widget,
            RadioSelect
        )
        self.assertEqual(
            inclusion_field.label,
            ''
        )


class IngredientInclusionFormSetTests(TestCase):

    def test_formset_settings(self):
        formset = IngredientInclusionFormSet()

        self.assertEqual(
            formset.extra,
            0
        )

        self.assertEqual(
            formset.form,
            IngredientInclusionForm
        )


class RecipeInclusionFormTests(TestCase):
    def test_fields(self):
        form = RecipeInclusionForm()
        name_field = form.fields['recipe_name']
        self.assertIsInstance(name_field, CharField)
        self.assertEqual(name_field.max_length, 10000)
        self.assertEqual(name_field.required, False)


class TagCreationFormTests(TestCase):
    def test_fields(self):
        form = TagCreationForm()
        name_field = form.fields['tag_name']
        self.assertIsInstance(name_field, CharField)
        self.assertEqual(name_field.max_length, 250)
        self.assertEqual(name_field.required, True)


class TagCreationFormsetTests(TestCase):
    def test_formset_settings(self):
        formset = TagCreationFormset()

        self.assertEqual(
            formset.extra,
            1
        )

        self.assertEqual(
            formset.form,
            TagCreationForm
        )


class TagSelectionFormTests(TestCase):
    def test_fields(self):
        form = TagSelectionForm()

        name_field = form.fields['tag_name']
        self.assertIsInstance(name_field, CharField)
        self.assertEqual(name_field.max_length, 250)

        id_field = form.fields['id']
        self.assertIsInstance(id_field, IntegerField)
        self.assertIsInstance(id_field.widget, HiddenInput)


class TagSelectionFormsetTests(TestCase):
    def test_formset_settings(self):
        formset = TagSelectionFormset()

        self.assertEqual(
            formset.extra,
            0
        )

        self.assertEqual(
            formset.form,
            TagSelectionForm
        )
