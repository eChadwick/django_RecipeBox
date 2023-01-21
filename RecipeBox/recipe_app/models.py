from django.db import models

# Create your models here.


class Ingredient(models.Model):
    name = models.CharField(null=False, max_length=200, unique=True)

    def clean(self):
        self.name = self.name.capitalize()
