## Connecting Sentry to a project
---
Sentry - monitoring service that allows you to conveniently track errors on the server
---
### Instructions
1. Create a new account in [Sentry](https://sentry.io/)
2. Add the application and select Django
3. Go to Settings on the main page and search for Client Keys (DSN).
4. Copy your DSN, then go to the .env file you created and add your
```env
    ENABLE_SENTRY=True
    SENTRY_DSN="<Your DSN>"
```

In the future, you can disable the use of S3 in your project using ENABLE_SENTRY.