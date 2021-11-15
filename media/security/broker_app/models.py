from django.db import models

# Create your models here.
class Account(models.Model):
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
    user_id = models.IntegerField(default=1)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20)
    expire_date = models.DateField()
    data_size = models.IntegerField(default=250)

class Journal(models.Model):
    name = models.CharField(max_length=100)
    user_id = models.IntegerField(default=1)
    value = models.TextField()






