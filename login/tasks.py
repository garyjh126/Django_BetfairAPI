# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import Celery


app = Celery('tasks', broker='amqp://localhost//', backend='db+sqlite:///results.sqlite')

@app.task
def reverse(string):
    return string[::-1]