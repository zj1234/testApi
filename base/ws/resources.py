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
from base.models import Client, Car

class WsView(APIView):
    print("ws")
    authentication_classes = (BenchmarkTokenAuthentication,)
    def get(self, request, format=None):
        print("wsget")
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
        return ApiErrorCodesMessages.AuthData("method")
    
    @staticmethod
    def getClients(value):
        if value=="base":
            clients=Client.objects.values("name", "cell", "mail")
        else:
            clients=Client.objects.values("name", "cars")
        return {"clientes":clients}


    