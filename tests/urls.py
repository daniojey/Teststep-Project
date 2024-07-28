# tests/urls.py

from django.urls import path
from tests import views

app_name = "tests"

urlpatterns = [
    path('', views.index, name="index"),
    path("rating/", views.rating, name="rating"),
    path('create/', views.create_test, name='create_test'),
    path('<int:test_id>/add_questions/', views.add_questions, name='add_questions'),
    path('<int:test_id>/complete_questions/', views.complete_questions, name='complete_questions'),
    path('<int:test_id>/add_answers/', views.add_answers, name='add_answers'),
]
