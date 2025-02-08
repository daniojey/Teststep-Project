# myapp/tests/test_validators.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from ..validators import validate_image
from PIL import Image
import io

# def validate_image(image):
#     """Валидатор для проверки размера изображения"""
#     MAX_SIZE = 10 * 1024 * 1024  # 10 MB
#     if image.size > MAX_SIZE:
#         raise ValidationError("Размер изображения превышает 10 МБ")

# class ImageValidatorTest(TestCase):
    # def create_image(self, size=(100, 100), format='JPEG', file_size=1024):
    #     """Утилита для создания тестового изображения с заданным размером файла"""
    #     img = Image.new('RGB', size)
    #     img_io = io.BytesIO()
    #     img.save(img_io, format=format)
    #     img_io.seek(0)
        
    #     # Проверка размера файла и его корректировка, если необходимо
    #     while img_io.tell() < file_size:
    #         img.save(img_io, format=format)
    #         img_io.seek(0)
        
    #     file = SimpleUploadedFile('test_image.jpg', img_io.read(), content_type='image/jpeg')
    #     return file

    # def test_valid_image(self):
    #     """Тестируем допустимое изображение"""
    #     image = self.create_image(size=(2000, 2000), format='JPEG', file_size=100 * 1024 * 1024)  # 100 MB
    #     try:
    #         # Запускаем валидатор
    #         validate_image(image)
    #     except ValidationError:
    #         self.fail("validate_image() вызвал ValidationError на допустимом изображении")

    # def test_image_size_too_large(self):
    #     """Тестируем слишком большой размер изображения"""
    #     image = self.create_image(size=(2000, 2000), format='JPEG', file_size=50 * 1024 * 1024)  # 50 MB
    #     with self.assertRaises(ValidationError):
    #         validate_image(image)

    # def test_invalid_image_format(self):
    #     """Тестируем изображение неподдерживаемого формата"""
    #     image = self.create_image(size=(200, 200), format='GIF', file_size=1024)
    #     with self.assertRaises(ValidationError):
    #         validate_image(image)

    # def test_corrupted_image(self):
    #     """Тестируем поврежденное изображение"""
    #     # Создаём файл, который не является изображением
    #     corrupted_file = SimpleUploadedFile('corrupted_image.jpg', b"not a valid image", content_type='image/jpeg')
    #     with self.assertRaises(ValidationError):
    #         validate_image(corrupted_file)