from django.forms import CharField, formset_factory, Form, TextInput


class IngredientForm(Form):
    name_error = 'Ingredient name is required when measurement is entered'
    name_field_placeholder = 'Ingredient'
    measurement_field_placeholder = 'Amount'

    name = CharField(
        max_length=255,
        required=False,
        label='Ingredient Name',
        widget=TextInput(attrs={'placeholder': name_field_placeholder})
    )
    measurement = CharField(
        max_length=255,
        required=False,
        widget=TextInput(attrs={'placeholder': measurement_field_placeholder})
    )

    def __eq__(self, other):
        return type(self) == type(other) and self.data == other.data

    def clean(self):
        if self.cleaned_data['measurement'] and not self.cleaned_data['name']:
            self.add_error('name', self.name_error)


extra_ingredient_form_count = 1
IngredientFormSetBase = formset_factory(
    IngredientForm, extra=extra_ingredient_form_count, can_delete=True)


class IngredientFormSet(IngredientFormSetBase):

    def __eq__(self, other):
        if (len(self.forms) != len(other.forms)):
            return False

        for i in range(0, len(self.forms)):
            if (self.forms[i] != other.forms[i]):
                return False

        return True

    def is_empty(self):
        for form in self.forms:
            if form.is_valid():
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
