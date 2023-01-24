from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.


class Ingredient(models.Model):
    name = models.CharField(null=False, max_length=200, unique=True)

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        self.clean_fields()
        try:
            self.validate_unique()
        except ValidationError:
            return

        models.Model.save(self, *args, **kwargs)

class Recipe(models.Model):
    name = models.CharField(null=False, max_length=200, unique=True)

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        self.clean_fields()
        try:
            self.validate_unique()
        except ValidationError:
            return

        models.Model.save(self, *args, **kwargs)