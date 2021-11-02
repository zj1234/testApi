# -*- coding: utf-8 -*-

"""
    @package main
    ===============
    @file    resources.py
    @class   * BenchmarksViewSet

    @author Aldo Cruz Romero  <acruz2094@gmail.com>

    @brief  * Clase ViewSet que permite devolver información.
    @date   nov/2021
    @todo       * Replicacion métodos de WebServices 
"""
from dateutil import tz
from pytz import timezone
from rest_framework.views import APIView
from datetime import datetime, time,date, timedelta
from rest_framework.response import Response
from django.utils.timezone import utc
from rest_framework.decorators import action
from .authentication import BenchmarkTokenAuthentication
from utils.error_api import ApiErrorCodesMessages
from base.models import Client, Car, Repair

"""
Clase para Vistas Generales de WebService
es necesario token y user con perfil de admin
@endpoints
http://0.0.0.0:8082/base/?token=?&method=getClients&user=?
http://0.0.0.0:8082/base/?token=?&method=getCarsClients&user=?
"""
class WsView(APIView):
    authentication_classes = (BenchmarkTokenAuthentication,)
    def get(self, request, format=None):
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
@endpoints
http://0.0.0.0:8082/base-new/?token=?&user=?&nombre=?&mail=?&celular=?
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
            Client.objects.create(perfil_id=1, name=clientName, mail=mail, cell=cell)   
        except Exception as e:
            return ApiErrorCodesMessages.NoInsert()
        return Response({"detalle":"Nuevo Usuario Ingresado"})
"""
Clase para Vistas de Nuevos Autos
es necesario token y user con perfil de admin
@endpoint
http://0.0.0.0:8082/base-newCar/?token=?&user=?&clientId=?&modelo=?&patente=?
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

  
"""
Clase para Vistas de Nueva Reparacion de Auto
es necesario token y user con perfil de admin
@endpoint
http://0.0.0.0:8082/base-newRepairCar/?token=?&user=?&patente=?&detail=?
"""
class WsNewRepairCarView(APIView):
    authentication_classes = (BenchmarkTokenAuthentication,)
    def get(self, request, format=None):        
        #VERIFICA FORMATO DE PATENTE
        try:
            patente=request.query_params["patente"]
            detail=request.query_params["detail"]
            try:
                validPatente=str(patente).split("-")
                if len(validPatente)!=3:
                    ApiErrorCodesMessages.BadFormat()
            except Exception as e:
                ApiErrorCodesMessages.BadFormat()
        except Exception as e:
            return ApiErrorCodesMessages.AuthData(str(e))
        _dataCar=(Car.objects.filter(patente=patente).values())
        #VALIDA SI EXISTE AUTO
        if not _dataCar:
            return ApiErrorCodesMessages.NoData()
        #VALIDA A QUE CLIENTE PERTENECE AUTO
        _dataClient=(Client.objects.filter(cliente_usuario_id=_dataCar.get()["id_client"]).values())
        if not _dataClient:
            return ApiErrorCodesMessages.NoData()
        data=WsNewRepairCarView.createRepair(_dataClient.get(), _dataCar, detail)
        if data is False:
            return ApiErrorCodesMessages.NoInsert()
        return Response(data)
    """
    @brief Método estático que inserta o actualiza tablas de reparacion 
    para el ingreso de una nueva repacion por auto por cliente,
    @return void
    """
    @staticmethod
    def createRepair(client, car, detail):
        try:
            Repair.objects.create(id_car=car.get()["id_ingreso"], description=detail)
        except Exception as e:
            return False
        try:
            idRepair=int(Repair.objects.values().latest('id')["id"])
            car.update(id_reparacion=idRepair)
        except Exception as e:
            return False
        dateRepair=str(datetime.now(timezone('America/Santiago')).replace(tzinfo=utc))
        return {"detalle":"Nueva Reparacion Ingresada de "+client["name"]+\
             "de auto "+car.get()["model"]+" "+car.get()["patente"] +" con fecha de ingreso "+dateRepair}

"""
Clase para Vistas de Nueva Reparacion de Auto
es necesario token y user con perfil de admin
@endpoint
http://0.0.0.0:8082/base-allRepairs/?token=?&user=?
"""
class WsAllRepairsView(APIView):
    authentication_classes = (BenchmarkTokenAuthentication,)
    def get(self, request, format=None):
        return Response({"arreglos totales":Repair.objects.values_list("id", "description", "entryDate").order_by("-entryDate")  })
