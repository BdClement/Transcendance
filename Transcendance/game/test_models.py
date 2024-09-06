from django.test import TestCase

from game.models import Play

class TestPlayModel(TestCase):

	def setUp(self):
		self.play = Play.objects.create(nb_players=4, remote=True)

	def test_model_creation(self):

		self.assertEqual(self.play.nb_players, 4)
		self.assertEqual(self.play.remote, True)

	def test_default_value(self):
		play = Play.objects.create()
		self.assertEqual(play.player1, 'player1')
		self.assertEqual(play.player2, 'player2')
		self.assertEqual(play.player3, 'player3')
		self.assertEqual(play.player4, 'player4')
		self.assertEqual(play.player_connected, 0)
		self.assertEqual(play.nb_players, 2)
		self.assertEqual(play.remote, False)
		self.assertEqual(play.clients_connected, 0)


