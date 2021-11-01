# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from utils.date import datetimeExpired
from django.db.models import JSONField

class Auth(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.TextField(blank=False)
    passText =  models.TextField(blank=False)
    created = models.DateTimeField(("created"), auto_now_add=True)
    expired = models.DateTimeField(("expired"),default=datetimeExpired())

    class Meta:
        managed = False
        db_table = 'auth'

