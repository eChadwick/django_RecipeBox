from django import forms


class IngredientForm(forms.Form):
    name_validation_error = 'Ingredient name is required'
    name = forms.CharField(max_length=255, required=True, error_messages={
        'required': name_validation_error})
    measurement = forms.CharField(max_length=255, required=False)


extra_ingredient_form_count = 1
IngredientFormSet = forms.formset_factory(
    IngredientForm, extra=extra_ingredient_form_count)


class RecipeForm(forms.Form):
    name_validation_error = 'Recipe name is required'
    ingredient_error = 'Ingredient errors are present'
    name = forms.CharField(
        max_length=255,
        required=True,
        error_messages={
            'required': 'Recipe name is required'
        }
    )
    directions = forms.CharField(max_length=10000)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if args and 'ingredients' in args[0]:
            self.ingredients = IngredientFormSet(args[0]['ingredients'])
        else:
            self.ingredients = IngredientFormSet()

    def clean(self):
        super().clean()
        if(not self.ingredients.is_valid()):
            self.add_error(None, self.ingredient_error)