from django.urls import path
from users import views

app_name = "users"

urlpatterns = [
    path('login/', views.UserLoginView.as_view() , name="login"),
    path('registration/', views.UserRegistrationView.as_view() , name="registration"),
    path('profile/', views.profile , name="profile"),
    path('logout/', views.logout, name='logout'),
    path('profile_image_upload/', views.profile_image_upload, name='profile_image_upload'),
]
