from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm, PasswordResetForm, SetPasswordForm

from users.models import User


class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        try:
            # Найдем пользователя по email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError('Користувача з такою електронною поштою не існує.')
        except User.MultipleObjectsReturned:
            self.cleaned_data['multiple_users_error'] = True
            raise forms.ValidationError('Виникла помилка, зверніться до служби підтримки')

        # Проверим пароль
        if not user.check_password(password):
            raise forms.ValidationError('Невірний пароль.')

        print(user.username)
        self.cleaned_data['username'] = user.username  # Задаем `username`, так как он нужен в процессе аутентификации

        return super(UserLoginForm, self).clean()


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
        username = forms.CharField(widget=forms.HiddenInput())
        email = forms.CharField()
        password1 = forms.CharField()
        password2 = forms.CharField()


class ProfileForm(UserChangeForm):

    class Meta:
        model = User
        fields = (
            'image',
            'first_name',
            'last_name',
            'email',
            'password'
        )



    image = forms.ImageField(required=False)
    first_name = forms.CharField()
    last_name = forms.CharField()
    username = forms.CharField()
    email = forms.CharField()
    password = forms.CharField()


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label='',
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Переопределяем help_text как HTML-код, чтобы изменить структуру, например, заменить `ul` на `div`
        self.fields['new_password1'].label = 'Новий пароль'
        self.fields['new_password1'].help_text = """
        <div class="password-rules">
            <p>- Пароль не повинен бути схожим на вашу особисту інформацію(наприклад рік/місяць/день народження).</p>
            <p>- Ваш пароль повинент бути не коротше 8 символів.</p>
            <p>- Пароль не повинен бути простим або розповсюдженним.</p>
            <p>- В вашому паролі не можуть використовуватися лише цифри.</p>
        </div>
        """
        self.fields['new_password2'].label = 'Повторіть пароль'