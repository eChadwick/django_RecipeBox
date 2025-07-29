from django.core.exceptions import ValidationError
from django.db import models


class Ingredient(models.Model):
    name = models.CharField(null=False, max_length=200,
                            unique=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = self.name.title()

    def save(self, *args, **kwargs):
        try:
            self.validate_unique()
        except ValidationError:
            self.pk = Ingredient.objects.get(name=self.name).pk
            return

        models.Model.save(self, *args, **kwargs)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(
        null=False,
        max_length=200,
        unique=True,
        blank=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = self.name.title()

    def save(self, *args, **kwargs):
        try:
            self.validate_unique()
        except ValidationError:
            self.pk = Tag.objects.get(name=self.name).pk
            return

        models.Model.save(self, *args, **kwargs)


class Recipe(models.Model):
    name = models.CharField(null=False, max_length=200,
                            unique=True, blank=True)
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient', related_name='ingredients')
    directions = models.CharField(null=True, max_length=5000, blank=True)
    tags = models.ManyToManyField(Tag)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = self.name.title()


class RecipeIngredient(models.Model):
    measurement = models.CharField(null=False, max_length=200)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.RESTRICT)
