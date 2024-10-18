from unittest.mock import ANY

from django.test import TestCase

from recipe_app.models import Tag
from recipe_app.forms.forms import TagSelectionForm
from recipe_app.forms.tag_selection_formset import TagSelectionFormset


class TagSelectionFormsetTests(TestCase):
    def setUp(self):
        self.tag1 = Tag.objects.create(name='Tag1')
        self.tag2 = Tag.objects.create(name='Tag2')
        self.tag3 = Tag.objects.create(name='Tag3')

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

    def test_formset_returns_all_tags_unselected_by_default(self):
        uut = TagSelectionFormset()

        self.assertTrue(uut.is_valid())
        self.assertEqual(len(uut), 3)

        tag_form1 = uut.cleaned_data[0]
        self.assertEqual(tag_form1['tag_name'], self.tag1.name)
        self.assertEqual(tag_form1['id'], self.tag1.id)
        self.assertFalse(tag_form1['include'])

        tag_form2 = uut.cleaned_data[1]
        self.assertEqual(tag_form2['tag_name'], self.tag2.name)
        self.assertEqual(tag_form2['id'], self.tag2.id)
        self.assertFalse(tag_form2['include'])

        tag_form3 = uut.cleaned_data[2]
        self.assertEqual(tag_form3['tag_name'], self.tag3.name)
        self.assertEqual(tag_form3['id'], self.tag3.id)
        self.assertFalse(tag_form3['include'])

    def test_formset_marks_input_tags_as_selected(self):
        input_tags = Tag.objects.all()[:2]

        uut = TagSelectionFormset(input_tags)

        self.assertTrue(uut.is_valid())
        self.assertEqual(len(uut), 3)

        tag_form1 = uut.cleaned_data[0]
        self.assertEqual(tag_form1['tag_name'], self.tag1.name)
        self.assertEqual(tag_form1['id'], self.tag1.id)
        self.assertTrue(tag_form1['include'])

        tag_form2 = uut.cleaned_data[1]
        self.assertEqual(tag_form2['tag_name'], self.tag2.name)
        self.assertEqual(tag_form2['id'], self.tag2.id)
        self.assertTrue(tag_form2['include'])

        tag_form3 = uut.cleaned_data[2]
        self.assertEqual(tag_form3['tag_name'], self.tag3.name)
        self.assertEqual(tag_form3['id'], self.tag3.id)
        self.assertFalse(tag_form3['include'])

    def test_init_handles_custom_prefix(self):
        uut = TagSelectionFormset(prefix='test-prefix')

        self.assertTrue(uut.is_valid())
        self.assertEqual(len(uut), 3)

    def test_init_properly_constructs_management_form(self):
        uut = TagSelectionFormset()

        self.assertEqual(
            uut.data['form-TOTAL_FORMS'],
            str(len(Tag.objects.all()))
        )
        self.assertEqual(
            uut.data['form-INITIAL_FORMS'],
            str(len(Tag.objects.all()))
        )
        self.assertEqual(
            uut.data['form-MIN_NUM_FORMS'],
            ANY
        )
        self.assertEqual(
            uut.data['form-MAX_NUM_FORMS'],
            ANY
        )
