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


class WsView(APIView):
    print("ws")
    authentication_classes = (BenchmarkTokenAuthentication,)
    def get(self, request, format=None):
        print("ws", request)
        return Response("hola")

    