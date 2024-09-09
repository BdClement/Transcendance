from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status

from game.models import Play
from game.serializer import PlaySerializer
# from  game.serializer import BallPositionSerializer, PlayerPositionSerializer
# Create your views here.

def index(request):
	return render(request, 'game/index.html')

#APIView pour des actions specifiques
#ModelViewset pour les operations CRUD directement liee a un model1

class PlayCreateAPIView(APIView):
	def post(self, request):
		# print("Request data:", request.data)
		#Pre validation pour eviter des operations plus couteuses si les fields requis ne sont pas present
		if 'remote' not in request.data or 'nb_players' not in request.data:
			raise ValidationError('remote and nb_players are required')

		#[ Autre option ] Extraire manuellement les donnees de la requete pour pouvoir creer un objet puis le mettre dans un serializer
		# remote = request.data.get('remote')
		#Recuperer les donnees depuis la requete directement grace au serializer pour simplifier la vue
		serializer = PlaySerializer(data=request.data)
		if serializer.is_valid():#Validation inclue dans le serializer
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class PlayStartAPIView(APIView):
# 	def post(self, request, id):
# 		try :
# 			play = Play.objects.get(id=id)
# 			#Recuperation de la socket cree par le Js
# 			#Lancement de la boucle Python du jeu
# 			# Thread / Celery / asyncio ?
# 			#(avec les mouvements communiquees via la websocket)
# 			return Response({"status": "Game started successfully"}, status=status.HTTP_200_OK)
# 		except Play.DoesNotExist:
# 			return Response({"error": "Play not found"}, status=status.HTTP_404_NOT_FOUND)
