from django.contrib import admin
from django.urls import path, include

from recipe_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('recipes/', include('recipe_app.recipe_urls')),
    path('', views.recipe_list),
    path('ingredients/', include('recipe_app.ingredient_urls'))
]
