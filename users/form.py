from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from users.models import User


class UserLoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField()


    class Meta:
        model = User
        

    # username = forms.CharField(
    #     label="Имя пользователя",
    #     widget=forms.TextInput(attrs={"autofocus": True,
    #                                   'class': 'form-control',
    #                                    'placeholder': 'Введите ваше имя пользователя', })
    # )
    # password = forms.CharField(
    #     label='Пароль',
    #     strip=False,
    #     widget=forms.PasswordInput(attrs={'autocomplete': "current-password",
    #                                       'class': 'form-control',
    #                                    'placeholder': 'Введите ваше имя пользователя',}),
    # )
        
class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'password1',
            'password2',
        )

        first_name = forms.CharField()
        last_name = forms.CharField()
        username = forms.CharField()
        email = forms.CharField()
        password1 = forms.CharField()
        password2 = forms.CharField()
