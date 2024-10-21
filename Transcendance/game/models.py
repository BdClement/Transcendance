from django.db import models
from channels.db import database_sync_to_async
from authentication.models import User

# Create your models here.

# Pour reinitiliser les id des models lors des tests, dans un shell Django:
		# from django.db import connection
		# from yourapp.models import YourModel
		# with connection.cursor() as cursor:
		# cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{Play._meta.db_table}';")

# AJOUT DE LA DATE A FAIRE POUR MODULE D'ILONA
class Play(models.Model):
	#Liason de ce joueur a cette partie, ce joueur peut etre lier a plusieurs parties
	player1 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='player1')
	player2 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='player2')
	player3 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='player3')
	player4 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='player4')
	# player1 =  models.CharField(max_length=255, default='player1')

	#Lier la partie a un tournoi, la partie peut etre lier uniquemenr a ce tournoi
	#Liason a Tournament via une string car Django le permet pour eiter les boucles d'importations
	#Django resout la string avec le model qui est declare plus tard dans le fichier
	tournament = models.ForeignKey('Tournament', related_name='plays', on_delete=models.SET_NULL, null=True)
	#Pour indiquer a quel tour appartient la partie dans le tournoi
	tournament_round = models.PositiveIntegerField(default=1)

	player_connected= models.PositiveIntegerField(default=0)#Nombre de joueurs connectes a la partie
	nb_players = models.IntegerField(choices=[(2, 'Deux joueurs'), (4, 'Quatre joueurs')], default=2)# Nombre de joueur = mode normal ou 2V2# Nombre de joueur = mode normal ou 2V2
	remote = models.BooleanField(default=False)# Remote ou pas
	date = models.DateTimeField(blank=True, null=True)

	#Choix de stocker les resultats dans un JSONField pour permettre une flexibilite au client en terme d'affchage
	#Possibilite de modifier le field sans toucher a la base de donnee
	results = models.JSONField(null=True, blank=True)
	is_finished = models.BooleanField(default=False)

	async def add_victory(self, nb_player):
		if nb_player == 1:
			player = self.player1
		elif nb_player == 2:
			player = self.player2
		elif nb_player == 3:
			player = self.player3
		elif nb_player == 4:
			player = self.player4
		else :
			player = None

		if player is not None :
			player.nbVictoires += 1
			await database_sync_to_async(player.save)()

	async def add_defeat(self, nb_player):
		if nb_player == 1:
			player = self.player1
		elif nb_player == 2:
			player = self.player2
		elif nb_player == 3:
			player = self.player3
		elif nb_player == 4:
			player = self.player4
		else :
			player = None

		if player is not None :
			player.nbDefaites += 1
			await database_sync_to_async(player.save)()

	def add_player(self, player):
		if self.player1 is None:
			self.player1 = player
		elif self.player2 is None:
			self.player2 = player
		elif self.player3 is None:
			self.player3 = player
		elif self.player4 is None:
			self.player4 = player
		else:
			return False
		self.save()
		return True



#VERSION TOURNAMENT JULIEN
#Pour acceder aux parties dans un tournoi, utiliser l'attribut reverse genere automatiquement par Django grace au related_name
#Exemple ici tournament.plays.all()
# class Tournament(models.Model):
#     nb_players = models.IntegerField(choices=[(4, 'Quatre joueurs'), (8, 'Huit joueurs')], default=4)
#     players = models.ManyToManyField(User, related_name='tournaments_players')
#     results = models.JSONField(null=True, blank=True)
#     is_finished = models.BooleanField(default=False)
#     current_round = models.IntegerField(default=0)

#     def create_next_round(self):
#         if self.current_round == 0:  # Cas du premier round
#             players = list(self.players.all())
#             self.create_plays_for_new_round(players)
#         else:
#             plays_from_last_round = Play.objects.filter(tournament=self, tournament_round=self.current_round, is_finished=True)

#             if plays_from_last_round.count() == 1:  # La finale a été jouée
#                 final_play = plays_from_last_round.first()
#                 self.results = {
#                     "players": [player.id for player in self.players.all()],
#                     "winner": final_play.results.get('winners', []),
#                     "final_score": final_play.results.get('score', {})
#                 }
#                 self.is_finished = True
#             else:  # Création des parties du prochain round
#                 winners = []
#                 for play in plays_from_last_round:
#                     winner_ids = play.results.get('winners', [])
#                     winners.extend(User.objects.filter(id__in=winner_ids))

