from django.urls import path
from users import views
from django.contrib.auth import views as auth_views
from users.form import CustomPasswordResetForm, CustomSetPasswordForm
from django.views.decorators.cache import cache_page

app_name = "users"

urlpatterns = [
    path('login/', views.UserLoginView.as_view() , name="login"),
    path('registration/', views.UserRegistrationView.as_view() , name="registration"),
    path('profile/', views.UserProfileView.as_view() , name="profile"),
    path('logout/', views.logout, name='logout'),
    path('profile_image_upload/', views.profile_image_upload, name='profile_image_upload'),
    path('adding_students/', views.AddUsersView.as_view(), name='adding_students'),

    path('reset_password/', auth_views.PasswordResetView.as_view(
        template_name='users/reset_password.html',
        email_template_name='users/password_reset_email.html',
        success_url='/user/reset_password_sent/',
        form_class=CustomPasswordResetForm,
    ), name='reset_password'),
    
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html',
        success_url='/user/reset_password_complete/',
        form_class=CustomSetPasswordForm,
    ), name='password_reset_confirm'),
    
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'
    ), name='password_reset_complete'),
]

