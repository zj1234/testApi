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
    #print("ws")
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


    