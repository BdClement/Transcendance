from django.urls import reverse_lazy, reverse
from rest_framework.test import APITestCase

from game.models import Play, Tournament
from authentication.models import User
# Create your tests here.

#python manage.py test pour lancer l'ensemble des tests
# OU python manage.py test myApp
# OU python manage.py test myapp.tests.MyTestClass

#La bonne pratique en terme de test est de creer des test unitaires pour chaque element pour verifier leur viabilite
#Et de creer des tests d'integration lorsque plusieurs elements partagent certaines logiques pour verifier la viabilite de certains scénario

class TestPlayAPI(APITestCase):
	#Stockage de l'url dans un attribut de classe
	url_create = reverse_lazy('play_create')

	def test_create_valid(self):
		# #Test qu'aucune partie existe initialement
		self.assertFalse(Play.objects.exists())
		# #Test de creation d'une partie via l'API
		response = self.client.post(self.url_create, data={'remote': False, 'nb_players': 2})
		self.assertEqual(response.status_code, 201)
		play = Play.objects.get(pk=1)
		self.assertEqual(play.remote, False)
		self.assertEqual(play.nb_players, 2)

	def test_create_errors(self):
		#No remote field
		response_no_remote = self.client.post(self.url_create, data={'nb_players': 2})
		self.assertEqual(response_no_remote.status_code, 400)
		#Bad remote field
		response_bad_remote = self.client.post(self.url_create, data={'remote': 'Wesh', 'nb_players': 2})
		self.assertEqual(response_bad_remote.status_code, 400)
		#No nb_players field
		response_no_nb_players = self.client.post(self.url_create, data={'remote': False})
		self.assertEqual(response_no_nb_players.status_code, 400)
		#Bad nb_players field
		response__bad_nb_players = self.client.post(self.url_create, data={'remote': False, 'nb_players': 3})
		self.assertEqual(response__bad_nb_players.status_code, 400)

	def test_detail_valid(self):
		play = Play.objects.create()
		self.url_detail = reverse_lazy('play_detail', kwargs={'play_id': play.id})
		response = self.client.get(self.url_detail)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(play.nb_players, 2)
		self.assertEqual(play.is_finished, False)
		self.assertIsNone(play.results)

	def test_detail_errors(self):
		url_detail_no_id = 'api/play/detail'# Pas d'utilisation de reverse_lazy car l'url initial attend un argument obligatoire
		url_detail_bad_id = reverse_lazy('play_detail', kwargs={'play_id': 'Not an ID'})
		url_detail_id_does_not_exist = reverse_lazy('play_detail', kwargs={'play_id': 1000})

		response_no_id = self.client.get(url_detail_no_id)
		self.assertEqual(response_no_id.status_code, 404)
		response_bad_id = self.client.get(url_detail_bad_id)
		self.assertEqual(response_bad_id.status_code, 400)
		repsonse_id_does_not_exist = self.client.get(url_detail_id_does_not_exist)
		self.assertEqual(repsonse_id_does_not_exist.status_code, 404)



