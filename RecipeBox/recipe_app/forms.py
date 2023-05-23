from django import forms


class IngredientForm(forms.Form):
    name_validation_error = 'Ingredient name is required'
    name = forms.CharField(max_length=255, required=True, error_messages={
        'required': name_validation_error})
    measurement = forms.CharField(max_length=255, required=False)


IngredientFormSet = forms.formset_factory(IngredientForm, extra=1)


class RecipeForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        required=True,
        error_messages={
            'required': 'Recipe name is required'
        }
    )
    directions = forms.CharField(max_length=10000)

    def clean(self):
        cleaned_data = super().clean()
        self.cleaned_data['ingredients'] = IngredientFormSet(
            self.data['ingredients'])
