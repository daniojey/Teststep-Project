# tests/urls.py

from django.urls import path
from tests import views

app_name = "tests"

urlpatterns = [
    path('', views.index, name="index"),
    path("rating/", views.UserRatingView.as_view(), name="rating"),
    path("rating/<int:test_id>", views.RatingTestView.as_view(), name="rating_test"),
    path('all_tests/', views.AllTestsView.as_view() , name='all_tests'),
    path('test/<int:test_id>', views.test_preview , name='test_preview'),
    path('create/', views.create_test, name='create_test'),
    path('delete/<int:test_id>', views.delete_test, name='delete_test'),
    path('add_question_group/<int:test_id>/', views.add_question_group, name='add_question_group'),
    path('<int:test_id>/add_questions/', views.add_questions, name='add_questions'),
    path('delete/<int:question_id>/', views.delete_question, name='delete_question'),
    path('<int:question_id>/add_answers/', views.add_answers, name='add_answers'),
    path('<int:answer_id>/delete_answer/', views.delete_answer, name='delete_answer'),
    path('<int:question_id>/add_matching_pair/', views.add_matching_pair, name='add_matching_pair'),
    path('<int:test_id>/complete_questions/', views.complete_questions, name='complete_questions'),
    path('tests_group_reviews/<int:test_id>/', views.test_group_reviews, name='test_group_reviews'),
    path('test_st/<int:test_id>/', views.take_test, name='take_test'),
    path('results/<int:test_id>/', views.test_results, name='test_results'),
    path('tests_for_review/', views.tests_for_review, name='tests_for_review'),
    path('tests_for_review/<int:user_id>/<int:test_id>/', views.take_test_review, name='take_test_review'),
    path('success_page/', views.success_manual_test, name='success_page'),
]
