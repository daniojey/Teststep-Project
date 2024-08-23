# tests/urls.py

from django.urls import path
from tests import views

app_name = "tests"

urlpatterns = [
    path('', views.index, name="index"),
    path("rating/", views.rating, name="rating"),
    path("rating/<int:test_id>", views.rating_test, name="rating_test"),
    path('all_tests/', views.all_tests , name='all_tests'),
    path('test/<int:test_id>', views.test_preview , name='test_preview'),
    path('create/', views.create_test, name='create_test'),
    path('<int:test_id>/add_questions/', views.add_questions, name='add_questions'),
    path('<int:question_id>/add_answers/', views.add_answers, name='add_answers'),
    path('<int:test_id>/complete_questions/', views.complete_questions, name='complete_questions'),
    path('test_st/<int:test_id>/', views.take_test, name='take_test'),
    path('results/<int:test_id>/', views.test_results, name='test_results'),


]
