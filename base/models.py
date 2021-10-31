from __future__ import unicode_literals

from django.db import models
from utils.date import datetimeExpired
from django.db.models import JSONField

class Token(models.Model):

    cliente_usuario_id = models.IntegerField(unique=True)
    token = models.CharField(("Key"), max_length=40, primary_key=True)
    created = models.DateTimeField(("created"), auto_now_add=True)
    expired = models.DateTimeField(("expired"),default=datetimeExpired())

    class Meta:
        managed = False
        db_table = 'token'


class Client(models.Model):

    cliente_usuario_id = models.IntegerField(unique=True, primary_key=True)
    perfil_id=models.IntegerField(blank=False)
    name = models.TextField(blank=False)
    mail = models.TextField()
    cell=models.IntegerField()
    cars =JSONField()

    class Meta:
        managed = False
        db_table = 'client'
    
class Car(models.Model):

    id_ingreso = models.IntegerField(unique=True, primary_key=True)
    model = models.TextField(blank=False)
    patente = models.TextField(blank=False)
    id_reparacion=JSONField()
    id_client =models.IntegerField(blank=False)

    class Meta:
        managed = False
        db_table = 'car'

class Repair(models.Model):

    id = models.IntegerField(unique=True, primary_key=True)
    id_car = models.IntegerField(blank=False)
    description=models.TextField(blank=False)
    entryDate=models.DateTimeField(blank=False)
    finalDate=models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'repair'


class Perfil(models.Model):

    id = models.IntegerField(blank=False, primary_key=True)
    name = models.TextField(blank=False)
    description = models.TextField(blank=False)

    class Meta:
        managed = False
        db_table = 'client'
