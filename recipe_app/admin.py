from django.contrib import admin
from recipe_app.models import Recipe, Ingredient, RecipeIngredient, Tag

# Register your models here.
admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(RecipeIngredient)
admin.site.register(Tag)