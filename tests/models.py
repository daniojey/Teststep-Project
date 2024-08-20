from django.db import models
from users.models import User

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_tests')
    name = models.CharField(verbose_name="Название",max_length=130, unique=True)
    description = models.CharField(verbose_name="Описание",max_length=500)
    image = models.ImageField(verbose_name="Превью",null=True, blank=True)
    duration = models.DurationField(verbose_name="Продолжительность теста", null=True, blank=True, default=60)
    category = models.ForeignKey(Categories, related_name='tests', on_delete=models.CASCADE, verbose_name="Категория")
    
    def __str__(self):
        return  self.name

    class Meta:
        db_table = "tests"
        verbose_name = "Тест"
        verbose_name_plural = "Тести"


class Question(models.Model):
    SINGLE_CHOICE = 'SC'                                                                                                                                                                                                
    MULTIPLE_CHOICE = 'MC'
    IMAGE = 'IMG'
    AUDIO = 'AUD'
    MATCHING = 'MTCH'
    TEXT = 'TXT'

    QUESTION_TYPES = [
        (SINGLE_CHOICE, 'Single Choice'),
        (MULTIPLE_CHOICE, 'Multiple Choice'),
        (IMAGE, 'Image'),
        (AUDIO, 'Audio'),
        (MATCHING, 'Matching'),
        (TEXT, 'Text')
    ]

    test = models.ForeignKey(Tests, related_name='questions', on_delete=models.CASCADE, default='single' ,verbose_name="Тест")
    text = models.TextField(verbose_name="Текст вопроса")
    question_type = models.CharField(max_length=5, choices=QUESTION_TYPES, verbose_name="Тип вопроса")
    image = models.ImageField(upload_to='questions/images/', blank=True, null=True, verbose_name="Картинка")
    audio = models.FileField(upload_to='questions/audios/', blank=True, null=True, verbose_name="Аудио")


    class Meta:
        db_table = "questions"
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE, verbose_name="Вопрос")
    text = models.CharField(verbose_name="Текст ответа", max_length=255)
    is_correct = models.BooleanField(default=False, verbose_name="Правильный ответ")

    class Meta:
        db_table = "answers"
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        return self.text
    
    
class TestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results')
    test = models.ForeignKey(Tests, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    date_taken = models.DateTimeField(auto_now_add=True)


    class Meta:
        db_table = 'test_results'
        verbose_name = 'Результат теста'
        verbose_name_plural = 'Результаты тестов'

    
    def __str__(self):
        return f"{self.user.username} - {self.test.name} - {self.score}"