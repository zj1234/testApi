# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from django.utils import timezone
from rest_framework import authentication
from rest_framework import exceptions

from utils.error_api import ApiErrorCodesMessages
"""
@class BaseTokenAuthentication
@brief Clase para manejar la autenticación por token de atApi.
"""
class BenchmarkTokenAuthentication(authentication.BaseAuthentication):
    """
    @brief Reescritura de método para validar autenticación
    del la petición, de que tenga el token correcto.
    En caso contrario:
        - Data que viene en la petición está mal formateada: 
    """

    def authenticate(self, request):
        print("auth", request.method)
        if request.method == "GET" or request.method == "DELETE":
            data = request.query_params
        else:
            data = request.data
        print(data)
        if "token" not in data:
            return ApiErrorCodesMessages.AuthException()
            