from channels.testing import WebsocketCommunicator
from django.test import TestCase

from game.routing import application
from game.models import Play

class PlayConsumerTest(TestCase):

	def setUp(self):
		self.play = Play.objects.create()

	async def test_connect_existing_game(self):
		communiactor = WebsocketCommunicator(application, "/ws/game/1/")

	async def test_can_connect_to_consumer(self):
		communicator = WebsocketCommunicator(application, "/ws/game/1/")
		connected, subprotocol = await communicator.connect()
		self.assertTrue(connected)
		await communicator.disconnect()
