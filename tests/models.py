import os
from uuid import uuid4
from pathlib import Path
from django.db import models
from django.forms import ValidationError
from users.models import User
from .validators import validate_image, validate_audio_file
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from PIL import Image
from io import BytesIO
from django.core.files import File
from django.core.validators import MinValueValidator, MaxValueValidator

class Categories(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Назва")
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name="URL")
    
    def __str__(self):
        return  self.name

    class Meta:
        db_table = "category"
        verbose_name = "Категорію"
        verbose_name_plural = "Категорії"


class Tests(models.Model):
    MANUAL_CHECK = 'manual'
    AUTO_CHECK = 'auto'
    CHECK_CHOICES = [
        (MANUAL_CHECK, 'Ручна перевірка'),
        (AUTO_CHECK, 'Авто-перевірка')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_tests')
    students = models.JSONField(verbose_name='Студенти', default=list, blank=True, null=True)
    name = models.CharField(verbose_name="Ім'я",max_length=130, unique=True)
    description = models.CharField(verbose_name="Описание",max_length=500)
    image = models.ImageField(verbose_name="Превью",null=True, blank=True, validators=[validate_image], upload_to="test-images")
    duration = models.DurationField(verbose_name="Продовжуваність теста", null=True, blank=True)
    date_taken = models.DateTimeField(auto_now_add=True)
    date_in = models.DateTimeField(auto_now_add=False, verbose_name='c')
    date_out = models.DateTimeField(auto_now_add=False, verbose_name='до')
    category = models.ForeignKey(Categories, related_name='tests', on_delete=models.CASCADE, verbose_name="Категорія", null=False)
    check_type = models.CharField(max_length=10, choices=CHECK_CHOICES, default=AUTO_CHECK, verbose_name="Тип перевірки відповідей")
    image_thumbnail = ImageSpecField(source='image',
                                      processors=[ResizeToFill(286, 184)],
                                      format='JPEG',
                                      options={'quality': 40})

    def __str__(self):
        return  self.name
    
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

    def clean(self):
        super().clean()

        if self.image or getattr(self.image, 'name', None):
            valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            ext = os.path.splitext(self.image.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError({
                    'image': f"Недопустимый формат изображения: {ext}. Поддерживаются: {', '.join(valid_extensions)}."
                })

    class Meta:
        db_table = "tests"
        verbose_name = "Тест"
        verbose_name_plural = "Тести"


class QuestionGroup(models.Model):
    name = models.CharField(max_length=155, verbose_name='Назва группи')
    test = models.ForeignKey(Tests, on_delete=models.CASCADE)

    class Meta:
        db_table = 'question_group'
        verbose_name = 'Группа для питань'
        verbose_name_plural = 'Группы для питань'
    
    def __str__(self):
        return f"Группа - {self.name}: Тест - {self.test}"
    

class Question(models.Model):
    TEXT = 'TXT'                                                                                                                                                                                                   
    IMAGE = 'IMG'
    AUDIO = 'AUD'
    MATCHING = 'MTCH'

    QUESTION_TYPES = [
        (TEXT, 'Тест з текстом'),
        (IMAGE, 'Тест з фотографіею'),
        (AUDIO, 'Тест з голосовим питанням'),
        (MATCHING, 'Тест з встановленням відповідності'),
        
    ]

    SINGLE_CHOICE = 'SC'
    MULTIPLE_CHOICE = 'MC'
    ANSWER_INPUT = 'INP'
    ANSWER_AUDIO = 'AUD'

    ANSWER_TYPES = [
        (MULTIPLE_CHOICE, 'Множинний вибір'),
        (SINGLE_CHOICE, 'Одиночний вибір'),
        (ANSWER_INPUT, 'Текстова відповідь'),
        (ANSWER_AUDIO, 'Голосова відповідь'),
    ] 

    SCORE_FOR_ANSWER = "SA"
    SCORE_FOR_QUESTION = "SQ"

    SCORE_FOR_TYPES = [
        (SCORE_FOR_ANSWER, 'Бали за відповідь'),
        (SCORE_FOR_QUESTION, 'Бали за питання'),
    ]

    test = models.ForeignKey(Tests, related_name='questions', on_delete=models.CASCADE,verbose_name="Тест")
    group = models.ForeignKey(QuestionGroup, related_name='questions_group', on_delete=models.SET_NULL, verbose_name="Группа", blank=True, null=True)
    scores_for = models.CharField(choices=SCORE_FOR_TYPES , verbose_name="Тип оцінювання")
    scores = models.FloatField(default=0, validators=[MinValueValidator(0.0), MaxValueValidator(500.0)], verbose_name="Бали за питання", blank=True, null=True)
    text = models.TextField(verbose_name="Текст питання", blank=True, null=True)
    question_type = models.CharField(max_length=55, choices=QUESTION_TYPES, verbose_name="Тип питання")
    answer_type = models.CharField(choices=ANSWER_TYPES, verbose_name='Тип відповіді', blank=True, null=True)
    image = models.ImageField(upload_to='questions/images/', blank=True, null=True, verbose_name="Фото", validators=[validate_image])
    audio = models.FileField(upload_to='questions/audios/', blank=True, null=True, verbose_name="Аудио", validators=[validate_audio_file])


    class Meta:
        db_table = "questions"
        verbose_name = "Питання"
        verbose_name_plural = "Питання"

    def update_question_score(self):
        if self.scores_for == "SQ":
            pass
        elif self.scores_for == "SA":
            if self.question_type == 'MTCH':
                self.scores = sum(
                    pair.score for pair in self.matching_pairs.all()
                );
                self.save()
            elif self.answer_type == "INP":
                self.scores = self.answers.filter(is_correct=True).aggregate(models.Max('score'))['score__max']
                self.save()
            else:
                self.scores = sum(
                    answer.score for answer in self.answers.filter(is_correct=True)
                )
                self.save()

    @property
    def question_info(self):
        return self.text or f"{self.question_type} - {self.id}"

    def __str__(self):
        return f"Дата та назва тесту: {self.test.date_taken.date()} - {self.test.name}|  Питання: {self.text}" or f"Дата та назва тесту: {self.test.date_taken.date()} - {self.test.name}| Питання: {self.question_type} - {self.id}"

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

    def clean(self):
        super().clean()

        if self.image or getattr(self.image, 'name', None):
            valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            ext = os.path.splitext(self.image.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError({
                    'image': f"Недопустимый формат изображения: {ext}. Поддерживаются: {', '.join(valid_extensions)}."
                })
    

class MatchingPair(models.Model):
    question = models.ForeignKey(Question, related_name='matching_pairs', on_delete=models.CASCADE)
    score = models.FloatField(default=1, verbose_name="Бали за відповідність")
    left_item = models.CharField(max_length=255, verbose_name='Ліва частина')
    right_item = models.CharField(max_length=255, verbose_name='Права частина')

    class Meta:
        db_table = "matching_pairs"
        verbose_name = "Пара для відповідності"
        verbose_name_plural = "Пари для відповідності"

    def __str__(self) -> str:
        return f"Питання: {self.question.question_info}| Відповідність: {self.left_item} - {self.right_item}"


class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE, verbose_name="Питання")
    score = models.FloatField(default=0, verbose_name="Бали за відповідь")
    text = models.CharField(verbose_name="Текст відповіді", max_length=255)
    is_correct = models.BooleanField(default=False, verbose_name="Правильна відповідь")
    audio_response = models.FileField(upload_to='answers/audios/', blank=True, null=True, verbose_name="Голосова відповідь")

    class Meta:
        db_table = "answers"
        verbose_name = "Відповідь"
        verbose_name_plural = "Відповіді"

    def __str__(self):
        return f"Питання: {self.question.question_info}| Відповідь: {self.text}"



class TestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results')
    test = models.ForeignKey(Tests, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    date_taken = models.DateTimeField(auto_now_add=True)
    attempts = models.PositiveIntegerField(default=1)
    duration = models.DurationField(null=True, blank=True)
    max_attempts = models.PositiveIntegerField(default=2)
    extra_attempts = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'test_results'
        verbose_name = 'Результат теста'
        verbose_name_plural = 'Результати тестів'

    
    def __str__(self):
        return f"{self.user.username} - {self.test.name} - {int(self.score)}%"
    
    @property
    def remaining_atemps(self):
        return (self.max_attempts + self.extra_attempts) - self.attempts
    

class TestsReviews(models.Model):
    test = models.ForeignKey(Tests, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_taken = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField()
    answers = models.JSONField()  # Хранение ответов пользователя в формате JSON
    audio_answers = models.JSONField(blank=True, null=True)
    group = models.CharField(max_length=100, blank=True, null=True)  # Опционально: группа пользователя
    reviewed = models.BooleanField(default=False)
    score = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "test_reviews"
        verbose_name = 'Тест на перевірку'
        verbose_name_plural = 'Тести на перевірку'

    def __str__(self):
        return f"Перевірка по  {self.test.name}: пройшов тест {self.user.username}"
