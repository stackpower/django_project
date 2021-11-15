from django.db import models
import datetime

# Create your models here.
class Account(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=50)
    sure_name = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    permission = models.IntegerField(default=2)
    status = models.CharField(max_length=20, default='enable')
    expire_date = models.DateField()
    ib_user_name = models.CharField(max_length=20, default='some string')
    ib_id = models.IntegerField()
    ib_port = models.IntegerField()
    saxo_token = models.TextField()
    saxo_account_key = models.TextField(default='')


class Security(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(default=1)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20)
    trading_day = models.DateField()
    expire_date_1 = models.DateField()
    expire_date_2 = models.DateField()
    expire_date_3 = models.DateField()
    data_size = models.IntegerField(default=250)

class Journal(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    user_id = models.IntegerField(default=1)

class Journal_Data(models.Model):
    id = models.AutoField(primary_key=True)
    journal_id = models.IntegerField(default=1)
    security_id = models.IntegerField(default=1)
    symbol = models.CharField(default="", max_length=50)
    side = models.CharField(default="", max_length=50)
    create_date = models.DateField(blank=True)
    max_p = models.FloatField(default=0)
    min_p = models.FloatField(default=0)
    percent = models.FloatField(default=0)
    last = models.FloatField(default=0)
    last_percent = models.FloatField(default=0)







