from datetime import date, timedelta
import factory
from factory.django import DjangoModelFactory
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image
from pydub import AudioSegment
from pydub.utils import which
from django.core.files.uploadedfile import SimpleUploadedFile

from tests.models import Tests

class ImageFactory:
    """Вспомогательный класс для создания изображений"""

    @staticmethod
    def create_image(filename="test.jpg", format="JPEG", size=(100, 100), color=(255, 0, 0)):
        """Создаёт настоящее изображение с помощью Pillow"""
        image = Image.new("RGB", size, color)
        img_io = BytesIO()
        image.save(img_io, format=format)
        img_io.seek(0)
        return SimpleUploadedFile(filename, img_io.read(), content_type="image/jpeg")
    
    @staticmethod
    def create_large_image():
        """Создаём файл с недопустимым размеров"""
        return ImageFactory.create_image("large.img", 20)
    
    @staticmethod
    def create_invalid_extension():
        return ImageFactory.create_image("image.gif")
    

# Указываем путь к ffmpeg вручную, если он не найден
AudioSegment.converter = which("ffmpeg") or "C:\\ffmpeg-7.1-essentials_build\\bin\\ffmpeg.exe"    

class AudioFactory:
    """Вспомогательный класс для создания аудио файлов"""
    
    @staticmethod
    def create_audio(filename="test.mp3", duration_ms=1000, format="mp3"):
        """Создаёт тестовый аудиофайл"""
        sample_rate = 44100
        channels = 1

        audio = AudioSegment.silent(duration=duration_ms, frame_rate=sample_rate)

        audio_io = BytesIO()
        audio.export(audio_io, format=format)
        audio_io.seek(0)

        return SimpleUploadedFile(filename, audio_io.read(), content_type=f"audio/{format}")
    
    @staticmethod
    def create_large_audio():
        """Создаём файл с недопустимым размером"""
        return AudioFactory.create_audio("large.mp3", duration_ms=500000)  # 20MB
    
    @staticmethod
    def create_invalid_extension():
        """Создаём файл с неподдерживаемым расширением"""
        return AudioFactory.create_audio("audio.txt", format="txt")
    

class TestFactory(DjangoModelFactory):
    class Meta:
        model=Tests

    name = "Test name"
    description = "Test description"
    check_type = Tests.AUTO_CHECK
    duration = factory.LazyFunction(lambda: timedelta(minutes=50))
    date_out = factory.LazyFunction(lambda: date(2025, 10, 5))

    students = factory.LazyAttribute(
        lambda obj: {"students": [str(obj.user.id),]}
    )

    @classmethod
    def create(cls, **kwargs):
        if 'user' not in kwargs:
            raise ValueError('user is required')
        if 'category' not in kwargs:
            raise ValueError('category is required')
        return super().create(**kwargs)

    