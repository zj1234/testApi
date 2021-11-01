# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from django.utils import timezone
from rest_framework import authentication
from rest_framework import exceptions

from utils.error_api import ApiErrorCodesMessages, AuthFailed
from base.models import Client, Token
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
        if request.method == "GET" or request.method == "DELETE":
            data = request.query_params
        else:
            data = request.data
        if "token" not in data or 'user' not in data:
            return ApiErrorCodesMessages.AuthException()
        else:
            token=data["token"]
            user=data["user"]
            _token=(Token.objects.filter(token=token))
            _userAdmin=Client.objects.filter(cliente_usuario_id=user,\
                perfil_id=0)
            print(_token, _userAdmin)
            if not _token :
                return ApiErrorCodesMessages.AuthToken()
            if not _userAdmin:
                return ApiErrorCodesMessages.AuthUser()
            