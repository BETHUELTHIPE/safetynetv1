from django.urls import re_path

from dashboard import consumers

websocket_urlpatterns = [
    re_path(r'ws/crime_alerts/', consumers.CrimeAlertConsumer.as_asgi()),
]
