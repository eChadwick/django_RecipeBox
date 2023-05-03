from django import forms


class IngredientForm(forms.Form):
    name = forms.CharField(max_length=255, required=True)
    measurement = forms.CharField(max_length=255, required=False)

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        measurement = cleaned_data.get('measurement')
        if not name and measurement:
            self.add_error(
                '__all__', 'Ingredient name must be entered when measurement is provided')
        elif not (name and measurement):
            self.add_error('__all__', 'Invalid ingredient format')


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
