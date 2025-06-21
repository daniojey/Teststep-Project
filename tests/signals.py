from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Tests, Question

@receiver(post_save, sender=Tests)
def create_test_signal(sender, instance, created, raw, update_fields,**kwargs):
    if raw:
        return

    if created:
        print('СОЗДАН ТЕСТ', instance.name)
    else:
        print("НЕ создано")


@receiver(post_save, sender=Question)
def question_create_handler(sender, instance, raw, **kwargs):
    print('СОЗДАН ВОПРОС',  instance)