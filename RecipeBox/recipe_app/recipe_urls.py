from django.urls import path

from . import views

urlpatterns = [
    path('', views.recipe_search, name='home'),
    path('detail/<int:pk>/', views.recipe_detail, name='recipe-detail'),
    path('create', views.recipe_create, name='recipe-create'),
    path('update/<int:pk>/', views.recipe_update, name='recipe-update'),
    path('search', views.recipe_search, name='recipe-search')
]
