# # Transcendance/Transcendance/routing.py

from django.urls import re_path, path
from .consumers import GameConsumer

#path pour les URL simples pour les cas courants
#re_path pour les path avec regex (expressions regulieres)

websocket_urlpatterns = [
	path('ws/game/<int:game_id>/',  GameConsumer.as_asgi()),
]
