from django.db import models
from django.contrib.auth.models import User

class Login(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Market(models.Model):
    marketStartTime = models.CharField(max_length=50)
    marketId = models.CharField(max_length=50, primary_key=True)
    marketStatus = models.CharField(max_length=50)
    inPlay = models.CharField(max_length=50)
    course = models.CharField(max_length=50)
    back = models.FloatField(max_length=50)
    lay = models.FloatField(max_length=50)

    # marketStartTime = '', marketId='', marketStatus='', inPlay='',course='',back=0.0,lay=0.0    
    
    class Meta:
        ordering = ('marketStartTime',)


class Runner(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    selectionId = models.CharField(max_length=50, primary_key=True)
    runnerName = models.CharField(max_length=50)
    runnerStatus = models.CharField(max_length=50)

    # market=market, selectionId='', runnerName='', runnerStatus=''

    def __str__(self):
        return self.selectionId

    class Meta: 
        unique_together = (('market', 'selectionId'),)


class SportsAPI(models.Model):
    id = models.AutoField(primary_key=True)
    payload = models.CharField(max_length=400, unique=False)
    url = models.CharField(max_length=100, unique=False)
    headers = models.CharField(max_length=200, unique=False)
    path_cert = models.CharField(max_length=200, unique=False)

    def __str__(self):
        return self.payload

class Form(models.Model):
    id = models.AutoField(primary_key=True)
    request = models.CharField(max_length=400, unique=False)
    params = models.CharField(max_length=100, unique=False)
    start_time = models.CharField(max_length=200, unique=False)

class MarketDictionaryM(models.Model):
    market_id = models.CharField(primary_key = True, max_length=50)
    market_status = models.CharField(max_length = 50, default="", editable=False)
    market_inPlay = models.CharField(max_length = 50, default="", editable=False)
    market_removed = models.BooleanField(max_length = 50, default=False)

class RunnerDictionaryM(models.Model):
    runner_id = models.CharField(primary_key = True, max_length=50)
    runner_status = models.CharField(max_length = 50, default="", editable=False)
    runner_backPrice= models.CharField(max_length = 50, default="", editable=False)
    runner_layPrice = models.CharField(max_length = 50, default="", editable=False)
