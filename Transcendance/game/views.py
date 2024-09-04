from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from game.models import Play
from game.serializer import PlaySerializer
# from  game.serializer import BallPositionSerializer, PlayerPositionSerializer
# Create your views here.

def index(request):
	return render(request, 'game/index.html')

#APIView pour des actions specifiques
#ModelViewset pour les operations CRUD directement liee a un model

# Systeme de partage de l'id pour pouvoir joindre la partie en remote
# Autre endpoint pour joindre la partie en remote a creer
class PlayCreateAPIView(APIView):
	def post(self, request):
		serializer = PlaySerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PlayStartAPIView(APIView):
	def post(self, request, id):
		try :
			play = Play.objects.get(id=id)
			#Recuperation de la socket cree par le Js
			#Lancement de la boucle Python du jeu
			# Thread / Celery / asyncio ?
			#(avec les mouvements communiquees via la websocket)
			return Response({"status": "Game started successfully"}, status=status.HTTP_200_OK)
		except Play.DoesNotExist:
			return Response({"error": "Play not found"}, status=status.HTTP_404_NOT_FOUND)
