from __future__ import unicode_literals

from django.db import models

# Create your models here.

class auth_user(models.Model):

    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    group_id = models.IntegerField()
