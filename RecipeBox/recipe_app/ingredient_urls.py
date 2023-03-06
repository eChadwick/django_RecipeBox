from django.urls import path

from . import views

urlpatterns = [
    path('', views.ingredient_list, name='ingredients')
]