# -*- coding: utf-8 -*-

import datetime
import xml.etree.ElementTree as ET
from datetime import timedelta, datetime, time
import pytz
from django.http import HttpResponse
from pytz import timezone as pytztimezone
from common.models.public import ObjetivoConfig, ClienteUsuario, Objetivo, Codigo, PeriodoMarcado, Intervalo, \
    Nodo, Cliente, ClienteMapaClienteObjetivo, Monitor, HorarioItem, Horario, ClienteMapaSubclienteUsuario,\
    ClienteMapaSubclienteObjetivo, Servicio
from common.models.procesado import Evento
from public.models import ControlPeticiones, ControlPeticionesUsuario
from utils.date import formatDateToTimezone
from utils.error_codes_api import ApiErrorCodesMessages
from utils.network import Network
from utils.constants import ConstantCodes, ObjectivesSpecialList
from common.models.cache import UltimoEstado
import numpy as np
import math

class BenchmarksSerializer:

    """
    @brief Método que permite retornar un string con el nombre del evento.
    @param eventoId String con la información del eventoId
    @return String con el nombre del evento según eventoId solicitado.
    """
    @staticmethod
    def nameEvent(eventoId):
        nombre = ''
        if eventoId == '1':
            nombre = 'uptime'
        elif eventoId == '2':
            nombre = 'downtime'
        elif eventoId == '3':
            nombre = 'downtime parcial'
        elif eventoId == '7':
            nombre = 'no monitoreo'
        elif eventoId == '9':
            nombre = 'evento cliente'
        return nombre

    @staticmethod
    def registerLog(request, token, clienteId, objetivoId, metodo):
        """
        Registra en base interna al cliente en caso de tener existo en consulta de webservice.

        @param  request         Request con información para el método.
        @param  token           Token con el cual se valido el usuario.
        @param  clienteId       Cliente id del usuario.
        @param  objetivoId      Objetivo id del objetivo consultado.
        @param  metodo          Método webservice consultado.

        """
        ipCurrent = Network.getClientIp(request)
        # Registrar acceso en LogAuth
        # LogWS.createData(clienteId, ipCurrent, token, objetivoId, metodo)

    """
    @brief Método que permite validar si un registro de la tabla procesado.evento es
    correcto o no con sus códigos de error respectivos.
    @param eventStatus String con la información del estado del paso
    @param codesOK Lista con códigos Ok
    @return True si es correcto, false en caso contrario
    """

    @staticmethod
    def isStatusOkPerStep(eventStatus, codesOK):
        # Declarar variable a devolver
        isOK = False
        # Dividir los estados en arreglo de patrones cortando desde las comas
        statusPatterns = eventStatus.split(",")
        # Si la cantidad es mayor a uno significa que tiene más de 2 patrones
        if len(statusPatterns) > 1:
            # Aquí se realiza una validación para saber si lo que contiene
            # de patrones está dentro de códigos ok para ser true, en caso
            # contrario es false
            isOK = next((False for statusPattern in statusPatterns \
                         if not int(statusPattern) in codesOK), True)
            """isOK = next((True for statusPattern in statusPatterns \
                         if int(statusPattern) in codesOK), False)"""

        else:
            # Sino es que tiene un solo valor y se comprueba que es ok
            if int(eventStatus) in codesOK:
                isOK = True
            else:
                # Si es false entonces se sale automáticamente
                # debido a que hay algún problema
                isOK = False
        # Retornar variable
        return isOK

    @staticmethod
    def isStatusOk(eventStatus, codesOK, steps):
        """
        Método que permite validar si un registro de la tabla procesado.evento es
        correcto o no con sus códigos de error respectivos.
        @param eventStatus String con la información de los estados de los pasos
        @param codesOK Lista con códigos Ok
        @param stepsInfo Información de pasos de objetivo
        @return True si es correcto, false en caso contrario
        """
        # Declarar variable a devolver
        isOK = False
        # Transformar el string de eventos
        eventStatusSplit = eventStatus.split("|")
        # Recorrer el split de eventos
        for index, status in enumerate(eventStatusSplit):
            # Obtener la visibilidad según objetivos
            visible = steps[index]["visible"]
            # Si el paso es visible
            if visible:
                # Dividir los estados en arreglo de patrones cortando desde las comas
                statusPatterns = status.split(",")
                # Si la cantidad es mayor a uno significa que tiene más de 2 patrones
                if len(statusPatterns) > 1:
                    # Aquí se realiza una validación para saber si lo que contiene
                    # de patrones está dentro de códigos ok para ser true, en caso
                    # contrario es false
                    isOK = next((True for statusPattern in statusPatterns \
                                 if int(statusPattern) in codesOK), False)
                else:
                    # Sino es que tiene un solo valor y se comprueba que es ok
                    if int(status) in codesOK:
                        isOK = True
                    else:
                        # Si es false entonces se sale automáticamente
                        # debido a que hay algún problema
                        isOK = False
                        break
        # Retornar variable
        return isOK

    @staticmethod
    def validathor(request):
        if not 'objetivoId' or not 'horarioId' or not 'key' or not 't' in request.query_params:
            return ApiErrorCodesMessages.AuthException()
        try:
            objId = int(request.query_params["objetivoId"])
            horarioId = int(request.query_params["horarioId"])
            key = request.query_params['key']
            time = request.query_params['t']
        except ValueError:
            return ApiErrorCodesMessages.ApiQueryError('Existe un parametro que no corresponde a su tipo.')
        varDict = dict()
        varDict["objId"] = objId
        varDict["horarioId"] = horarioId
        varDict["fechaInicio"] = None
        varDict["fechaTermino"] = None
        varDict["key"] = key
        varDict["time"] = time
        return varDict

    @staticmethod
    def validathorCustom(request):
        if not 'objetivoId' or not 'horarioId' or not 'fechaInicio' or not 'key' or not 'fechaTermino' in request.query_params:
            return ApiErrorCodesMessages.AuthException()
        try:
            objId = int(request.query_params['objetivoId'])
            fechaInicio = request.query_params['fechaInicio']
            fechaTermino = request.query_params['fechaTermino']
            horarioId = int(request.query_params["horarioId"])
            key = request.query_params['key']
            #time = request.query_params['t']
        except ValueError:
            return ApiErrorCodesMessages.ApiQueryError('Existe un parametro que no corresponde a su tipo.')
        varDict = dict()
        varDict["objId"] = objId
        varDict["fechaInicio"] = fechaInicio
        varDict["fechaTermino"] = fechaTermino
        varDict["horarioId"] = horarioId
        varDict["key"] = key
        varDict["time"] = None
        return varDict

    @staticmethod
    def validathorPasoId(request):
        if not 'pasoId' in request.query_params:
            return ApiErrorCodesMessages.AuthException()
        try:
            pasoId = int(request.query_params["pasoId"])
        except ValueError:
            return ApiErrorCodesMessages.ApiQueryError('Existe un parametro que no corresponde a su tipo.')
        return pasoId

    @staticmethod
    def validathorNodoId(request):
        if not 'nodoId' in request.query_params:
            return ApiErrorCodesMessages.AuthException()
        try:
            nodoId = int(request.query_params["nodoId"])
        except ValueError:
            return ApiErrorCodesMessages.ApiQueryError('Existe un parametro que no corresponde a su tipo.')
        return nodoId

    @staticmethod
    def validKey(key):
        """
                    validKey
                     @param  key           key para ingresar al método
                    """

        f = open("config/auth.key", "r")
        if not f.read() == key:
            return False
        else:
            return True

    @staticmethod
    def controlValidathor(objId, clientId, key, metodo):
        """
        Validador de intervalo de petición (1 cada 10 min por objetivo)
        @param  objId        ObjetivoId del objetivo.

        """
        if not clientId:
            return 0
        if not BenchmarksSerializer.validKey(key):
            return 3
        # response para obtener y validar datos obtenido desde el request(cliente y objetivo realmente esten asociados).
        cliente = Cliente.objects.using('public').filter(cliente_id=clientId)
        objetivo = Objetivo.objects.using('public').filter(objetivo_id=objId)

        if not cliente or not objetivo:
            return 1
        if metodo !="special":
            existMapaClienteObjetivo = ClienteMapaClienteObjetivo.objects.using('public') \
                .values('cliente_mapa_cliente_objetivo_id').filter(cliente=cliente, objetivo=objetivo).exists()
            if existMapaClienteObjetivo is False:
                return 2
        if objId is not None:
            """try:
                with transaction.atomic():
                    datetimeNow = datetime.utcnow().replace(tzinfo=pytz.UTC) - timedelta(minutes=10)
                    dateUltimaPeticion = ControlPeticiones.objects.select_for_update().values('ultima_peticion').get(objetivo_id=objId, ruta='indicadores')[
                        'ultima_peticion']
                if datetimeNow > dateUltimaPeticion:
                    ControlPeticiones.updateData(objId, datetime.utcnow().replace(tzinfo=pytz.UTC), 'indicadores')
                    return [True, objetivo, cliente]
            except ControlPeticiones.DoesNotExist, ValueError:
                ControlPeticiones.createData(objId, datetime.utcnow().replace(tzinfo=pytz.UTC), 'indicadores')
                return [True, objetivo, cliente]"""
            return [True, objetivo, cliente]

    @staticmethod
    def bodyResponse(request, objId, horarioId, metodo, key, time,
                     fechaInicio, fechaTermino, pasoId, isForStep, isForParcial, isForResumen, clientId=None):
        """
        Cuerpo del response para los métodos Disponibilidad (detalle o resumen), pudiendo ser (global o parcial), y finalmente agrupados por (objetivo o paso).

        @param  request                 Request con información para el método.
        @param  objId                   Objetivo id del objetivo consultado.
        @param  metodo                  Método webservice consultado.
        @param  pasoId                  Paso id relacionado al objetivo consultado.
        @param  horarioId               Horario id relacionado al objetivo consultado.
        @param  isForStep               Verificador para que método webservice se esta consultando.
        @param  isParcial               Verificador para que método webservice se esta consultando.
        @param  isForResumen            Verificador para que método webservice se esta consultando.
        @param  clientId                Verificador id del cliente.
        """
        if clientId is None:
            # Validador de intervalo de petición (1 cada 10 min por objetivo)
            userClientId = request.user["userClientId"]
            clientId = request.user["clientId"]
            
        else:
            # Validador de intervalo de petición (1 cada 10 min por objetivo)
            userClientId = request.query_params["user"]
            clientId = clientId


        controlValidor = BenchmarksSerializer.controlValidathor(objId, clientId, key, metodo)
        if controlValidor == 0:
            return 0
        if controlValidor == 1 or controlValidor == 2:
            return 1
        if controlValidor == 3:
            return 2
        iscontrolValidor = controlValidor[0]
        if iscontrolValidor is False:
            return 3
        # obtener objetivo desde validador
        objetivo = controlValidor[1]
        cliente = controlValidor[2]

        if time != None:
            if time == 'h':
                if 'Rendimiento' in metodo or metodo == 'AvailabilityHour':
                    #dateEnd = datetime.now() - timedelta(hours=2)
                    dateEnd = datetime.now()
                    dateStart = datetime.now() - timedelta(hours=3)
                else:
                    dateStart = datetime.now() - timedelta(hours=1)
                    dateEnd = datetime.now()
            elif time == '3h':
                dateEnd = datetime.now()
                dateStart = datetime.now() - timedelta(hours=3)
            elif time == 'd':
                dateStart = datetime.now() - timedelta(days=1)
                dateEnd = datetime.now()
                if 'ResumenRendimiento' in metodo:
                    """or 'ResumenDisponibilidad' in metodo:"""
                    dtNow = datetime.now()
                    day = dtNow.day
                    """dateStart = datetime.now() - timedelta(weeks=1)
                    dateEnd = datetime.now()"""
                    try:
                        dateStart = dtNow.replace(day=day + 1, hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
                    except ValueError:
                        dateStart = dtNow.replace(month=dtNow.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(
                            days=1)
                    try:
                        dateEnd = dtNow.replace(day=day + 1, hour=0, minute=0, second=0, microsecond=0)
                    except ValueError:
                        dateEnd = dtNow.replace(month=dtNow.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            elif time == '3d':
                dateStart = datetime.now() - timedelta(days=3)
                dateEnd = datetime.now()
                if 'ResumenRendimiento' in metodo:
                    """or 'ResumenDisponibilidad' in metodo:"""
                    dtNow = datetime.now()
                    day = dtNow.day
                    """dateStart = datetime.now() - timedelta(weeks=1)
                    dateEnd = datetime.now()"""
                    try:
                        dateStart = dtNow.replace(day=day + 1, hour=0, minute=0, second=0, microsecond=0) - timedelta(days=3)
                    except ValueError:
                        dateStart = dtNow.replace(month=dtNow.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(
                            days=3)
                    try:
                        dateEnd = dtNow.replace(day=day + 1, hour=0, minute=0, second=0, microsecond=0)
                    except ValueError:
                        dateEnd = dtNow.replace(month=dtNow.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            elif time == 'w':
                dtNow = datetime.now()
                day = dtNow.day
                if 'getDetalleDisponibilidadGlobalObjetivoDowntime' == metodo \
                        or 'getDetalleDisponibilidadParcialObjetivoDowntime' == metodo:
                    dateStart = datetime.now() - timedelta(weeks=1)
                    dateEnd = datetime.now()
                else:
                    dateStart = datetime.now() - timedelta(weeks=1)
                    dateEnd = datetime.now()
                    #dateStart = dtNow.replace(day = day + 1, hour = 0, minute = 0, second = 0, microsecond = 0) - timedelta(weeks=1)
                    #dateEnd = dtNow.replace(day = day + 1, hour = 0, minute = 0, second = 0, microsecond= 0)
            elif time == '6h':
                dateEnd = datetime.now()
                dateStart = datetime.now() - timedelta(hours=6)
            elif time == '12h':
                dateEnd = datetime.now()
                dateStart = datetime.now() - timedelta(hours=12)
            elif time == '2d':
                dateStart = datetime.now() - timedelta(days=2)
                dateEnd = datetime.now()
                if 'ResumenRendimiento' in metodo:
                    """or 'ResumenDisponibilidad' in metodo:"""
                    dtNow = datetime.now()
                    day = dtNow.day
                    """dateStart = datetime.now() - timedelta(weeks=1)
                    dateEnd = datetime.now()"""
                    try:
                        dateStart = dtNow.replace(day=day + 1, hour=0, minute=0, second=0, microsecond=0) - timedelta(days=2)
                    except ValueError:
                        dateStart = dtNow.replace(month=dtNow.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(
                            days=2)
                    try:
                        dateEnd = dtNow.replace(day=day + 1, hour=0, minute=0, second=0, microsecond=0)
                    except ValueError:
                        dateEnd = dtNow.replace(month=dtNow.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            elif time == '2h':
                dateEnd = datetime.now()
                dateStart = datetime.now() - timedelta(hours=6)
            elif time == 'M':
                dtNow = datetime.now()
                day = dtNow.day
                if 'getDetalleDisponibilidadGlobalObjetivoDowntime' == metodo \
                        or 'getDetalleDisponibilidadParcialObjetivoDowntime' == metodo:
                    dateStart = datetime.now() - timedelta(months=1)
                    dateEnd = datetime.now()
                else:
                    dateStart = datetime.now() - timedelta(months=1)
                    dateEnd = datetime.now()
                    #dateStart = dtNow.replace(day = day + 1, hour = 0, minute = 0, second = 0, microsecond = 0) - timedelta(weeks=1)
                    #dateEnd = dtNow.replace(day = day + 1, hour = 0, minute = 0, second = 0, microsecond= 0)
        else:
            if fechaInicio > fechaTermino:
                return 8
            dateStart = datetime.strptime(fechaInicio, "%Y-%m-%d")
            dateEnd = datetime.strptime(fechaTermino, "%Y-%m-%d") + timedelta(days=1)
            """if dateEnd - dateStart > timedelta(days=2):
                return 9"""
        weekDay = dateStart.weekday() + 1
        # Obtener y validar el intervalo asociado al objetivo (úsado para obtener una fecha, para luego usarla como limite en el response de resultados)
        """
        try:
            interval_id = ObjetivoConfig.objects.using('public').values('intervalo') \
                .get(objetivo=objId, es_ultima_config=True)['intervalo']
        except ObjetivoConfig.DoesNotExist:
            return 5

        if not interval_id:
            return 5
        """
        # Obtener la zona horaria según el usuario
        clientUserLocalTime = ClienteUsuario.getTimeZoneValueById(userClientId)
        dateStartMonitors = dateStart
        dateEndMonitors = dateEnd
        if time != None and time == 'h':
            dateStart = dateStart.replace(tzinfo=pytz.UTC).astimezone(pytztimezone(clientUserLocalTime)).replace(
                tzinfo=None)
            dateEnd = dateEnd.replace(tzinfo=pytz.UTC).astimezone(pytztimezone(clientUserLocalTime)).replace(
                tzinfo=None)
        if time != None and time == '3h':
            dateStart = dateStart.replace(tzinfo=pytz.UTC).astimezone(pytztimezone(clientUserLocalTime)).replace(
                tzinfo=None)
            dateEnd = dateEnd.replace(tzinfo=pytz.UTC).astimezone(pytztimezone(clientUserLocalTime)).replace(
                tzinfo=None)
        if time != None and time == 'd':
            dateStart = dateStart.replace(tzinfo=pytz.UTC).astimezone(pytztimezone(clientUserLocalTime)).replace(
                tzinfo=None)
            dateEnd = dateEnd.replace(tzinfo=pytz.UTC).astimezone(pytztimezone(clientUserLocalTime)).replace(
                tzinfo=None)
        if time != None and time == '3d':
            dateStart = dateStart.replace(tzinfo=pytz.UTC).astimezone(pytztimezone(clientUserLocalTime)).replace(
                tzinfo=None)
            dateEnd = dateEnd.replace(tzinfo=pytz.UTC).astimezone(pytztimezone(clientUserLocalTime)).replace(
                tzinfo=None)
        if time != None and time == 'w':
            dateStart = dateStart.replace(tzinfo=pytz.UTC).astimezone(pytztimezone(clientUserLocalTime)).replace(
                tzinfo=None)
            dateEnd = dateEnd.replace(tzinfo=pytz.UTC).astimezone(pytztimezone(clientUserLocalTime)).replace(
                tzinfo=None)
        if time != None and time == '2d':
            dateStart = dateStart.replace(tzinfo=pytz.UTC).astimezone(pytztimezone(clientUserLocalTime)).replace(
                tzinfo=None)
            dateEnd = dateEnd.replace(tzinfo=pytz.UTC).astimezone(pytztimezone(clientUserLocalTime)).replace(
                tzinfo=None)
        if time != None and time == '6h':
            dateStart = dateStart.replace(tzinfo=pytz.UTC).astimezone(pytztimezone(clientUserLocalTime)).replace(
                tzinfo=None)
            dateEnd = dateEnd.replace(tzinfo=pytz.UTC).astimezone(pytztimezone(clientUserLocalTime)).replace(
                tzinfo=None)
        if time != None and time == '12h':
            dateStart = dateStart.replace(tzinfo=pytz.UTC).astimezone(pytztimezone(clientUserLocalTime)).replace(
                tzinfo=None)
            dateEnd = dateEnd.replace(tzinfo=pytz.UTC).astimezone(pytztimezone(clientUserLocalTime)).replace(
                tzinfo=None)
        listDates = list()
        isHorarioHabil = False
        if horarioId <> 0:
            try:
                horarios = Horario.objects.using('public').values('horario_id').filter(cliente=cliente)
                for horario in horarios:
                    if horario['horario_id'] == horarioId:
                        isHorarioHabil = True
                if isHorarioHabil:
                    horarioLink = HorarioItem.objects.using('public').values('link_horario_id').filter(
                        horario_id=horarioId,
                        link_horario_id__isnull=False)
                    if not horarioLink:
                        # en caso de querer obtener todos los horarios item, relacionados con el horario id, eliminar el filtro por 'dia_semana'.
                        horarioIncluido = HorarioItem.objects.using('public').filter(
                            es_incluido=True, horario_id=horarioId, dia_semana=weekDay).values('horario_id',
                                                                                               'es_incluido',
                                                                                               'fecha_inicio',
                                                                                               'fecha_termino',
                                                                                               'hora_inicio',
                                                                                               'hora_termino')
                else:
                    return 7
            except HorarioItem.DoesNotExist, Horario.DoesNotExist:
                return 6
            import datetime as dt
            horaEndAux = dt.time(0, 0, 0)
            horaAux = dt.time(0, 0, 0)
            listHour = list()
            dictHour = {}
            dictDates = {}

            if not horarioLink:
                for index, horario in enumerate(horarioIncluido):
                    if index == 0:
                        horaAux = horario['hora_inicio']
                        horaEndAux = horario['hora_termino']
                        if index == len(horarioIncluido) - 1:
                            dictHour = {'hora_inicio': horaAux, 'hora_termino': horaEndAux}
                            listHour.append(dictHour)
                    else:
                        if horario['hora_inicio'] <= horaAux:
                            horaEndAux = horario['hora_termino']
                        else:
                            dictHour = {'hora_inicio': horaAux, 'hora_termino': horaEndAux}
                            horaAux = horario['hora_inicio']
                            horaEndAux = horario['hora_termino']
                            listHour.append(dictHour)
                            if index == len(horarioIncluido) - 1:
                                dictHour = {'hora_inicio': horaAux, 'hora_termino': horaEndAux}
                                listHour.append(dictHour)

                for hour in listHour:
                    if hour['hora_inicio'] <> dt.time(0, 0, 0) and hour['hora_termino'] <> dt.time(0, 0, 0):
                        dateEnd = dateStart + timedelta(hours=hour['hora_termino'].hour)
                        dateStart = dateStart + timedelta(hours=hour['hora_inicio'].hour)
                    elif hour['hora_inicio'] == dt.time(0, 0, 0) and hour['hora_termino'] <> dt.time(0, 0, 0):
                        dateEnd = dateStart + timedelta(hours=hour['hora_termino'].hour)
                    elif hour['hora_inicio'] <> dt.time(0, 0, 0) and hour['hora_termino'] == dt.time(0, 0, 0):
                        dateStart = dateStart + timedelta(hours=hour['hora_inicio'].hour)
                    dictDates = {'fechaInicio': dateStart, 'fechaTermino': dateEnd}
                    listDates.append(dictDates)
        try:
            # Obtener los códigos Ok
            codesOK = Codigo.objects.using("public").filterCodesOK()
            # Obtener información de pasos
            steps = ObjetivoConfig.objects.using("public").stepIdAndNameAsJSON(objId, onlyVisible=True,
                                                                               addVisibleData=False)
        except Codigo.DoesNotExist:
            return 6

        # Diccionario base del objetivo
        dictElementObjetivo = {'Objetivo_Id': objId, 'Objetivo_Nombre': objetivo[0].nombre}

        # Obtener los nodos y monitores asociados a objetivo, y convertirlo a lista siempre y cuando no haya un nodo id definido
        """try:
            monitores = Monitor.objects.using("public") \
                .extra(tables=["objetivo_config"],
                       where=["objetivo_config.es_ultima_config = true",
                              "monitor.monitor_id = any(objetivo_config.monitor_id )",
                              "objetivo_config.objetivo_id= {}".format(objId)]) \
                .values("monitor_id", "nodo_id").distinct()
        except Monitor.DoesNotExist:
            return 6
        if not monitores:
            return 6
        for monitor in monitores:
                    nodo = Nodo.objects.using('public').values('nodo_id', 'nombre').filter(nodo_id=monitor['nodo_id'])
                    listNodo.append(nodo)"""
        try:
            monitor_1 = ObjetivoConfig.objects.using("public").filter(objetivo=objetivo,
                                                                      fecha_creacion__lt=dateStartMonitors).order_by(
                "-fecha_creacion").values("monitor_id")[:1]
            monitor_2 = ObjetivoConfig.objects.using("public").filter(objetivo=objetivo, fecha_creacion__gte=dateStartMonitors,
                                                                      fecha_creacion__lt=dateEndMonitors).values("monitor_id")
        except Monitor.DoesNotExist:
            return 6
        from itertools import chain
        monitoresQuery = chain(monitor_1, monitor_2)
        # lista para almacenar los eventos por paso.
        listNodo = list()
        listMonitor = list()
        for monitorQuery in monitoresQuery:
            for monitor_id in monitorQuery['monitor_id']:
                try:
                    monitor = Monitor.objects.using("public").filter(monitor_id=monitor_id).values("monitor_id", "nodo_id")
                except Monitor.DoesNotExist:
                    return 6
                nodo = Nodo.objects.using('public').values('nodo_id', 'nombre').filter(nodo_id=monitor[0]['nodo_id'])
                listNodo.append(nodo)
                listMonitor.append(monitor[0]['monitor_id'])
        listNodo = sorted(listNodo, key=lambda k: k[0]['nodo_id'])
        listNodoFinal = list()
        isFirst = True
        for index, nodo in enumerate(listNodo):
            if isFirst:
                listNodoFinal.append(nodo)
                isFirst = False
            else:
                if nodo[0]['nodo_id'] != listNodo[index - 1][0]['nodo_id']:
                    listNodoFinal.append(nodo)
        return [listDates, steps, listNodoFinal, clientUserLocalTime, codesOK, dateStart, dateEnd, dictElementObjetivo, cliente, objetivo, listMonitor]

    @staticmethod
    def patternAsJSON(objectiveId, onlyVisible=True):
        """
        Construye un json con los patrones extraidos del xml

        @param  objectiveId        ObjetivoId del objetivo.
        @param  onlyVisible        Variable para traer solo los pasos visibles

        """
        import xml.etree.cElementTree as et
        import xmltodict

        querySet = ObjetivoConfig.objects.using("public") \
            .values_list("xml_configuracion", flat=True) \
            .filterByObjIdAndLastConf(objectiveId)
        if querySet:
            # ElementTree para trabajar xml configuración
            xmlConfig = et.fromstring(querySet[0])
        else:
            return ApiErrorCodesMessages.WithoutData()
        patronList = list()
        # recorrer elemento según paso
        for element in xmlConfig.iter('paso'):
            stepDict = dict()
            stepDict["patrones"] = [xmltodict.parse(et.tostring(x, encoding="utf8", method="html"))["patron"] for x in
                                    element.findall("patron")]
            # Si el paso es visible
            visibleElement = element.attrib['visible'] if "visible" in element.attrib else None
            # Es visible cuando no se declara atributo visible o si contiene valor '1'
            stepIsVisible = True if visibleElement is None or visibleElement == "1" else False
            if onlyVisible:
                if stepIsVisible:
                    # Agregar a contenedor
                    patronList.append(stepDict)
        return patronList

    @staticmethod
    def round_half_up(n, decimals=0):
        multiplier = 10 ** decimals
        return math.floor(n * multiplier + 0.5) / multiplier


class IndicadorSerializer:


    @staticmethod
    def hours_aligned(start, end, inc=True):
        import dateutil.rrule as rrule
        if inc: yield start
        rule = rrule.rrule(rrule.HOURLY, dtstart=start)
        for x in rule.between(start, end, inc=False):
            yield x
        if inc: yield end
    @staticmethod
    def uniqueList(list):
        lista_nueva = []
        for i in list:
            if i not in lista_nueva and i["desde"]!=i["hasta"]:
                lista_nueva.append(i)
        return lista_nueva
    @staticmethod
    def stateGlobalstep(steps, state):
        listOk = [0, 25]
        listSteps=[]
        for step in steps:
            _estado = str(state).split("|")[int(step["id_paso"])]
            if len(_estado) > 2:
                _estado = _estado.split(",")[0]
            listSteps.append(_estado)
        validateOk = [x for x in listSteps if int(x) in listOk]
        if len(validateOk)==len(listSteps):
            return 1
        else:
            return 2

    @staticmethod
    def intervalObj(obj):
        _interval = ObjetivoConfig.objects.using("public").filter(objetivo_id=obj, es_ultima_config=True).values(
            "intervalo_id")
        if _interval[0]["intervalo_id"]:
            _interval = _interval[0]["intervalo_id"]
        else:
            _interval = ObjetivoConfig.objects.using("public").filter(objetivo_id=obj).values("intervalo_id").order_by(
                "objetivo_config_id")
            _interval = _interval[1]["intervalo_id"]
        _interval = Intervalo.objects.using("public").filter(intervalo_id=_interval).values("valor", "nombre")

        return _interval

    @staticmethod
    def MarksEvents(marks, clientUserLocalTime, events):
        listEvents = []
        markOut = []
        for mark in marks:
            dictMarks = {}
            markFinal = str(mark["fecha_termino"]).split("+")[0]
            markFinal = formatDateToTimezone(clientUserLocalTime, datetime.strptime(markFinal, '%Y-%m-%d %H:%M:%S'))
            markFinal = datetime.strftime(markFinal, '%Y-%m-%d %H:%M:%S')
            markBegin = str(mark["fecha_inicio"]).split("+")[0]
            markBegin = formatDateToTimezone(clientUserLocalTime, datetime.strptime(markBegin, '%Y-%m-%d %H:%M:%S'))
            markBegin = datetime.strftime(markBegin, '%Y-%m-%d %H:%M:%S')
            dictMarks["fecha_termino"] = markFinal
            dictMarks["fecha_inicio"] = markBegin
            dictMarks["nodos"] = mark["nodos_id"]
            markOut.append(dictMarks)
            for event in events:
                if not mark["fecha_inicio"] <= event["fecha"] <= mark["fecha_termino"]:
                    listEvents.append(event)
        return listEvents

    @staticmethod
    def convertDatetoTimezone(clientUserLocalTime, date):
        date = formatDateToTimezone(clientUserLocalTime, datetime.strptime(str(date)[0:19], '%Y-%m-%d %H:%M:%S'))
        return date

    @staticmethod
    def convertDatetoTimezoneUptime(clientUserLocalTime, date):
        date = formatDateToTimezone(clientUserLocalTime, datetime.strptime(str(date)[0:19], '%Y-%m-%d'))
        return date    

    @staticmethod
    def ValuesQuerySetToDict(vqs):
        """
            Funcion que convierte el querySet en diccionario.

            @param vqs corresponde al querySet a transformar.
            """
        # retorna diccionario
        return [item for item in vqs]

    @staticmethod
    def ConvertDateTimeToDefault(dateTime):
        """
            Funcion que convierte a formato str el dateTime (castea a ISO).

            @param dateTime Fecha y hora.
         """

        if isinstance(dateTime, datetime):
            # Retorna la fecha y hora como String.
            return dateTime.__str__()

    @staticmethod
    def markPeriod(objetive, user, dateBegin, dateFinal):
        mark = PeriodoMarcado.objects.using("public") \
                .values("nodos_id", "objetivo_id", "fecha_inicio", "fecha_termino", "id_tipo_marcado") \
                .filter(fecha_inicio__lte=dateFinal,fecha_termino__gt=dateBegin, objetivo_id=objetive)
        marks=[]
        for perioMark in mark:
            if perioMark["id_tipo_marcado"]=='9':
                marks.append(perioMark)
        return marks

    @staticmethod
    def infoStepsVisible(obj):
        querySet = ObjetivoConfig.objects.using("public") \
            .values_list("xml_configuracion", flat=True) \
            .filterByObjIdAndLastConf(obj)
        listStep = []
        if querySet:
            # ElementTree para trabajar xml configuración
            xmlConfig = ET.fromstring(querySet[0])

            for element in xmlConfig.iter('paso'):
                visibleElement = element.attrib['visible'] if "visible" in element.attrib else None
                if visibleElement is None or visibleElement == "1":
                    dicStep = {}
                    dicStep["nombre_paso"] =element.attrib['nombre'] if "nombre" in element.attrib else ""
                    dicStep["id_paso"] = element.attrib["paso_orden"]
                    listStep.append(dicStep)
        return listStep

    @staticmethod
    def infoStepsVisiblePatterns(obj):
        querySet = ObjetivoConfig.objects.using("public") \
            .values_list("xml_configuracion", flat=True) \
            .filterByObjIdAndLastConf(obj)
        # ElementTree para trabajar xml configuración
        listStep = []
        if querySet:
            xmlConfig = ET.fromstring(querySet[0])
            for element in xmlConfig.iter('paso'):
                visibleElement = element.attrib['visible'] if "visible" in element.attrib else None
                if visibleElement is None or visibleElement == "1":
                    # print element.attrib["paso_id"]
                    patternsList = []
                    for dataElement in element:
                        # print dataElement.attrib
                        # POSEE PATRON
                        if dataElement.tag == 'patron':
                            # POSEE MONITOR
                            patternsList.append(dataElement.attrib)
                    dicStep = {}
                    dicStep["nombre_paso"] = element.attrib['nombre'] if "nombre" in element.attrib else ""
                    dicStep["id_paso"] = element.attrib["paso_orden"]
                    dicStep["patrones"] = patternsList
                    listStep.append(dicStep)
        return listStep

    @staticmethod
    def intervalsReporte(time):
        dateFinal = datetime.now()
        if time =='h':
            dateBegin = dateFinal - timedelta(hours=1)
        elif time =='3h':
            dateBegin = dateFinal - timedelta(hours=3)
        elif time =='d':
            dateBegin = dateFinal - timedelta(days=1)
        elif time =='3d':
            dateBegin = dateFinal - timedelta(days=3)
        elif time =='w':
            dateBegin = dateFinal - timedelta(weeks=1)
        else:
            return {}
        dates = {"beginDate": dateBegin, "FinalDate": dateFinal}
        return dates

    @staticmethod
    def validKey(key):
        """
                    validKey
                     @param  key           key para ingresar al método
                    """

        f = open("config/auth.key", "r")
        if not f.read() == key:
            return False
        else:
            return True

    @staticmethod
    def controlValidathorTime(data, key):
        """
        Validador de intervalo de petición (1 cada 10 min por objetivo)
        @param  objId        ObjetivoId del objetivo.

        """
        if "objetive" in data:
            function = 1
            data = data["objetive"]
        if "user" in data:
            function = 2
            data = data["user"]
        validKey = IndicadorSerializer.validKey(key)
        if validKey is True:
            try:
                datetimeNow = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) - datetime.timedelta(minutes=0.5)
                if function ==1:
                    dateUltimaPeticion = ControlPeticiones.objects.values('ultima_peticion').filter(objetivo_id=data)
                if function ==2:
                    dateUltimaPeticion = ControlPeticionesUsuario.objects.values('ultima_peticion').filter(cliente_id=data)
                dateUltimaPeticion= dateUltimaPeticion[0]["ultima_peticion"]
                if datetimeNow > dateUltimaPeticion:
                    if function ==1:
                        ControlPeticiones.updateData(data, datetime.datetime.utcnow().replace(tzinfo=pytz.UTC))
                    if function ==2:
                        ControlPeticionesUsuario.updateData(data, datetime.datetime.utcnow().replace(tzinfo=pytz.UTC))
                    return True
            except:
                if function ==1:
                    ControlPeticiones.createData(data, datetime.datetime.utcnow().replace(tzinfo=pytz.UTC))
                if function ==2:
                    ControlPeticionesUsuario.createData(data, datetime.datetime.utcnow().replace(tzinfo=pytz.UTC))
                return True
            return ApiErrorCodesMessages.ApiQueryError(
                "Se han realizado request duplicados dentro de un mismo intervalo (1 cada 1 min).")
        else:
            return ApiErrorCodesMessages.ApiQueryError('La key no es válida.')

    @staticmethod
    def errorMessageTime():
        from django.http import JsonResponse
        from rest_framework import status
        _responseMessage = {'Mensaje': 'Tipo de Tiempo no existe', 'Estado': 'Error'}
        # Retorna error en Json.
        return HttpResponse(JsonResponse(_responseMessage), status=status.HTTP_400_BAD_REQUEST,
                            content_type='application/json;charset=utf-8')

    @staticmethod
    def GetUserObjetivesNormal(user):
        listOK = map(lambda x: int(x["codigo_id"]),
                     Codigo.objects.using("public").values("codigo_id").filter(codigo_tipo_id__in=[1, 3]))
        from django.db.models import F
        import re

        # CONSULTA PARA OBTENER GRUPOS EN LO QUE ESTA EL USUARIO
        subClientQuery = ClienteMapaSubclienteUsuario.objects.using("public").filter(cliente_usuario_id=user).values(
            "cliente_subcliente_id")
        subClientQuery = map(lambda x: x["cliente_subcliente_id"], list(subClientQuery))
        # CONSULTA PARA OBTENER TODOS LOS OBJETIVOS DE ESOS GRUPOS
        _otherList = ClienteMapaSubclienteObjetivo.objects.using("public").filter(
            cliente_subcliente_id__in=subClientQuery)
        objetiveList = {x["objetivo_id"] for x in _otherList.values("objetivo_id")}
        # CONSULTA PARA OBTENER OBJETIVOS NO EXPIRADOS

        listUptime = []
        listDown = []
        listParcial = []
        listMark=[]
        for obj in objetiveList:
            dictObjetive = \
            Objetivo.objects.using("public").filter(objetivo_id=obj).values("servicio_id", "nombre", "objetivo_id")[0]
            # OBTIENE PASOS VISIBLES
            visibleSteps = IndicadorSerializer.infoStepsVisible(obj)
            _objetive = ObjetivoConfig.objects.using("public").filter(objetivo_id=obj, es_ultima_config=True).values(
                "monitor_id", "intervalo_id")

            _objetiveMonitor = list(_objetive)[0]

            # SI OBJETIVO PRESENTA MONITOR E INTERVALO
            if _objetiveMonitor["monitor_id"] and _objetiveMonitor["intervalo_id"] is not None:

                # OBTIENE INTERVALO
                interval_value = \
                Intervalo.objects.using('public').values('valor').get(intervalo_id=_objetiveMonitor["intervalo_id"])[
                    'valor']
                # MAXIMO INTERVALO
                dateMaxInterval = (datetime.now() - timedelta(seconds=(timedelta.total_seconds(interval_value * 3))))
                # print datetime.now(), interval_value, dateMaxInterval
                # NODES WITH DATA
                nodes = Evento.objects.using("procesado").values("nodo_id").distinct().filter(objetivo_id=obj,
                                                                                            fecha_hasta__gt=dateMaxInterval)
                mark = PeriodoMarcado.objects.using("public").values("objetivo_id", "fecha_inicio", "fecha_termino") \
                           .filter(objetivo_id=obj, fecha_termino__gt=dateMaxInterval).order_by("-fecha_termino")[:1]
                if mark:
                    markBegin = datetime.strptime((str(mark[0]["fecha_inicio"]).split("+")[0]), '%Y-%m-%d %H:%M:%S')
                    markFinal = datetime.strptime((str(mark[0]["fecha_termino"]).split("+")[0]), '%Y-%m-%d %H:%M:%S')
                    if markBegin < datetime.strptime((str(dateMaxInterval).split(".")[0]), '%Y-%m-%d %H:%M:%S') < markFinal:
                        listMark.append(dictObjetive)
                else:
                    countNodes = 0
                    for node in nodes:
                        queryEvent = Evento.objects.using("procesado").values("estado").filter(objetivo_id=obj, \
                                fecha_hasta__gt=dateMaxInterval,nodo_id=node["nodo_id"]).exclude(\
                            fecha_desde=F('fecha_hasta')).order_by("-fecha_hasta")[:1]
                        countStepDown = 0
                        if queryEvent:
                            listStatusEventByNode = str(queryEvent[0]["estado"]).split("|")
                            for step in visibleSteps:
                                # PASOS POR NODO SI ESTAN EN LISTA OK
                                if not [x for x in str(listStatusEventByNode[int(step["id_paso"])]).split(",") if
                                        int(x) in listOK]:
                                    countStepDown = countStepDown + 1
                        # print 'pasos caidos', countStepDown
                        if countStepDown == len(visibleSteps):
                            # print 'nodo caido'
                            countNodes = countNodes + 1
                    # print countStepDown, len(nodes)
                    if countNodes == len(nodes):
                        dictObjetive["estado"] = "Downtime"
                        listDown.append(dictObjetive)
                    elif countNodes == 0:
                        dictObjetive["estado"] = "Parcial"
                        listUptime.append(dictObjetive)
                    else:
                        dictObjetive["estado"] = "Uptime"
                        listParcial.append(dictObjetive)
        dicData = {"Uptime": listUptime, "Downtime": listDown, "Partial": listParcial, "Marcado":listMark}

        return dicData

    @staticmethod
    def getDataNodeMonitor(monitor):
        _node = Monitor.objects.using("public").filter(monitor_id=monitor).values("nodo_id")
        _dataNode = Nodo.objects.using("public").filter(nodo_id=_node).values("nombre", "titulo",
                                                                              "subtitulo",
                                                                              "nodo_id")
        return _dataNode[0]

    @staticmethod
    def GetUserObjetives(user):
        listOK=map(lambda x:x["id"], ConstantCodes.at_codes_ok)
        from django.db.models import F
        import re
        # CONSULTA PARA OBTENER GRUPOS EN LO QUE ESTA EL USUARIO
        subClientQuery = ClienteMapaSubclienteUsuario.objects.using("public").filter(cliente_usuario_id=user).values(
            "cliente_subcliente_id")
        subClientQuery = map(lambda x: x["cliente_subcliente_id"], list(subClientQuery))
        # CONSULTA PARA OBTENER TODOS LOS OBJETIVOS DE ESOS GRUPOS
        _otherList = ClienteMapaSubclienteObjetivo.objects.using("public").filter(
            cliente_subcliente_id__in=subClientQuery)
        objetiveList = {x["objetivo_id"] for x in _otherList.values("objetivo_id")}
        # CONSULTA PARA OBTENER OBJETIVOS NO EXPIRADOS
        listObjetives = []
        listUptime=[]
        listDown=[]
        listNomon=[]
        listParcial=[]
        listServices=[]
        listServicesUnified = []
        listServicesFinal = []
        listServicesUnifiedFinal = []
        # Obtener la zona horaria según el usuario
        clientUserLocalTime = ClienteUsuario.getTimeZoneValueById(user)
        for objetive in objetiveList:
            visibleSteps= IndicadorSerializer.infoStepsVisible(objetive)
            visibleStepsPatterns = IndicadorSerializer.infoStepsVisiblePatterns(objetive)
            # CONSULTA PARA OBTENER NOMBRE, ID, Y SERVICIO
            dictObjetive = Objetivo.objects.using("public").filter(objetivo_id=objetive, servicio_id__lte=700, fecha_expiracion=None) \
                           | Objetivo.objects.using("public").filter(objetivo_id=objetive, fecha_expiracion__gte=datetime.now())
            dictObjetive = dictObjetive.values("servicio_id", "nombre", "objetivo_id", "sla_rendimiento_ok",
                                               "sla_rendimiento_ok", "sla_rendimiento_error",
                                               "sla_disponibilidad_ok", "sla_disponibilidad_error", "descripcion")
            lisNodes=[]
            listMonitor = []
            if dictObjetive:
                dictObjetive=dictObjetive[0]
                #print dictObjetive["nombre"], objetive
                #listServices.append(dictObjetive["servicio_id"])
                service =  Servicio.objects.using("public").filter(servicio_id=dictObjetive["servicio_id"]).values("nombre")[0]["nombre"]
                dictObjetive["nombre_servicio"] = service
                serviceUnified = 'atMeta'
                if 'atDns' in service:
                    service = 'atDns'
                if 'atStress' in service:
                    service = 'atStress'
                if 'atTransaction 2.0' in service:
                    service = 'atTransaction 2.0'
                    serviceUnified = 'atWeb'
                if 'atTransaction Plus 2.0' in service:
                    service = 'atTransaction Plus 2.0'
                    serviceUnified = 'atWeb'
                if 'AtIVR Monitoreo para centrales IVR' in service:
                    serviceUnified = 'atIvr'
                if 'AtAppMobile' in service:
                    serviceUnified = 'atMobile'
                dictObjetive["nombre_servicio_unificado"] = serviceUnified
                dictObjetive["grupo_servicio_unificado"] = serviceUnified
                dictObjetive["grupo_servicio"] = service
                listServices.append(service)
                listServicesUnified.append(serviceUnified)
                if dictObjetive["sla_rendimiento_ok"] =='null' or dictObjetive["sla_rendimiento_ok"] <= 0:
                    dictObjetive["sla_rendimiento_ok"]= 5.00
                if dictObjetive["sla_rendimiento_error"]=='null' or dictObjetive["sla_rendimiento_error"] <= 0:
                    dictObjetive["sla_rendimiento_error"]= 30.00
                if dictObjetive["sla_disponibilidad_ok"] =='null' or dictObjetive["sla_disponibilidad_ok"] <= 0:
                    dictObjetive["sla_disponibilidad_ok"]= 99.00
                if dictObjetive["sla_disponibilidad_error"]=="null" or dictObjetive["sla_disponibilidad_error"] <= 0:
                    dictObjetive["sla_disponibilidad_error"]= 97.00
                _objetive = ObjetivoConfig.objects.using("public").filter(objetivo_id=objetive,es_ultima_config=True).values(
                    "monitor_id", "intervalo_id")
                _objetiveMonitor = {}
                if _objetive:
                    _objetiveMonitor = list(_objetive)[0]
                dictObjetive["sla_rendimiento_ok"] = str(dictObjetive["sla_rendimiento_ok"])
                dictObjetive["sla_rendimiento_error"] = str(dictObjetive["sla_rendimiento_error"])
                dictObjetive["sla_disponibilidad_ok"] = str(dictObjetive["sla_disponibilidad_ok"])
                dictObjetive["sla_disponibilidad_error"] = str(dictObjetive["sla_disponibilidad_error"])
                # print _objetiveMonitor["intervalo_id"]
                if _objetiveMonitor:
                    dictObjetive["intervalo_id"] = _objetiveMonitor["intervalo_id"]
                if _objetiveMonitor and _objetiveMonitor["monitor_id"] and _objetiveMonitor["intervalo_id"] is not None:
                    _estado = "Activo"
                    interval_value = Intervalo.objects.using('public').values('valor').get(intervalo_id=_objetiveMonitor["intervalo_id"])[
                        'valor']
                    dictObjetive["intervalo"] = str(interval_value)
                    #print timedelta.total_seconds(interval_value*3)
                    dateMaxInterval= (datetime.now()- timedelta(seconds=(timedelta.total_seconds(interval_value*3))))
                    dictObjetive["estado"] = _estado

                    Monitors = ObjetivoConfig.objects.using("public").values_list("monitor_id", flat=True).filter(
                        objetivo=objetive, es_ultima_config=True)
                    contDown=0
                    contNoMon=0
                    contParcial=0
                    contUptime=0
                    lisNodes.append({"nodo": 'Global', "id_nodo": 0})
                    dateAuxLastStatus = datetime.now().replace(tzinfo=pytz.UTC).astimezone(pytztimezone(clientUserLocalTime)).replace(tzinfo=None)
                    
                    for stepVisible in visibleSteps:
                        stepDownMonitor=0
                        noMonMonitor=0
                        for i, monitor in enumerate(Monitors[0], start=0):
                            listMonitor.append(monitor)
                            dataNode = IndicadorSerializer.getDataNodeMonitor(monitor)
                            lisNodes.append({"nodo": dataNode["nombre"], "id_nodo": dataNode["nodo_id"], "monitor": monitor,
                                         "titulo": dataNode["titulo"], "subtitulo": dataNode["subtitulo"]})
                            dataLastStatus=UltimoEstado.objects.using("cache").filter(objetivo_id=objetive, \
                                fecha__gt=dateMaxInterval, monitor_id=monitor).values("estado", "fecha").order_by("-fecha")[:1]
                            if dataLastStatus:
                                status= dataLastStatus[0]["estado"]
                                statusStep=(str(status).split("|"))[int(stepVisible["id_paso"])]
                                sizeStatusStep= len(statusStep)
                                if sizeStatusStep>1:
                                    if [x for x in str(statusStep).split(",") if int(x) not in listOK]:
                                        stepDownMonitor+=1
                                else:
                                    if int(statusStep) not in listOK:
                                        stepDownMonitor+=1
                            else:
                                noMonMonitor+=1
                        if noMonMonitor!=len(Monitors[0]):
                            if stepDownMonitor==0:
                                stepVisible["estado_paso"]="Uptime"
                                contUptime+=1
                            else:
                                if (stepDownMonitor+noMonMonitor)==len(Monitors[0]):
                                    stepVisible["estado_paso"]="Downtime"
                                    contDown+=1
                                else:
                                    stepVisible["estado_paso"]="Parcial"
                                    contParcial+=1
                        else:
                            stepVisible["estado_paso"]="No Monitoreo"
                            contNoMon+=1
                    if contUptime>0 and contParcial==0 and contDown==0:
                        dictObjetive["estado"] = "Uptime"
                        dictObjetive["orden"] = 2
                        dictObjetive["color"] = "rgb(160, 246, 92)"
                        dictObjetive["fecha"] = str(dateAuxLastStatus)
                        listUptime.append(dictObjetive)
                    elif contDown>0:
                        dictObjetive["estado"] = "Downtime"
                        dictObjetive["orden"] = 0
                        dictObjetive["color"] = "rgb(255, 96, 89)"
                        dictObjetive["fecha"] = str(dateAuxLastStatus)
                        listDown.append(dictObjetive)
                    else:
                        if contDown==0 and contParcial>0:
                            dictObjetive["estado"] = "Parcial"
                            dictObjetive["orden"] = 1
                            dictObjetive["color"] = "rgb(254, 254, 25)"
                            dictObjetive["fecha"] = str(dateAuxLastStatus)
                            listParcial.append(dictObjetive)
                        else:
                            dictObjetive["estado"] = "No monitoreo"
                            dictObjetive["orden"] = 3
                            dictObjetive["color"] = "rgb(241, 241, 241)"
                            dictObjetive["fecha"] = str(datetime.now() - timedelta(hours=1))
                            listNomon.append(dictObjetive)
                else:
                    dictObjetive["estado"] = "No monitoreo"
                    dictObjetive["orden"] = 3
                    dictObjetive["color"] = "rgb(241, 241, 241)"
                    dictObjetive["fecha"] = str(datetime.now() - timedelta(hours=1))
                    listNomon.append(dictObjetive)
                lisNodes=[dict(t) for t in {tuple(d.items()) for d in lisNodes}]
                listMonitor=list(set(listMonitor))
                dictObjetive["Nodos"]=lisNodes
                dictObjetive["Pasos"]=visibleSteps
                dictObjetive["Pasos_patrones"] = visibleStepsPatterns
                dictObjetive["Monitores"] = listMonitor
        listNomon=sorted(listNomon, key=lambda k: k['orden'])
        listServices = np.unique(listServices)
        listServicesUnified = np.unique(listServicesUnified)
        for services in listServices:
            listServicesFinal.append(services)
        for services in listServicesUnified:
            listServicesUnifiedFinal.append(services)
        dicData={"Uptime":listUptime, "Downtime": listDown, "NoMonitoring": listNomon, "Partial": listParcial, "Services":listServicesFinal, "ServicesUnified":listServicesUnifiedFinal}
        return dicData