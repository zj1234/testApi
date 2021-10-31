from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Token
from utils import error_api
import json
# Create your views here.

class AuthReportView(APIView):
    def post(self, request):
        try:
            if request.content_type == "application/json;charset=utf-8":
                # para cuando se pasan los parametros por json(reporte stress)
                data = json.loads(request.body)
            else:
                data = request.data
            token=data["token"]
            _dataUser= Token.objects.values("cliente_id", \
                "cliente_usuario_id", "name").filter(token=token)
            print(_dataUser)
            if _dataUser:
                return Response(True)
            else:
                return Response(error_api.ApiErrorCodesMessages.AuthToken())
        except Exception as e:
            return Response(error_api.ApiErrorCodesMessages.AuthException())

