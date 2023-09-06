from django.forms import ModelForm, CharField, formset_factory, Form

from recipe_app.models import Recipe


class IngredientForm(Form):
    name = CharField(max_length=255, required=False, label='Ingredient Name')
    measurement = CharField(max_length=255, required=False)

    name_error = 'Ingredient name is required when measurement is entered'

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
        for form in self.forms:
            if form.is_valid():
                return False

        return True


class RecipeForm(Form):
    name = CharField(max_length=255, required=False, label='Recipe Name')
    directions = CharField(max_length=10000, required=False)

    def __eq__(self, other):
        return type(self) == type(other) and self.data == other.data
