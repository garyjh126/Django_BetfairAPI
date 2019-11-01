# import string

from __future__ import absolute_import

from celery import shared_task
from .models import SportsAPI, Form
from celery import shared_task
import time
from .api_logic.SportsAPI import SportsAPI_
from .api_logic.Form1 import Form_
from django.http import HttpResponse
from django.apps import apps
import pickle


@shared_task
def timer_tick(bookRequestList):
    
    while True:
        Form_.ListMarketBook(SportsAPI_, bookRequestList)
        Form_.CheckMarkets()
        time.sleep(5)
        print("repeat")
