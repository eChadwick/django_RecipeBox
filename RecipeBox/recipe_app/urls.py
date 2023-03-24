from django.urls import path

from . import views

urlpatterns = [
    path('', views.recipe_list , name='recipe-list'),
    path('recipes/delete/<int:pk>/', views.recipe_delete, name='recipe-delete'),
    path('recipes/detail/<int:pk>/', views.recipe_detail, name='recipe-detail')
]