# 💼 TestStep

<div align="center" width="100%">
  <img src="docs/images/Home_page.png" alt="Описание" width="100%"/>
</div>

> Learning platform for testing students' knowledge
### [[Screenshots](docs/images/screenshots.md)]
### [[Demo](http://ec2-13-53-147-251.eu-north-1.compute.amazonaws.com/)]
---
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)]()

## 📋 Description

This project was created to monitor students' knowledge and serves as a convenient tool for testing students' knowledge, allowing teachers to quickly and conveniently create tests with different questions and assign tests to students in a group.

### ✨ Key features

- 🔥 **1** - Creating and editing tests
- ⚡ **2** - Groups for students and teachers  
- 🎯 **3** - Creating different types of questions for tests and different types of answers
- 🛡️ **4** - Students have the opportunity to change their password by receiving an email to their student email address.

---

## 🛠️ Project stack

### Frontend
- **HTML** - language for creating markup that will be displayed in the browser
- **CSS** - I use language to assign different styles to each element in HTML.
- **JavaScript** - A programming language that allows you to dynamically change elements in HTML.

### Backend
- **Python** `3.11.x - 3.13.x` - programming language
- **Django** `5.0.4` -  A framework for Python that makes it quick and easy to develop projects.
- **Postgresql** `17.x` - Database

---

## 📦 Dependencies

### Dependencies

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


### System requirements

- **Python**: version 3.11 or higher
- **pip**: version 21.x or higher
- **PostgreSQL**: version 16.x or higher
- **FFmpeg**: for processing audio/video files

---

### ⚙️ Setup and launch
1. Clone the project (To clone, you need to install [Github cli](https://git-scm.com/downloads))
```bash
    git clone https://github.com/daniojey/Pilot-project.git
```
2. Go to the project folder after successful cloning
```bash
    cd Pilot-project.git
```
3. Create a virtual environment using the command
```bash
    python -m venv <Name of environment>
```
4. After that, you will need to log in every time to interact with the project correctly.
> Activation of the virtual environment
```bash
    <Name of environment>/Scripts/activate
```
> If you need to exit it
```bash
    deactivate
```
5. Establishing project dependencies
```bash
    pip install -r requirements.txt
```
6. We are waiting for the installation to complete, after which we will proceed as follows
```
    main/
    ├── settings.py 
```
7. Go to line 115 of the code in settings.py.
> This segment will contain the following code
```bash
    DATABASES = {
        "default": dj_database_url.config(
            default="postgres://test:root@localhost:5432/Tests", conn_max_age=600
        )
    }
```
8. Download one of the latest versions of PostgreSql, then open pgadmin4 (the application that was installed along with Postgresql services):
   8.1. Create a user in the “Login/Group Roles” section.
       > Set your password, which will be used later, as well as in Previleges.
   8.2. Create a new Databases
       > In owner, select the user you created.

9. Now you need to change the URL specified in DATABASES in settings.py, which you can edit.
```bash
    default="postgres://<Name of the created user>:<User password>@localhost:5432/<Name of the created database>", conn_max_age=600
```

10. Project launch
```bash
    python manage.py runserver
```

### 2️⃣ Django Secret key is required to access the project (optional feature, but mandatory for production)
>[You can generate a key here](https://djecrety.ir/)
> Only put the key in the .env file in the project root (if you haven't made a .env file yet, you can do that to add the django-secret-key and also connect extra features later).
```env
    DJANGO_SECRET_KEY = <Your secret key>
```

## 🔧 Available commands

| Command | Description |
|---------|----------|
| `python manage.py runserver` | Server startup |
| `python manage.py createsuperuser` | Creating an admin |
| `python manage.py pytest` | Launch of project tests |

---
### Additional features
> The project also supports additional features such as
- Sentry (Error Monitoring)
- Amazon S3 (for storing media and static files in the cloud)
- STMP (sending email messages)

**All additional dependencies are set in the .env file.**

1. [Sentry Installation guide](docs/additional_features/sentry.md)
2. [S3 Installation guide](docs/additional_features/amazon_s3.md)
3. [SMTP installation guide](docs/additional_features/email_smtp.md)