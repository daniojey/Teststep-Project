## Creating an S3 Bucket
---
S3 - responsible for storing media files and static files in this project, which is very important when deploying the project on Heroku, as it deletes all media stored in the project's local storage every 24 hours.

### Use in this project
- Saves project statistics and media files (images, audio files)

---
## Instructions

### 1 Registration
1. Go to [aws.amazon.com](https://aws.amazon.com)
2. Click **“Create an AWS Account”**
3. Fill out the registration form:
   - Email address
   - Password
   - AWS account name
4. Confirm your email

### 2 Choosing a plan

1. Select **“Basic support - Free”** to get started
2. Complete registration

> 💡 **Important**: AWS offers a 12-month Free Tier for new accounts!

### 3 Switching to the S3 console

1. Log in to [AWS Management Console](https://console.aws.amazon.com)
2. Enter **“S3”** in the search bar.
3. Select **“S3”** from the search results.

### 4 Creating a new bucket

1. Click **“Create bucket”**
2. Fill in the basic settings:
   - **Bucket name**: `your-project-media-files` (must be globally unique)
   - **AWS Region**: Select the nearest region (e.g., `us-east-1`)

### 5 Access settings

1. **Object Ownership**: select **“ACLs enabled”**
2. **Block Public Access settings**: 
   - Uncheck **“Block all public access”**
   - Check the confirmation box
3. **Bucket Versioning**: you can leave it **“Disable”**
4. **Default encryption**: select **“Amazon S3-managed keys (SSE-S3)”**

### 6 Completion of creation

1. Click **“Create bucket”**
2. The bucket will be created and will appear in the list.

---

## 👤 Step: Creating an IAM user

### 7 Switch to the IAM console

1. In the AWS Console, find **“IAM”** in the search bar.
2. Select **“IAM”**
3. In the left menu, click **“Users”**

### 8 Creating a new user

1. Click **“Create user”**
2. **User name**: enter a name, for example `s3-django-user`
3. **Access type**: select **“Programmatic access”**
4. Click **“Next”**

### 9 Configuring access rights

1. **Set permissions**: select **“Attach policies directly”**
2. In the search, find and select **“AmazonS3FullAccess”**
3. Click **“Next”**
4. Add tags (optional)
5. Click **“Create user”**

### 10 Keeping your access keys safe

1. After creating a user, you will see:
   - **Access key ID**: `AKIA...`
   - **Secret access key**: `...` 
2. **Copy and save both keys** - the secret key will not be displayed again!
3. You can download a .csv file with keys


### 11 CORS settings

1. Return to the S3 console
2. Select your bucket
3. Go to the **“Permissions”** tab.
4. Find **“Cross-Origin Resource Sharing (CORS)”**
5. Click **“Edit”** and paste:

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

### 11 Bucket Policy Settings
In the Permissions section of our S3, you need to find Bucket policy and click Edit, then add the following code and save it

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

### 12 Set the parameters in **.env**

```env
    ENABLE_S3=True
    AWS_ACCESS_KEY_ID=<id вашого bucket>
    AWS_SECRET_ACCESS_KEY=<access key який був отриманний при створенні bucket>
    AWS_STORAGE_BUCKET_NAME=<Назва вашого bucket>
    AWS_S3_REGION_NAME=eu-north-1
```
---
In the future, you can disable the use of S3 in your project using ENABLE_S3.