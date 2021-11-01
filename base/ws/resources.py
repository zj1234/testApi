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

"""
Clase para Vistas Generales de WebService
es necesario token y user con perfil de admin
"""
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
        #SEGUN METODO DE ENTRADA OBTENDRA CLIENTES O VEHICULOS POR CLIENTES
        if method=="getClients" or method=="getCarsClients":
            values=""
            if method=="getClients":
                values="base"
            data= WsView.getClients(values)
            return Response(data)
        #SEGUN METODO LLAMA REPARACION DE AUTOS
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
    """
    @brief Método estático que levanta petición de todos los clientes,
    @return void
    """
    @staticmethod
    def getClients(value):
        if value=="base":
            clients=Client.objects.values("cliente_usuario_id","name", "cell", "mail")
        else:
            clients=Client.objects.values("cliente_usuario_id","name", "cars")
        return {"clientes":clients}
    """
    @brief Método estático que levanta petición de todos los Autos Reparados,
    @return void
    """
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
"""
Clase para Vistas de Nuevos clientes
es necesario token y user con perfil de admin
"""
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
"""
Clase para Vistas de Nuevos Autos
es necesario token y user con perfil de admin
"""
class WsNewCarView(APIView):
    authentication_classes = (BenchmarkTokenAuthentication,)
    def get(self, request, format=None):
        #VERIFICA VARIABLES DE CLIENTE PARA REALIZAR INGRESO POR CLIENTE
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
        #VERIFICA VARIABLES DE AUTO
        try:
            requestData= request.query_params
            model=requestData["modelo"]
            patente=requestData["patente"]
        except Exception as e:
            return ApiErrorCodesMessages.AuthData(str(e))
        #OBTIENE INFORMACION DE CLIENTE SEGUN VARIABLES
        _client=Client.objects.filter(**{key:value}).values()
        if not _client:
            return ApiErrorCodesMessages.NoData()
        data =WsNewCarView.createNewCar(_client, model, patente)
        return Response(data)
    
    """
    @brief Método estático que inserta o actualiza tablas de auto y cliente 
    para el ingreso de un nuevo auto por cliente,
    @return void
    """
    @staticmethod
    def createNewCar(_client, model, patente):
        #VALIDA SI CLIENTE POSEE AUTOS, SI NO, LO AGREGA
        #INSERTA O ACTUALIZA EN TABLA DE AUTOS Y DE CLIENTE
        if _client.get()["cars"] is None or _client.get()["cars"]=="":
            try:
                car=Car.objects.create(model=model, patente=patente, \
                    id_client=_client.get()["cliente_usuario_id"])
                carDict={"autos":[{"modelo":model, "patente":patente}]}
                _client.update(cars=carDict)
            except Exception as e:
               return ApiErrorCodesMessages.NoInsert()
        else:
            try:
                car=Car.objects.create(model=model, patente=patente, \
                    id_client=_client.get()["cliente_usuario_id"])
                arrayCars= _client.get()["cars"]["autos"]
                arrayCars.append({"modelo":model, "patente":patente})
                car={"autos":arrayCars}
                _client.update(cars=car)
            except Exception as e:
               return ApiErrorCodesMessages.NoInsert()
        #_client.create(perfil_id=1, name=clientName, mail=mail, cell=cell)
        return {"detalle":"Nuevo Auto Ingresado de "+_client.get()["name"]}

  

    