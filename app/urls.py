from django.urls import path

from app import views

app_name = "app"
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path("about_dev/", views.AboutDevView.as_view(), name="about_dev"),
]

