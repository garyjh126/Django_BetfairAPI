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

    class Meta:
        ordering = ('marketStartTime',)


class Runner(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    selectionId = models.CharField(max_length=50, primary_key=True)
    runnerName = models.CharField(max_length=50)
    runnerStatus = models.CharField(max_length=50)

    def __str__(self):
        return self.selectionId

    