class TestTournamentAPI(APITestCase):

	def setUp(self):
		self.tournament = Tournament.objects.create()
		self.url = reverse_lazy('tournament-list')
		self.url_detail = reverse_lazy('tournament-detail', kwargs={'pk': self.tournament.pk})
		self.url_bad_id = reverse_lazy('tournament-detail', kwargs={'pk': 'TEST'})
		self.url_does_not_exist = reverse_lazy('tournament-detail', kwargs={'pk': 1500})
		#Creer des joueurs fictifs pour simuler les liens avec les alias_names
		self.player1 = User.objects.create(username="salut1", alias="test1", email="test1@42.fr")
		self.player1 = User.objects.create(username="salut2", alias="test2", email="test2@42.fr")
		self.player1 = User.objects.create(username="salut3", alias="test3", email="test3@42.fr")
		self.player1 = User.objects.create(username="salut4", alias="test4", email="test4@42.fr")
		self.player1 = User.objects.create(username="salut5", alias="test5", email="test5@42.fr")
		self.player1 = User.objects.create(username="salut6", alias="test6", email="test6@42.fr")
		self.player1 = User.objects.create(username="salut7", alias="test7", email="test7@42.fr")
		self.player1 = User.objects.create(username="salut8", alias="test8", email="test8@42.fr")

	def test_create_valid(self):
		# Test tournoi a 4
		response_4 = self.client.post(self.url, data={ 'nb_players': 4, 'alias_names': ['test1', 'test2', 'test3', 'test4']})
		self.assertEqual(response_4.status_code, 201)
		tournament_created = Tournament.objects.get(pk=2)
		self.assertEqual(tournament_created.nb_players, 4)
		plays_created = Play.objects.filter(tournament=tournament_created, tournament_round=tournament_created.current_round, is_finished=False)
		# print(f'is_finished == {tournament_created.is_finished}')
		# print(f'current_round == {tournament_created.current_round}')
		# print(plays_created)
		# print(f'{plays_created.first().player1.alias} va affronter {plays_created.first().player2.alias}')
		# print(f'{plays_created.last().player1.alias} va affronter {plays_created.last().player2.alias}')
		self.assertEqual(plays_created.count(), 2)
		self.assertEqual(plays_created.first().tournament_round, 1)

		#test tournoi a 8
		response_8 = self.client.post(self.url, data={ 'nb_players': 8, 'alias_names': ['test1', 'test2', 'test3', 'test4', 'test5', 'test6', 'test7', 'test8']})
		# print(f'REPONSE ===== {response_8.data}')
		self.assertEqual(response_8.status_code, 201)
		tournament_created = Tournament.objects.get(pk=3)
		self.assertEqual(tournament_created.nb_players, 8)
		plays_created2 = Play.objects.filter(tournament=tournament_created, tournament_round=tournament_created.current_round, is_finished=False)
		# print(f'{plays_created2.first().player1.alias} va affronter {plays_created2.first().player2.alias}')
		# print(f'{plays_created2.last().player1.alias} va affronter {plays_created2.last().player2.alias}')
		# print(plays_created2)
		self.assertEqual(plays_created2.count(), 4)
		self.assertEqual(plays_created2.first().tournament_round, 1)


	def test_create_errors(self):
		#Pas de donnee envoye dans la requete
		response_no_data_sent = self.client.post(self.url)
		self.assertEqual(response_no_data_sent.status_code, 400)
		#Field nb_players manquant
		response_no_nb_players = self.client.post(self.url, data={'alias_names': ['test1', 'test2', 'test3', 'test4']})
		self.assertEqual(response_no_nb_players.status_code, 400)
		#Field alias_names manquant
		reponse_no_alias_names = self.client.post(self.url, data={ 'nb_players': 4})
		self.assertEqual(reponse_no_alias_names.status_code, 400)
		#Field nb_players errone
		response_bad_nb_players = self.client.post(self.url, data={ 'nb_players': 6, 'alias_names': ['test1', 'test2', 'test3', 'test4']})
		self.assertEqual(response_bad_nb_players.status_code, 400)
		#Alias_names different du nb_players attendu
		response_nb_players_nb_alias_different = self.client.post(self.url, data={ 'nb_players': 4, 'alias_names': ['test1', 'test2', 'test3']})
		self.assertEqual(response_nb_players_nb_alias_different.status_code, 400)
		#Test avec des alias qui ne sont pas relier a aucun nom
		response_bad_alias_names = self.client.post(self.url, data={ 'nb_players': 4, 'alias_names': ['Alias', 'Does', 'Not', 'Exist']})
		self.assertEqual(response_bad_alias_names.status_code, 400)
		# Test avec des alias_name en doublon
		response_double_alias_name = self.client.post(self.url, data={ 'nb_players': 4, 'alias_names': ['test1', 'test1', 'test2', 'test3']})
		self.assertEqual(response_double_alias_name.status_code, 400)



	def test_detail_valid(self):
		response = self.client.get(self.url_detail)
		# print(f'REPONSE ===== {response.data}')
		self.assertEqual(response.status_code, 200)


	def test_detail_errors(self):
		response_bad_id = self.client.get(self.url_bad_id)
		self.assertEqual(response_bad_id.status_code, 404)
		response_does_not_exist = self.client.get(self.url_does_not_exist)
		self.assertEqual(response_does_not_exist.status_code, 404)
