from django.forms import Form, ModelForm, CharField, formset_factory

from recipe_app.models import Recipe


class IngredientForm(Form):
    name_validation_error = 'Ingredient name is required'
    name = CharField(max_length=255, required=True, error_messages={
        'required': name_validation_error})
    measurement = CharField(max_length=255, required=False)


extra_ingredient_form_count = 1
IngredientFormSet = formset_factory(
    IngredientForm, extra=extra_ingredient_form_count)


class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'directions']
