from __future__ import absolute_import

from .models import SportsAPI, Form
import time
from .api_logic.SportsAPI import SportsAPI_
from .api_logic.Form1 import Form_
from django.http import HttpResponse
from django.apps import apps


def timer_tick_test(bookRequestList):

    Form_.ListMarketBook(SportsAPI_, bookRequestList)
    Form_.CheckMarkets()
