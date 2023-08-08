from django.forms import ModelForm, CharField, formset_factory

from recipe_app.models import Recipe, Ingredient


class IngredientForm(ModelForm):
    measurement = CharField(max_length=255, required=False)

    class Meta:
        model = Ingredient
        fields = ['name']

    def __eq__(self, other):
        return type(self) == type(other) and self.data == other.data


extra_ingredient_form_count = 1
IngredientFormSet = formset_factory(
    IngredientForm, extra=extra_ingredient_form_count)


class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'directions']
