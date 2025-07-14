# 💼 TestStep

<div align="center" width="100%">
  <img src="docs/images/Home_page.png" alt="Описание" width="100%"/>
</div>

> Навчальна платформа для перевірки знань студентів

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)]()

## 📋 Опис

Данний проект був створений для контролю знань студентів і він слугуе зручним інструментом для перевірки знань студентів надавая змогу вчителям швидко та зручно створювати тести з різними питаннями і назначати тест студентим в группі

### ✨ Основні можливості

- 🔥 **1** - Створення та редагування тестів
- ⚡ **2** - Групи для учнів і вчителів  
- 🎯 **3** - Створення різних типів питань для тестів а такой різні типи відповідей
- 🛡️ **4** - В учнів є можливість змінювати пароль отримуючи лист на email учня 

---

## 🛠️ Стек проекту

### Frontend
- **HTML** - мова для створення розмітки яка буде відображена у браузері
- **CSS** - мова я слугуе для закріплення різних стилів за кожним елементом в HTML
- **JavaScript** - мова програмування яка надае можливість динамічно змінювати елменти в HTML

### Backend
- **Python** `3.11.x - 3.13.x` - мова програмування
- **Django** `5.0.4` -  фреймворк для Python який надає швидко та зручно розробляти проекти
- **Postgresql** `17.x` - PostgreSql база данний 

---

## 📦 Залежності

### Основні залежності (dependencies)

```json
 {
  "web_framework": {
    "Django": "5.2.4",
    "asgiref": "3.8.1",
    "gunicorn": "23.0.0"
  },
  "database": {
    "psycopg": "3.2.4", 
    "psycopg-binary": "3.2.4",
    "dj-database-url": "2.3.0",
    "sqlparse": "0.5.1"
  },
  "django_extensions": {
    "django-appconf": "1.0.6",
    "django-debug-toolbar": "5.0.1",
    "pytest-ordering": "0.6", 
    "django-imagekit": "5.0.0",
    "django-ratelimit": "4.1.0",
    "django-storages": "1.14.4",
    "django-unfold": "0.59.0",
    "django_csp": "3.8"
  },
  "aws_integration": {
    "boto3": "1.35.90",
    "botocore": "1.35.90",
    "s3transfer": "0.10.4"
  },
  "data_processing": {
    "pandas": "2.3.0",
    "numpy": "2.3.0",
    "openpyxl": "3.1.5",
    "xlrd": "2.0.1",
    "et_xmlfile": "2.0.0"
  },
  "media_processing": {
    "pillow": "11.0.0",
    "pilkit": "3.0",
    "audioread": "3.0.1",
    "pydub": "0.25.1",
    "ffmpeg-python": "0.2.0"
  },
  "http_requests": {
    "requests": "2.32.3",
    "httpx": "0.27.0",
    "httpcore": "1.0.6",
    "h11": "0.14.0",
    "urllib3": "2.2.3"
  },
  "utilities": {
    "python-decouple": "3.8",
    "python-dotenv": "1.0.1",
    "python-dateutil": "2.9.0.post0",
    "python-magic": "0.4.27",
    "pytz": "2024.2",
    "tzdata": "2024.1"
  },
  "testing_and_development": {
    "factory_boy": "3.3.3",
    "Faker": "36.1.0"
  },
  "monitoring_and_logging": {
    "sentry-sdk": "2.30.0", 
    "logtail-python": "0.3.3"
  },
  "static_files": {
    "whitenoise": "6.8.2"
  },
  "template_engine": {
    "Jinja2": "3.1.3",
    "MarkupSafe": "2.1.5"
  },
  "system_dependencies": {
    "anyio": "4.6.2.post1",
    "certifi": "2024.8.30",
    "charset-normalizer": "3.4.0",
    "idna": "3.10",
    "jmespath": "1.0.1",
    "lxml": "5.4.0",
    "msgpack": "1.1.0",
    "packaging": "24.2",
    "setuptools": "75.3.0",
    "six": "1.17.0",
    "sniffio": "1.3.1",
    "typing_extensions": "4.12.2",
    "future": "1.0.0"
  }
}

```


### Системні вимоги

- **Python**: версія 3.11 або вище
- **pip**: версія 21.x або вище  
- **PostgreSQL**: версія 16.x або вище
- **FFmpeg**: для обробки аудио/видео файлів

---

### ⚙️ Налаштування та запуск
1. Клонуйте проект (Для можливості клонування потрібно буде встановити [Github cli](https://git-scm.com/downloads))
```bash
    git clone https://github.com/daniojey/Pilot-project.git
```
2. Перейдіть в папрку проекту після успішного клонування
```bash
    cd Pilot-project.git
```
3. Створіть Віртуальне оточення за допомогою комманди
```bash
    python -m venv <Назва оточення>
```
4. Після чого вам потрібно буде переходити в нього кожен раз для правильної взаемодії с проектом
>Активація віртуального оточення
```bash
    <Назва оточення>/Scripts/activate
```
> Якщо необхідно вийти з нього
```bash
    deactivate
```
5. Встановлюємо залежності проекту
```bash
    pip install -r requirements.txt
```
6. Очікуємо завершення встановлення після чого переходимо за таким шляхом
```
    main/
    ├── settings.py 
```
7. Перейдіть на 115 строку коду в settings.py
> в данному відрізку буде такий код
```bash
    DATABASES = {
        "default": dj_database_url.config(
            default="postgres://test:root@localhost:5432/Tests", conn_max_age=600
        )
    }
```
8. Завантажте одну с останніх версій PostgreSql після чого відкрийте pgadmin4(застосунок який був встановлений разом з службами Postgresql):
   8.1. Ствоюйте користувача в Login/Group Roles
       > Установіть свій пароль який буде використовуватися пізніше а також в Previleges
   8.2. Створіть нову Databases
       > в owner оберіть створенного вами користувача

9. Тепер необхідно змінити url вказаний в DATABASES в settings.py який ви можете редагувати
```bash
    default="postgres://<Ім'я створенного користувача>:<Пароль користувача>@localhost:5432/<Назва свореної бази данних>", conn_max_age=600
```

10. Запуск проекту
```bash
    python manage.py runserver
```

### 2️⃣ Django Secret key необхідний для доступу к проекту(опіональна можливість але для продакшену обов'язкова)
>[Згенерувати ключ можна тут](https://djecrety.ir/)
> Встановлюйте ключ лише в файл .env у корні проекту(якщо ви не створили ще .env файл то можна це зробити щоб додати django-secret-key а також в подальшому підключити додаткові можливості)
```env
    DJANGO_SECRET_KEY = orz(0trfms-x^*c4+zjw(s-%rod^*&k6^5aqy@ysmhy8453fv8
```

## 🔧 Доступные команды

| Команда | Опис |
|---------|----------|
| `python manage.py runserver` | Запуск сервера |
| `python manage.py createsuperuser` | Створення адміна |
| `python manage.py pytest` | Запуск тестів проекту |

---
### Додаткові можливості
> Також проект підтримує додаткові можливості такі як
- Sentry(Моніторинг помилок)
- Amazon S3(Для сберігання медіа та статики в хмарі)
- STMP(відправка email повідомлень)

**Усі додаткові залежності встановлються в .env файл**

1. [Інструкція по встановленню Sentry](docs/additional_features/sentry.md)
2. [Інструкція по встановленню S3](docs/additional_features/amazon_s3.md)
3. [Інструкція по встановленню SMTP](docs/additional_features/email_smtp.md)