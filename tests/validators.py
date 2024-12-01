from django.forms import ValidationError
from PIL import Image

def validate_image(image):
    # Проверяем, если это объект BytesIO, получить размер напрямую
    if hasattr(image, 'size'):
        file_size = image.size  # Для BytesIO или аналогичных объектов
    elif hasattr(image, 'file') and hasattr(image.file, 'size'):
        file_size = image.file.size  # Для загруженных файлов
    else:
        raise ValidationError("Не вдалося визначити розмір зображення.")

    # Проверка размера файла
    max_size = 5 * 1024 * 1024  # 5 MB
    if file_size > max_size:
        raise ValidationError(f"Розмір зображення повинент бути не більше 5 MB. Ваш файл: {file_size / 1024 / 1024:.2f} MB.")
    
    # Проверка поврежденности изображения
    try:
        img = Image.open(image)
        img.verify()  # Проверка на повреждение изображения
    except (IOError, SyntaxError):
        raise ValidationError("Недопустимий або пошкодженний файл зображення.")
    
   # Дополнительная проверка на формат (например, jpg, png)
    valid_formats = ['JPEG', 'PNG', 'WEBP']  # Все в верхнем регистре
    print(img.format.upper())
    if img.format.upper() not in valid_formats:  # Приводим к верхнему регистру
        raise ValidationError(f"Недопустимий формат зображення. Підтримуються зображення типу: {', '.join(valid_formats)}.")