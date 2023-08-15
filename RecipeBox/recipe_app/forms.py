from django.forms import ModelForm, CharField, formset_factory

from recipe_app.models import Recipe, Ingredient


class IngredientForm(ModelForm):
    measurement = CharField(max_length=255, required=False)

    class Meta:
        model = Ingredient
        fields = ['name']
        labels = {'name': 'Ingredient Name'}

    def __eq__(self, other):
        return type(self) == type(other) and self.data == other.data


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


class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'directions']
        labels = {'name': 'Recipe Name'}

    def __eq__(self, other):
        return type(self) == type(other) and self.data == other.data
