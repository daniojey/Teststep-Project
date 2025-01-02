from django.db import models
from users.models import User
from .validators import validate_image, validate_audio_file

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
    students = models.JSONField(verbose_name='Юзеры', default=list)
    name = models.CharField(verbose_name="Ім'ям",max_length=130, unique=True)
    description = models.CharField(verbose_name="Описание",max_length=500)
    image = models.ImageField(verbose_name="Превью",null=True, blank=True, validators=[validate_image], upload_to="test-images")
    duration = models.DurationField(verbose_name="Продолжительность теста", null=True, blank=True)
    date_taken = models.DateTimeField(auto_now_add=True)
    date_out = models.DateTimeField(auto_now_add=False, verbose_name='Будет доступный до')
    category = models.ForeignKey(Categories, related_name='tests', on_delete=models.CASCADE, verbose_name="Категория", null=False)
    check_type = models.CharField(max_length=10, choices=CHECK_CHOICES, default=AUTO_CHECK, verbose_name="Тип проверки ответов")

    def __str__(self):
        return  self.name

    class Meta:
        db_table = "tests"
        verbose_name = "Тест"
        verbose_name_plural = "Тести"


class QuestionGroup(models.Model):
    name = models.CharField(max_length=155, verbose_name='Назва группи')
    test = models.ForeignKey(Tests, on_delete=models.CASCADE)

    class Meta:
        db_table = 'question_group'
        verbose_name = 'Группа для вопросов'
        verbose_name_plural = 'Группы для вопросовё'
    
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

    test = models.ForeignKey(Tests, related_name='questions', on_delete=models.CASCADE,verbose_name="Тест")
    group = models.ForeignKey(QuestionGroup, related_name='questions_group', on_delete=models.SET_NULL, verbose_name="Группа", blank=True, null=True)
    text = models.TextField(verbose_name="Текст вопроса", blank=True, null=True)
    question_type = models.CharField(max_length=55, choices=QUESTION_TYPES, verbose_name="Тип питання")
    answer_type = models.CharField(choices=ANSWER_TYPES, verbose_name='Тип відповіді', blank=True, null=True)
    image = models.ImageField(upload_to='questions/images/', blank=True, null=True, verbose_name="Картинка", validators=[validate_image])
    audio = models.FileField(upload_to='questions/audios/', blank=True, null=True, verbose_name="Аудио", validators=[validate_audio_file])


    class Meta:
        db_table = "questions"
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return self.text or f"{self.question_type} - {self.id}"
    
class MatchingPair(models.Model):
    question = models.ForeignKey(Question, related_name='matching_pairs', on_delete=models.CASCADE)
    left_item = models.CharField(max_length=255, verbose_name='Левая часть')
    right_item = models.CharField(max_length=255, verbose_name='Правая часть')

    class Meta:
        db_table = "matching_pairs"
        verbose_name = "Пара для соответствия"
        verbose_name_plural = "Пари для соответствий"

    def __str__(self) -> str:
        return f"{self.left_item} - {self.right_item}"


class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE, verbose_name="Вопрос")
    text = models.CharField(verbose_name="Текст ответа", max_length=255)
    is_correct = models.BooleanField(default=False, verbose_name="Правильный ответ")
    audio_response = models.FileField(upload_to='answers/audios/', blank=True, null=True, verbose_name="Голосовой ответ")

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
    attempts = models.PositiveIntegerField(default=1)
    duration = models.DurationField(null=True, blank=True)
    max_attempts = models.PositiveIntegerField(default=2)
    extra_attempts = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'test_results'
        verbose_name = 'Результат теста'
        verbose_name_plural = 'Результаты тестов'

    
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
        verbose_name = 'Тест на проверку'
        verbose_name_plural = 'Тесты на проверку'

    def __str__(self):
        return f"Проверка по  {self.test.name}: проходил тест {self.user.username}"