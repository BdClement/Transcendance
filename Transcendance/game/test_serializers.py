# from django.urls import reverse_lazy
from rest_framework.test import APITestCase

from .serializer import PlaySerializer

# from game.models import Play

class PlaySerializerTest(APITestCase):

	def test_serializer_valid(self):
		data = {'nb_players': 2, 'remote': True}
		serializer = PlaySerializer(data=data)
		self.assertTrue(serializer.is_valid())

	def test_serializer_invalid_data(self):
		data = {'nb_players': 3, 'remote': 'yes'}
		serializer = PlaySerializer(data=data)
		self.assertFalse(serializer.is_valid())
		self.assertIn('nb_players must be 2 or 4', serializer.errors['non_field_errors'])# erreur validation globale
		print(f'Is valid: {serializer.is_valid()}')
		print(f'Errors: {serializer.errors}')

