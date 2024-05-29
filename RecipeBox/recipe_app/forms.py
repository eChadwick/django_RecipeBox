from django.forms import (
    CharField,
    formset_factory,
    Form,
    TextInput,
    BooleanField,
    CheckboxInput,
    IntegerField,
    HiddenInput,
    ChoiceField,
    RadioSelect,
)


class IngredientForm(Form):
    name_error = "Can't have Amount without Ingredient"
    name_field_placeholder = 'Ingredient'
    measurement_field_placeholder = 'Amount'

    name = CharField(
        max_length=255,
        required=False,
        label='',
        widget=TextInput(attrs={'placeholder': name_field_placeholder})
    )
    measurement = CharField(
        max_length=255,
        required=False,
        label='',
        widget=TextInput(attrs={'placeholder': measurement_field_placeholder})
    )
    DELETE = BooleanField(
        required=False,
        label='',
        widget=CheckboxInput(attrs={'onclick': 'hideParent(this)'})
    )

    def __eq__(self, other):
        return type(self) == type(other) and self.data == other.data

    def clean(self):
        if self.cleaned_data['measurement'] and not self.cleaned_data['name']:
            self.add_error('name', self.name_error)


extra_ingredient_form_count = 1
IngredientFormSetBase = formset_factory(
    IngredientForm, extra=extra_ingredient_form_count)


class IngredientFormSet(IngredientFormSetBase):

    def __eq__(self, other):
        if (len(self.forms) != len(other.forms)):
            return False

        for i in range(0, len(self.forms)):
            if (self.forms[i] != other.forms[i]):
                return False

        return True

    def is_empty(self):
        self.is_valid()
        if not self.cleaned_data:
            return True
        else:
            for entry in self.cleaned_data:
                if 'name' in entry and not entry.get('DELETE'):
                    return False

            return True


class RecipeForm(Form):
    name_error = 'Recipe name is required'
    name_field_placeholder = 'Recipe Name'
    content_error = 'Ingredients or directions must be provided'
    directions_field_placeholder = 'Directions'

    name = CharField(
        max_length=255,
        required=False,
        widget=TextInput(attrs={'placeholder': name_field_placeholder})
    )
    directions = CharField(
        max_length=10000,
        required=False,
        widget=TextInput(attrs={'placeholder': directions_field_placeholder})
    )

    def __eq__(self, other):
        return type(self) == type(other) and self.data == other.data

    def clean(self):
        if not self.cleaned_data['name']:
            self.add_error('name', self.name_error)


class IngredientInclusionForm(Form):
    radio_button_options = [
        ('or', 'Or'),
        ('and', 'And'),
        ('exclude', 'Exclude'),
        ('neutral', '-')
    ]
    default_inclusion_option = radio_button_options[3]

    name = CharField(
        max_length=255,
        widget=TextInput(attrs={'readonly': 'readonly'}),
        label=''
    )
    id = IntegerField(
        widget=HiddenInput()
    )
    inclusion = ChoiceField(
        choices=radio_button_options,
        widget=RadioSelect(),
        initial=default_inclusion_option,
        label=''
    )


IngredientInclusionFormSet = formset_factory(IngredientInclusionForm, extra=0)


class RecipeInclusionForm(Form):
    recipe_name = CharField(
        max_length=10000,
        required=False
    )


class TagForm(Form):
    tag_name = CharField(
        max_length=250
    )


TagFormset = formset_factory(TagForm, extra=1)
