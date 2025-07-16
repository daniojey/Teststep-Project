# tasks.py
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from users.models import User, EmailTestNotyficateUser

@shared_task(bind=True, max_retries=3)
def send_emails_task(self, users_data, test_id):
    try:
        if users_data:
            from .models import Tests

            test = Tests.objects.get(id=test_id)
            users = User.objects.filter(id__in=users_data)
            subject = "Вам назначений тест"
            notifies = list(
                EmailTestNotyficateUser.objects.filter(test=test)
                .select_related("user")
                .values_list("user__id", flat=True)
                .distinct()
            )
            
            sended_emails = []

            for user in users:
                try:
                    if int(user.id) not in notifies and not user.is_staff and not user.is_superuser:
                        context = {
                            "user": user,
                            "test": test,
                        }

                        html_message = render_to_string(
                            "emails/notify_user_set_test.html", context
                        )
                        plain_message = render_to_string(
                            "emails/notify_user_set_test.txt", context
                        )

                        msg = EmailMultiAlternatives(
                            subject=subject,
                            body=plain_message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            to=[user.email],
                        )

                        msg.attach_alternative(html_message, "text/html")
                        msg.send()

                        notify = EmailTestNotyficateUser(user=user, test=test)
                        sended_emails.append(notify)
                except Exception as e:
                    print(e)
                    continue
            
            if sended_emails:
                EmailTestNotyficateUser.objects.bulk_create(sended_emails)

    except Exception as e:
        print(f"Retrying... Attempt {self.request.retries + 1}")
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
    