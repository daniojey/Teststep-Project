## Створення S3 Bucket
---
S3 - відповідає в цьому проекті за збереження медіа файлів та статики, це дуже необхідно в випадку розгортання проекту на Heroku, так як він кожні 24 години видаляє усі медіа що були збереженні в локальному сховищі проекту

### Використання в данному проекті
- Зберігає статику проекта а також медіа файли(картинки, аудіо файли)

---
## Інструкція

### 1 Реєстрація
1. Перейдіть на [aws.amazon.com](https://aws.amazon.com)
2. Натисніть **"Create an AWS Account"**
3. Заповніть реєстраційну форму:
   - Email адреса
   - Пароль
   - Назва акаунта AWS
4. Підтвердьте email

### 2 Вибір плану підтримки

1. Виберіть **"Basic support - Free"** для початку
2. Завершіть реєстрацію

> 💡 **Важливо**: Для нових акаунтів AWS надає Free Tier на 12 місяців!

### 3 Перехід до S3 консолі

1. Увійдіть у [AWS Management Console](https://console.aws.amazon.com)
2. У пошуковому рядку введіть **"S3"**
3. Виберіть **"S3"** з результатів пошуку

### 4 Створення нового bucket

1. Натисніть **"Create bucket"**
2. Заповніть основні налаштування:
   - **Bucket name**: `your-project-media-files` (має бути унікальним глобально)
   - **AWS Region**: виберіть найближчий регіон (наприклад, `us-east-1`)

### 5 Налаштування доступу

1. **Object Ownership**: виберіть **"ACLs enabled"**
2. **Block Public Access settings**: 
   - Зніміть позначку з **"Block all public access"**
   - Поставте позначку у підтвердженні
3. **Bucket Versioning**: можна залишити **"Disable"**
4. **Default encryption**: виберіть **"Amazon S3 managed keys (SSE-S3)"**

### 6 Завершення створення

1. Натисніть **"Create bucket"**
2. Bucket буде створено і він з'явиться у списку

---

## 👤 Крок : Створення IAM користувача

### 7 Перехід до IAM консолі

1. У AWS Console знайдіть **"IAM"** у пошуковому рядку
2. Виберіть **"IAM"**
3. У лівому меню натисніть **"Users"**

### 8 Створення нового користувача

1. Натисніть **"Create user"**
2. **User name**: введіть ім'я, наприклад `s3-django-user`
3. **Access type**: виберіть **"Programmatic access"**
4. Натисніть **"Next"**

### 9 Налаштування прав доступу

1. **Set permissions**: виберіть **"Attach policies directly"**
2. У пошуку знайдіть і виберіть **"AmazonS3FullAccess"**
3. Натисніть **"Next"**
4. Додайте теги (опціонально)
5. Натисніть **"Create user"**

### 10 Збереження ключів доступу

1. Після створення користувача ви побачите:
   - **Access key ID**: `AKIA...` (20 символів)
   - **Secret access key**: `...` (40 символів)
2. **Скопіюйте та збережіть обидва ключі** - секретний ключ більше не буде показано!
3. Можете завантажити .csv файл із ключами


### 11 Налаштування CORS

1. Поверніться до S3 консолі
2. Виберіть ваш bucket
3. Перейдіть у вкладку **"Permissions"**
4. Знайдіть **"Cross-origin resource sharing (CORS)"**
5. Натисніть **"Edit"** і вставте:

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": []
    }
]
```

### 11 Налаштування Bucket Policy
У розділі Persmission нашого S3 вам потрібно знайти Bucket policy та натиснути Edit, після чого додати такий код та сберегти

```bash
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::teststepbucket/*"
        }
    ]
}
```

### 12 Встановлюемо параметри в **.env**
```env
    AWS_ACCESS_KEY_ID=<id вашого bucket>
    AWS_SECRET_ACCESS_KEY=<access key який був отриманний при створенні bucket>
    AWS_STORAGE_BUCKET_NAME=<Назва вашого bucket>
    AWS_S3_REGION_NAME=eu-north-1
```