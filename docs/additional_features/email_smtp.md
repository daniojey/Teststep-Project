## Configuring email notifications
---
### Use in this project
- To send letters to students after assigning tests to them
- To reset your password, an email is used to send a link to change your password.

### 1️⃣ SMTP (for sending messages to email)

> You need to create a Google account and add two-factor authentication in the settings, then go to App Passwords and add a new app, then copy and save the password for the created app.

> [Reference](https://support.google.com/a/answer/176600?hl=uk)

```env
    ENABLE_SMTP=True
    EMAIL_HOST=smtp.gmail.com
    EMAIL_PORT=<465 for HTTP | 587 for HTTPS>
    EMAIL_HOST_USER= <email address of your account>
    EMAIL_HOST_PASSWORD=<Application password>
    EMAIL_USE_TLS=<True for HTTPS | False for HTTP>
```

In the future, you can disable the use of S3 in your project using ENABLE_SMTP.
