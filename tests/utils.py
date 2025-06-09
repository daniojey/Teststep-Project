from datetime import date

from django.utils.timezone import localtime
from main import settings
from users.models import EmailTestNotyficateUser, User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_emails_from_users(users_data, test):
    if users_data:
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


def check_min_datetime(object_date, local_date):
    print(object_date)
    print(local_date)

    if object_date < local_date:
        return f"{object_date.date()}T{object_date.time().strftime("%H:%M")}"
    else:
        return f"{local_date.date()}T{local_date.time().strftime("%H:%M")}"

