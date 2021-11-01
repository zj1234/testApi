# -*- coding: utf-8 -*-
from rest_framework import exceptions
from rest_framework import status
from rest_framework.response import Response

"""
@class AuthFailed
@brief Clase que hereda de APIException para crear una excepción customizada
       enfocada en trabajar con la autenticación dentro de la api.
"""
class AuthFailed(exceptions.APIException):
    status_code = 401
    default_detail = "La autenticación no es correcta."
    default_code = "api_auth_failed"

class ApiErrorCodesMessages:
    """
    @brief Método estático que levanta una excepción de autenticación definida
    por defecto en Django Rest Framework, con error http 401 y se le agrega el
    detalle como código 401.
    @return void
    """
    @staticmethod
    def AuthException():
        raise AuthFailed('401')
    @staticmethod
    def AuthToken():
        raise AuthFailed('TOKEN NO EXISTE')
    @staticmethod
    def AuthUser():
        raise AuthFailed('Usuario No posee permisos suficientes')
    @staticmethod
    def NoData():
        raise AuthFailed('No Existe data Solicitada')
    @staticmethod
    def NoContinue():
        raise AuthFailed('No Es posible Continuar, Ingrese Campos Necesarios')
    @staticmethod
    def NoInsert():
        raise AuthFailed('No se pudo realizar Ingreso')
    @staticmethod
    def AuthData(e):
        raise AuthFailed('Parametro Faltante '+e)
    @staticmethod
    def BadFormat():
        raise AuthFailed('Parametro de patente mal ingresado, ej:aa-bb-cc')
