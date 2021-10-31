from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Token, Client
from public.models import Auth
from utils import error_api
from hashlib import md5
import json
import ast
# Create your views here.

class AuthReportView(APIView):
    def post(self, request):
        try:
            if request.content_type == "application/json;charset=utf-8":
                # para cuando se pasan los parametros por json(reporte stress)
                data = json.loads(request.body)
            else:
                data = request.data
            user=str(data["user"])
            passW = str(md5(data["pass"].encode()).hexdigest())
            _dataUserPass=Auth.objects.filter(passText=passW, user=user)
            
            if _dataUserPass:
                #print("datauser",_dataUserPass, user)
                _UserInfo=Client.objects.filter(name=user).values("perfil_id",\
                    "name", "mail", "cell", "cars", "cliente_usuario_id" ).get()
                _dataToken= Token.objects.values("token").filter(cliente_usuario_id=\
                    _UserInfo["cliente_usuario_id"]).get()
                return Response({"token":_dataToken, "user":_UserInfo})
            else:
                return Response(error_api.ApiErrorCodesMessages.AuthToken())
        except Exception as e:
            return Response(error_api.ApiErrorCodesMessages.AuthException())

