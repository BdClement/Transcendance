import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Play

class GameConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.game_id = self.scope['url_route']['kwargs']['game_id']#Attribu l'id de la partie au consumer
		self.game = Play.objects.get(pk=self.game_id)# Relier le Consumer a la partie

		# self.game_group_name = f'game_{self.game_id}'#Attribue un groupe a la partie dans lequel est ajoyte le consumer

		# Joindre un groupe de sockets, pour permettre les diffusions aux clients
		# await self.channel_layer.group_add(
		# 	self.game_group_name,
		# 	self.channel_name
		# )

		await self.accept()

		#Pour le remote player, metre un condition lorsque tout les clients sont connecte lance le thread 1 fois
		# self.game_logic = GameLogic(self.game_id, self)# Creation d'une instance de GameLogic en passant le consumer
		# self.game_logic.start_game()#Dans un thread separe dans GameLogic!

	async def disconnect(self, close_code):

		# self.game_logic.stop_game()#Appel de fin de jeu Gestion d'erreur


		# Quitter le groupe de sockets lors de la déconnexion
		await self.channel_layer.group_discard(
			self.game_group_name,
			self.channel_name
		)

	async def receive(self, text_data):
		# Recevoir un message du WebSocket et traiter les mouvements des joueurs
		text_data_json = json.loads(text_data)
		message = text_data_json['message']

		#Test
		print(f'Ce qui a ete recu sur le back par le front : {message}')
		#Check du message recu : Move player, Point marque ..
		# player_id = message['player_id']
		# direction = message['direction']
		# self.game_logic.process_player_move(player_id, direction)
		#Ou point_scored()

		# Envoyer un message au groupe de sockets
		# await self.channel_layer.group_send(# A faire dans process_player_move dans GameLogic
		# 	self.game_group_name,
		# 	{
		# 		'type': 'game_message',
		# 		'message': updated_message
		# 		}
		# )

	# async def game_message(self, event):
	# 	# Envoyer le message du groupe au WebSocket
	# 	message = event['message']

	# 	await self.send(text_data=json.dumps({
	# 		'message': message
	# 	}))
