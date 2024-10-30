# routing.py

from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/live-updates/', consumers.LiveUpdateConsumer.as_asgi()),
]
