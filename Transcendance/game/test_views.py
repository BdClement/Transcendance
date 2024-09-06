from django.urls import reverse_lazy
from rest_framework.test import APITestCase

from game.models import Play
# Create your tests here.

class TestPlayAPI(APITestCase):
	#Stockage de l'url dans un attribut de classe
	url_create = reverse_lazy('create_play')

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


