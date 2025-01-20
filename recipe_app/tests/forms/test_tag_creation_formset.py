from django.test import TestCase

from recipe_app.forms.forms import TagCreationFormset, TagCreationForm


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
