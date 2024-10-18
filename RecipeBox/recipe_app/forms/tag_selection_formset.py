from django.db.models import QuerySet
from django.forms import formset_factory

from recipe_app.forms.forms import TagSelectionForm
from recipe_app.models import Tag

TagSelectionFormsetBase = formset_factory(TagSelectionForm, extra=0)


class TagSelectionFormset(TagSelectionFormsetBase):

    def __init__(self, selected_tags=None, *args, **kwargs):
        all_tags = Tag.objects.all()

        selected_tag_ids = []
        if type(selected_tags) == QuerySet:
            for item in selected_tags:
                if type(item) == Tag:
                    selected_tag_ids.append(item.id)

        form_prefix = kwargs.get('prefix', 'form')
        formset_data = {
            f'{form_prefix}-TOTAL_FORMS': str(len(all_tags)),
            f'{form_prefix}-INITIAL_FORMS': str(len(all_tags)),
            f'{form_prefix}-MIN_NUM_FORMS': '',
            f'{form_prefix}-MAX_NUM_FORMS': '',
        }

        for i, tag in enumerate(all_tags):
            formset_data[f'{form_prefix}-{i}-tag_name'] = tag.name
            formset_data[f'{form_prefix}-{i}-id'] = str(tag.id)
            if tag.id in selected_tag_ids:
                formset_data[f'{form_prefix}-{i}-include'] = True

        kwargs['data'] = formset_data

        super().__init__(*args, **kwargs)
