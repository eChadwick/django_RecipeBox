from django.urls import path

from . import views

urlpatterns = [
    path('', views.recipe_list , name='recipes'),
    path('recipes/delete/<int:pk>/', views.recipe_delete, name='recipe-delete')
]