from django.test import TestCase

from game.models import Play, Tournament

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

class TestTournamentModel(TestCase):
	def setUp(self):
		self.tournament = Tournament.objects.create()

	# def test_model_creation(self):
	# 	self.assertTrue(self.tournament.exist())

	def test_default_value(self):
		self.assertEqual(self.tournament.nb_players, 4)
		self.assertEqual(self.tournament.is_finished, False)
		self.assertEqual(self.tournament.results, None)

	# def test_validation(self):
		#Pour l'instant aucune validation directement dans le model

	#def test_relationship(self):
		#Test a faire lorsque le model Player sera operationnel


