# import string

from __future__ import absolute_import

from celery import shared_task
from .models import SportsAPI
from celery import shared_task
import time
from .api_logic.SportsAPI import *
from .api_logic.Form1 import *
from django.http import HttpResponse

@shared_task
def timer_tick(sapi_model_id):
    print("sapi_model_id", sapi_model_id)
    sapi_model = SportsAPI.objects.get(pk=sapi_model_id)
    
    while True:
        ListMarketBook(sapi_model)
        CheckMarkets()
        time.sleep(5)
        print("repeat")

   