#                 if winners:
#                     self.create_plays_for_new_round(winners)
#                 else:
#                     print(f"PROBLEME: Aucun gagnant trouvé pour le round {self.current_round}")

#         if not self.is_finished:
#             self.current_round += 1
#         self.save()

#     def create_plays_for_new_round(self, players):
#         players = list(players)
#         if len(players) % 2 != 0:
#             print(f'AVERTISSEMENT: Nombre impair de joueurs ({len(players)}). Ajout d\'un "bye".')
#             players.append(None)

#         for i in range(0, len(players), 2):
#             player1 = players[i]
#             player2 = players[i + 1] if i + 1 < len(players) else None

#             if player1 and player2:
#                 Play.objects.create(
#                     player1=player1,
#                     player2=player2,
#                     tournament=self,
#                     tournament_round=self.current_round + 1
#                 )
#             elif player1:
#                 print(f"Joueur {player1.username} passe automatiquement au prochain tour (bye)")

#VERSION TOURNAMENT CLEMENT
#Pour acceder aux parties dans un tournoi, utiliser l'attribut reverse genere automatiquement par Django grace au related_name
#Exemple ici tournament.plays.all()
class Tournament(models.Model):

	#Nombre joueur d'un tournoi flexible, soumis a des choix predefinis tout de meme
	nb_players = models.IntegerField(choices=[ (4, 'Quatre joueurs'), (8, 'Huit joueurs')], default=4)

	#Aller chercher dans la database grace aux alias les players concercne
	#Ajouter cela a au field players pour lier plusieurs player a ce tournoi (flexibilite du nombre de joueur au tournoi)
	# Acces au joueur d'un tournoi avec par exemple : tournament.players.all()

	players = models.ManyToManyField(User, related_name='tournaments_players')
	results = models.JSONField(null=True, blank=True)
	is_finished = models.BooleanField(default=False)
	current_round = models.IntegerField(default=0)

	def create_next_round(self):
		if self.current_round == 0:#Cas du premier round
			players = self.players.all()
			print(f'TEST dans create_next_round pour le premier tour === {players}')
			self.create_plays_for_new_round(players)
		else:
			#recherche de toutes les parties finies du round actuel
			plays_from_last_round = Play.objects.filter(tournament=self, tournament_round=self.current_round, is_finished=True)
			if plays_from_last_round.count() == 1:#La finale a ete jouee
				print(f'TEST dans create_next_round quand la finale a ete jouee === {plays_from_last_round}')
				#Stockage de results avec plays_from_last_round
				self.results = {
					"players": [player.id for player in self.players.all()],
					"winner": plays_from_last_round.first().results['winners'],
					"final_score": plays_from_last_round.first().results['score']
				}
				self.is_finished = True
			else :#Creation de toutes les parties du prochain round
				winners = []
				for play in plays_from_last_round:
					if 'winners' in play.results:
						winners.append(play.results['winners'])
					else:
						print(f'PROBLEME: winners nest pas present dans results de la partie === {play.results}')
					print(f'TEST dans create_next_round les winners sont === {winners}')
				self.create_plays_for_new_round(winners)

		if not self.is_finished:
			self.current_round += 1
		print(f'TEST dans create_next_round current_round en fin dappel === {self.current_round}')
		self.save()

	def create_plays_for_new_round(self, players):
		if players.count() % 2 != 0:
			print(f'PROBLEME: dans create_plays_for_new_round, les joueurs recus sont impairs === {players}')
		else:
			for i in range(0, len(players), 2):
				player1 = players[i]
				if i + 1 < len(players):
					player2 = players[i + 1]
					print(f'TEST dans create_plays_for_new_round === player1 {player1}, player2 {player2}')
					Play.objects.create(player1=player1, player2=player2, tournament=self, tournament_round=self.current_round + 1)
				else:
					print(f'TEST dans create_plays_for_new_round PROBLEME Un nombre impair est donne')



		#API equivalente a PlayDetailsAPIView mais pour les tournois pour transmettre les donnees d'un tournoi

