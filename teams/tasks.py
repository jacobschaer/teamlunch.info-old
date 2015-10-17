from celery import Celery
from django.conf import settings

app = Celery('tasks', broker='amqp://{broker_username}:{broker_password}@localhost//'.format(
	broker_username=settings.CELERY_BROKER_USERNAME,
	broker_password=settings.CELERY_BROKER_PASSWORD
))

@app.task
def add(x, y):
    return x + y
