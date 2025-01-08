# Используем официальный Python-образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /application

# Копируем файл зависимостей в контейнер и устанавливаем их
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в контейнер
COPY . /application

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=main.production


# Открываем порт (Heroku не использует EXPOSE, но это не повредит)
EXPOSE 8000

# Добавляем переменную для порта (Heroku передаёт $PORT автоматически)
ENV PORT=8000

# # Запускаем сервер с использованием переменной $PORT
CMD ["sh", "-c", "python manage.py migrate && gunicorn main.wsgi:application --bind 0.0.0.0:$PORT"]

# Запускаем скрипт ожидания и сервер Django
# CMD ["sh", "-c", "python wait_for_db.py db 5432 && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]