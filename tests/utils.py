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

        # for user in users:
        #     try:
        #         if user.is_staff or not EmailTestNotyficateUser.objects.filter(user=user, test=test).exists():
        #             context = {
        #                 "user": user,
        #                 "test": test,
        #             }

        #             html_message = render_to_string("emails/notify_user_set_test.html", context)
        #             plain_message = render_to_string("emails/notify_user_set_test.txt", context)

        #             msg = EmailMultiAlternatives(
        #                 subject=subject,
        #                 body=plain_message,
        #                 from_email=settings.DEFAULT_FROM_EMAIL,
        #                 to=[user.email]
        #             )

        #             msg.attach_alternative(html_message, "text/html")
        #             msg.send()

        #             notify =EmailTestNotyficateUser.objects.create(user=user, test=test)
        #             notify.save()
        #         else:
        #             print("ВЖЕ існує або адмін")

        #     except Exception as e:
        #         print(e)
        #         continue
