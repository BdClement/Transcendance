from django.db import models

# Create your models here.

# Pour reinitiliser les id des models lors des tests, dans un shell Django:
		# from django.db import connection
		# from yourapp.models import YourModel
		# with connection.cursor() as cursor:
		# cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{Play._meta.db_table}';")

class Play(models.Model):
	# player1 = models.ForeignKey('autentication.User', on_delete=models.SET_NULL, related_name='player')
	# player2 = models.ForeignKey('autentication.User', on_delete=models.SET_NULL, related_name='player')
	player1 =  models.CharField(max_length=255, default='player1')
	player2 =  models.CharField(max_length=255, default='player2')
	player3 =  models.CharField(max_length=255, default='player3')
	player4 =  models.CharField(max_length=255, default='player4')

	player_connected= models.PositiveIntegerField(default=0)#Nombre de joueurs connectes a la partie
	nb_players = models.IntegerField(choices=[(2, 'Deux joueurs'), (4, 'Quatre joueurs')], default=2)# Nombre de joueur = mode normal ou 2V2# Nombre de joueur = mode normal ou 2V2
	remote = models.BooleanField(default=False)# Remote ou pas
	# clients_connected = models.PositiveBigIntegerField(default=0)#Utile pour remote player

