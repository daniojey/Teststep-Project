from pathlib import Path
from uuid import uuid4
from django.core.files import File
from django.db import models
from django.contrib.auth.models import AbstractUser
from PIL import Image
from io import BytesIO

class User(AbstractUser):
    image = models.ImageField(upload_to='users_images', blank=True, null=True)

    def __str__(self):
        return  self.username
    
    def save(self, *args, **kwargs):
        # если файла нет или он не изменился — просто сохраняем
        try:
            if self.image and getattr(self.image, 'file', None):
                    img = Image.open(self.image)

                    ext = Path(self.image.name).suffix.lower().lstrip('.')
                    ext_map = {'jpg': 'JPEG', 'jpeg': 'JPEG', 'png': 'PNG', 'webp': 'WEBP'}

                    img.thumbnail((800, 600), Image.Resampling.LANCZOS)

                    output = BytesIO()
                    img.save(output, format=ext_map.get(ext, 'JPEG'), quality=85)
                    output.seek(0)

                    # >>> важная строка: только базовое имя, без «test-images/»
                    filename = f"{uuid4().hex}{Path(self.image.name).suffix.lower()}"
                    self.image.save(filename, File(output), save=False)
        except FileNotFoundError:
            pass
            
        super().save(*args, **kwargs)

    class Meta:
        db_table = "user"
        verbose_name = "Користувач"
        verbose_name_plural = "Користувачі"


class UsersGroup(models.Model):
    name = models.CharField(verbose_name="Назва групи", max_length=100,unique=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = 'users_group'
        verbose_name = 'Група'
        verbose_name_plural = 'Групи'


class UsersGroupMembership(models.Model):
    user = models.OneToOneField(User ,on_delete=models.CASCADE , related_name='Учистник')
    group = models.ForeignKey(UsersGroup, on_delete=models.CASCADE, related_name='Участники')
    owner = models.BooleanField(default=False, verbose_name="Вчитель групи")

    def __str__(self):
        return f"{self.user} - {self.group}"

    class Meta:
        db_table = 'user_group_membership'
        verbose_name = 'Членство користувача в групі'
        verbose_name_plural = 'Членство користувача в групах'


class LoginAttempt(models.Model):
    email = models.EmailField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.email or self.id_address} at {self.timestamp} - {'Sucess' if self.success else 'Filed'}"
    

    class Meta:
        db_table = 'loginattempt'
        verbose_name = 'Спроба входу'
        verbose_name_plural = 'Спроби входу'


class EmailTestNotyficateUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_notifyes', verbose_name="Користувач")
    test = models.ForeignKey("tests.Tests", on_delete=models.CASCADE, related_name="notyfies", verbose_name="Тест")

    def __str__(self) -> str:
        return f"{self.user.first_name}-{self.user.last_name} - Тест: {self.test}"
    
    class Meta:
        db_table = "notify_email_test"
        verbose_name = 'Email Повідомлення по тесту'
        verbose_name_plural = 'Email Повідомлення по тестам'