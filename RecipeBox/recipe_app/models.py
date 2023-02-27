from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.


class Ingredient(models.Model):
    name = models.CharField(null=False, max_length=200, unique=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = self.name.title()

    def __str__(self):
        return f'pk: {self.pk}, name: {self.name}'

    def save(self, *args, **kwargs):
        try:
            self.validate_unique()
        except ValidationError:
            return

        models.Model.save(self, *args, **kwargs)


class Recipe(models.Model):
    name = models.CharField(null=False, max_length=200, unique=True)
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient', related_name='ingredients')
    directions = models.CharField(null=True, max_length=5000)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = self.name.title()

    def __str__(self):
        return_string = (
            f'pk: {self.pk}, name: {self.name}, directions: {self.directions}, '
            f'ingredients: '
        )
        for ri in RecipeIngredient.objects.filter(recipe=self).all():
            return_string += f'{ri.ingredient.name} - {ri.measurement}, '
        # remove comma from final entry
        return_string = return_string[:-2]
        return return_string


class RecipeIngredient(models.Model):
    measurement = models.CharField(null=False, max_length=200)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.RESTRICT)

    def __str__(self):
        return (
            f'pk: {self.pk}, recipe_pk: {self.recipe.pk}, recipe_name: '
            f'{self.recipe.name}, ingredient_pk: {self.ingredient.pk}, '
            f'ingredient_name: {self.ingredient.name}, measurement: '
            f'{self.measurement}'
        )
