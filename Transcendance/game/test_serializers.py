# from django.urls import reverse_lazy
from rest_framework.test import APITestCase

from .serializer import PlayCreateSerializer, PlayDetailSerializer
from game.models import Play

# from game.models import Play

class TestPlaySerializer(APITestCase):

	def test_serializer_valid(self):
		data = {'nb_players': 2, 'remote': True}
		serializer = PlayCreateSerializer(data=data)
		self.assertTrue(serializer.is_valid())

	def test_serializer_invalid_data(self):
		data = {'nb_players': 3, 'remote': 'yes'}
		serializer = PlayCreateSerializer(data=data)
		self.assertFalse(serializer.is_valid())
		self.assertIn('nb_players must be 2 or 4', serializer.errors['non_field_errors'])# erreur validation globale
		# print(f'Is valid: {serializer.is_valid()}')
		# print(f'Errors: {serializer.errors}')

	def test_serialization(self):
		data = {'nb_players': 2, 'remote': True}
		serializer = PlayCreateSerializer(data=data)
		self.assertTrue(serializer.is_valid())
		instance = serializer.save()
		self.assertEqual(instance.nb_players, data['nb_players'])
		self.assertEqual(instance.remote, data['remote'])


class TestPlayDetailSerializer(APITestCase):

	def setUp(self):
		self.play = Play.objects.create(nb_players=2, is_finished=False, results={})
		self.serializer = PlayDetailSerializer(instance=self.play)

	def test_serializer_valid(self):
		data = self.serializer.data
		self.assertEqual(set(data.keys()), {'nb_players', 'is_finished', 'results'})
		self.assertEqual(data['nb_players'], self.play.nb_players)
		self.assertEqual(data['is_finished'], self.play.is_finished)
		self.assertEqual(data['results'], self.play.results)
	# Si l'API permettait via ce serializer de creer ou modifier un objet Play, il faudrait tester la deserialisation

