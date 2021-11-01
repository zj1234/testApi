"""atApi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from base.views import AuthReportView
from base.ws.resources import WsView, WsNewView, WsNewCarView, WsNewRepairCarView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^auth/', AuthReportView.as_view(), name="auth"),
    # Rutas de base
    url(r'^base/', WsView.as_view(), name="base"),
    url(r'^base-new/', WsNewView.as_view(), name="base/new"),
    url(r'^base-newCar/', WsNewCarView.as_view(), name="base/newCar"),
    url(r'^base-newRepairCar/', WsNewRepairCarView.as_view(), name="base/newRepairCar"),
    
]
