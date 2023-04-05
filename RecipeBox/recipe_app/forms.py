from django import forms

class IngredientForm(forms.Form):
    name = forms.CharField(max_length=255, required=True)
    measurement = forms.CharField(max_length=255, required=False)

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        measurement = cleaned_data.get('measurement')
        if not name and measurement:
            self.add_error('__all__', 'Ingredient name must be entered when measurement is provided')
        elif not (name and measurement):
            self.add_error('__all__', 'Invalid ingredient format')
