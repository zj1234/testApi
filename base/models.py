from __future__ import unicode_literals

from django.db import models
from utils.date import datetimeExpired


class Token(models.Model):

    cliente_usuario_id = models.IntegerField(unique=True)
    cliente_id = models.IntegerField(blank=False, default=1)
    token = models.CharField(("Key"), max_length=40, primary_key=True)
    name = models.TextField()
    created = models.DateTimeField(("created"), auto_now_add=True)
    expired = models.DateTimeField(("expired"),default=datetimeExpired())

    class Meta:
        managed = False
        db_table = 'base_token'