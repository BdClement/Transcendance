from django.urls import reverse_lazy
from rest_framework.test import APITestCase

from game.models import Play
# Create your tests here.

#python manage.py test pour lancer l'ensemble des tests
# OU python manage.py test myApp
# OU python manage.py test myapp.tests.MyTestClass

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




