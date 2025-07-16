from celery import Celery

app = Celery('main')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True, ignore_results=True)
def debug_task(self):
    print(f'Request: {self.request!r}')