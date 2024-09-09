import json
import asyncio
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from .pong_game import PongGame
from .models import Play

#async pour creer une fonction asynchrone (une coroutine qui peut etre mis en attente et effectue au moment voulu sans bloquer)
#await pour attendre qu'une coroutine ou fonction asynchrone finisse a l'interieur d'une focntion asynchrone
#sync_to_async lorsqu'il faut appeler une focntion synchrone dans un contexte asynchrone

class GameConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		#Checker si la partie existe bien et n'est pas deja finie
		self.game_id = self.scope['url_route']['kwargs']['game_id']#Attribu l'id de la partie au consumer
		try:
			self.play = await database_sync_to_async(Play.objects.get)(id=self.game_id)
			if not await self.play_is_available():
				raise ValidationError('Play has already started or finished')
		except ObjectDoesNotExist:
			await self.close(code=4001)# Code a documenter dans l'API 4001 = objet non trouve
			return
		except ValidationError as e:
			if str(e) == 'Play has already started or finished':
				await self.close(code=4002)#Code a documenter dans l'API 4002 = partie non joignable
			return

		#Creation implicite d'un groupe et Ajout du consumer (client) au groupe pour diffuser les messages a tout les clients
		self.game_group_name = f'game_{self.game_id}'
		await self.channel_layer.group_add(
			self.game_group_name,
			self.channel_name
		)

		await self.accept()
		await self.add_players_to_play()
		# GESTION DE DECONNEXIONS CLIENTS
		# Probleme pour remote : Si l'instance de PongGame est creee dans le Consumer, si ce Consumer se deconnecte pour n'importe quelle raison
		# Le jeu serait detruit avec le consumer et affecterait alors les autres players. Solutions :
			#- Creer un objet global intermediaire qui stockerait les objets PongGameet qu'on manipulerait depuis cet objet ??
		if self.play_ready_to_start():
			# await self.channel_layer.group_send(
            #     self.game_group_name,
            #     {
            #         'type':'update_game',
			# 		'test':	self.game_id
            #     }
            # )
			# print('Play is ready')
			self.pong = await sync_to_async(PongGame, thread_sensitive=True)(self.game_id, self.game_group_name)
				# PongGame(self.game_id, self.game_group_name)Comprendre
			await self.pong.start_game()

	async def disconnect(self, close_code):

		#Enleve la websocket du groupe
		await self.channel_layer.group_discard(
			self.game_group_name,
			self.channel_name
		)

		await self.rm_players_from_play()
		if self.play.player.connected == 0:
			self.pong.stop_game()
			#remettre la partie avec tout les joueurs pour qu'elle ne soit plus jouable
			#ca depend des circonstance gestion des deconnexion inconnu ??

	async def receive(self, text_data):
		# Recevoir un message du WebSocket et traiter les mouvements des joueurs
		text_data_json = json.loads(text_data)
		#Test
		# message = text_data_json['message']
		# print(f'Ce qui a ete recu sur le back par le front : {message}')

		await self.pong.update_player_position(text_data_json)# Fonction update a modifier ??
		#Check du message recu : Move player, Point marque ..
		# player_id = message['player_id']
		# direction = message['direction']
		# self.game_logic.process_player_move(player_id, direction)
		#Ou point_scored()

	# Methode que chaque consumer connecte appelera individuellement via le channel_layer dans PongGame
	async def update_game(self, event):
		await self.send(text_data=json.dumps(event))

	# Methodes utilitaires
	async def play_is_available(self):
		if self.play.remote:
			return self.play.player_connected < self.play.nb_players
		else:
			return self.play.player_connected == 0

	async def add_players_to_play(self):
		if not self.play.remote:
			self.play.player_connected += self.play.nb_players
		else:
			self.play.player_connected += 1

	async def play_ready_to_start(self):
		return self.play.player_connected == self.play.nb_players

	async def rm_players_from_play(self):
		if self.play.remote:
			self.play.player_connected -= self.play.nb_players
		else:
			self.play.player_connected -= 1
