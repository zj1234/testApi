# -*- coding: utf-8 -*-
"""
    @package main
    ===============
    @file   router.py
    @class

    @author Aldo Cruz Romero <acruz2094@atentus.com>
    @brief  Encargada de definir las rutas que se consultaran en la api
    @date   oct/2021
    @todo
"""

from rest_framework import routers
from base.ws.resources import WsView

# Registrar Router por defecto
router = routers.SimpleRouter()
# Registrar las rutas
router.register(r'data', WsView, basename="data")

urlDefaultPatterns = router.urls