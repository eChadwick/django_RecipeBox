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
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient', related_name='ingredients')
    directions = models.CharField(null=True, max_length=5000)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = self.name.title()

    def __str__(self):
        return f'pk: {self.pk}, name: {self.name}, directions: {self.directions}'

class RecipeIngredient(models.Model):
    measurement = models.CharField(null=False, max_length=200)
    recipe = models.ForeignKey(Recipe,on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient,on_delete=models.CASCADE)

    def __str__(self):
        return f'pk: {self.pk}, recipe_primary_key: {self.recipe.pk}, ingredient_primary_key: {self.ingredient.pk}'