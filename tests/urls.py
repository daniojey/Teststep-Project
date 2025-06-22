# tests/urls.py

from django.urls import path
from tests import views

app_name = "tests"

urlpatterns = [
    path('', views.index, name="index"),
    path("rating/", views.UserRatingView.as_view(), name="rating"),
    path("rating/<int:test_id>", views.RatingTestView.as_view(), name="rating_test"),
    path('all_tests/', views.AllTestsView.as_view() , name='all_tests'),
    path('test/<int:test_id>', views.TestPreviewView.as_view() , name='test_preview'),
    path('create/', views.CreateTestView.as_view(), name='create_test'),
    path('edit/<int:pk>/', views.EditTestView.as_view(), name='edit_test'),
    path('delete_test/<int:test_id>', views.delete_test, name='delete_test'),
    path('add_question_group/<int:test_id>/', views.AddQuestionGroupView.as_view(), name='add_question_group'),
    path('<int:test_id>/add_questions/', views.AddQuestionsView.as_view(), name='add_questions'),
    path('delete_question/<int:question_id>/', views.delete_question, name='delete_question'),
    path('<int:question_id>/add_answers/', views.AddAnswersView.as_view(), name='add_answers'),
    path('<int:question_id>/correct_answers/', views.SaveCorrectView.as_view(), name='correct_answers'),
    path('<int:answer_id>/delete_answer/', views.delete_answer, name='delete_answer'),
    path('<int:question_id>/add_matching_pair/', views.AddMathicngPairView.as_view(), name='add_matching_pair'),
    path('<int:pair_id>/delete_matching_pair/', views.delete_matching_pair, name='delete_matching_pair'),
    path('<int:test_id>/complete_questions/', views.complete_questions, name='complete_questions'),
    path('change_question_score/<int:ids>/', views.ChangeQuestionScoreView.as_view(), name='change_question_score'),
    path('change_answer_score/<int:ids>/', views.ChangeAnswerScoreView.as_view(), name='change_answer_score'),
    path('tests_group_reviews/<int:test_id>/', views.TestGroupReviewsView.as_view(), name='test_group_reviews'),
    path('take_test/<int:test_id>/', views.TakeTestView.as_view(), name='take_test'),
    path('results/<int:test_id>/', views.TestsResultsView.as_view(), name='test_results'),
    path('tests_for_review/', views.TestsForReviewView.as_view(), name='tests_for_review'),
    path('tests_review_result/', views.TestReviewResults.as_view(), name='test_review_results'),
    path('tests_for_review/<int:user_id>/<int:test_id>/', views.TakeTestReviewView.as_view(), name='take_test_review'),
    path('success_page/', views.success_manual_test, name='success_page'),
]
