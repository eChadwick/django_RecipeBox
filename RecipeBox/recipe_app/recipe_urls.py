from django.urls import path

from . import views

urlpatterns = [
    path('', views.recipe_list , name='recipe-list'),
    path('delete/<int:pk>/', views.recipe_delete, name='recipe-delete'),
    path('detail/<int:pk>/', views.recipe_detail, name='recipe-detail'),
    path('create', views.recipe_create, name='recipe-create')
]