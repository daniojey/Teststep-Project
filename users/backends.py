from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, email=None, password=None, **kwargs):
        try:
            # Если передано имя пользователя, ищем по имени
            if username:
                user = User.objects.get(username=username)
            # Если передан email, ищем по email
            elif email:
                user = User.objects.get(email=email)
            else:
                return None
        except User.DoesNotExist:
            return None
        
        if user.check_password(password):
            return user
        return None