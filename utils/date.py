# -*- coding: utf-8 -*-
import pytz
from datetime import datetime, timedelta
from dateutil import tz
import locale

"""
@brief Método que permite obtener la fecha actual más una hora añadida.
@return datetime Fecha actualizada
"""
def datetimeExpired():	
	return datetime.now()+timedelta(hours=1)