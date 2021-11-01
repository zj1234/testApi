# -*- coding: utf-8 -*-

"""
    @package main
    ===============
    @file    resources.py
    @class   * BenchmarksViewSet

    @author Aldo Cruz Romero  <acruz2094@gmail.com>

    @brief  * BenchmarksViewSet: Clase ViewSet que permite devolver información.
    @date   Jun/2019
    @todo       * Replicacion métodos de WebServices 
"""
from dateutil import tz
from rest_framework.views import APIView
from datetime import datetime, time,date, timedelta
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone as dt
from .authentication import BenchmarkTokenAuthentication
from utils.error_api import ApiErrorCodesMessages
from base.models import Client, Car, Repair

class WsView(APIView):
    print("ws")
    authentication_classes = (BenchmarkTokenAuthentication,)
    def get(self, request, format=None):
        #print("wsget")
        try:
            requestData= request.query_params
            method=requestData["method"]
            user=requestData["user"]
        except Exception as e:
            return ApiErrorCodesMessages.AuthData(str(e))
        if method=="getClients" or method=="getCarsClients":
            values=""
            if method=="getClients":
                values="base"
            data= WsView.getClients(values)
            return Response(data)
        if method=="repairsByCar":
            try:
                patente=requestData["patente"]
                client=requestData["client"]
            except Exception as e:
                return ApiErrorCodesMessages.AuthData(str(e))
            data=WsView.getCarRepairs(client, patente)
            if data is False:
                return ApiErrorCodesMessages.NoData()
            return Response(data)
        return ApiErrorCodesMessages.AuthData("method")
    
    @staticmethod
    def getClients(value):
        if value=="base":
            clients=Client.objects.values("cliente_usuario_id","name", "cell", "mail")
        else:
            clients=Client.objects.values("cliente_usuario_id","name", "cars")
        return {"clientes":clients}
    
    @staticmethod
    def getCarRepairs(client, value):
        _carClients=Car.objects.values("id_ingreso").filter(id_client=client, patente=value)
        if _carClients:
            idCar=(_carClients.get()["id_ingreso"])
            repairsCar=(Repair.objects.filter(id_car=idCar).values("description", \
                "entryDate", "finalDate"))
            return {"reparaciones":repairsCar}
        else:
            return False

class WsNewView(APIView):
    authentication_classes = (BenchmarkTokenAuthentication,)
    def get(self, request, format=None):
        try:
            requestData= request.query_params
            clientName=requestData["nombre"]
            mail=requestData["mail"]
            cell=requestData["celular"]
        except Exception as e:
            return ApiErrorCodesMessages.AuthData(str(e))
        try:
            insert=Client.objects.create(perfil_id=1, name=clientName, mail=mail, cell=cell)   
        except Exception as e:
            return ApiErrorCodesMessages.NoInsert()
        return Response({"detalle":"Nuevo Usuario Ingresado"})

class WsNewCarView(APIView):
    authentication_classes = (BenchmarkTokenAuthentication,)
    def get(self, request, format=None):
        try:
            if 'nombre' in request.query_params:
                key="name"
                value=request.query_params["nombre"]
            if 'mail' in request.query_params:
                key="mail"
                value=request.query_params["mail"]
            if 'clientId' in request.query_params:
                key="cliente_usuario_id"
                value=request.query_params["clientId"]
        except Exception as e:
            return ApiErrorCodesMessages.NoContinue()
        try:
            requestData= request.query_params
            modelo=requestData["modelo"]
            patente=requestData["patente"]
        except Exception as e:
            return ApiErrorCodesMessages.AuthData(str(e))
        print(key,value)
        print(Client.objects.filter(**{key:value}))
            
        return Response('hola')


  

    