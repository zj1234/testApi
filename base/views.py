from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import auth_user
# Create your views here.

class AuthReportView(APIView):
    def post(self, request):
        print("fsdñlj", auth_user.objects.all())
        
        return Response(True)

