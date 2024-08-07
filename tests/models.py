from django.db import models

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

    QUESTION_TYPES = [
        (SINGLE_CHOICE, 'Single Choice'),
        (MULTIPLE_CHOICE, 'Multiple Choice'),
        (IMAGE, 'Image'),
        (AUDIO, 'Audio')
    ]

    test = models.ForeignKey(Tests, related_name='questions', on_delete=models.CASCADE, verbose_name="Тест")
    text = models.TextField(verbose_name="Текст вопроса")
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPES, verbose_name="Тип вопроса")
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
    text = models.TextField(verbose_name="Текст ответа")
    is_correct = models.BooleanField(default=False, verbose_name="Правильный ответ")

    class Meta:
        db_table = "answers"
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        return self.text