import random
import asyncio
import django
import os

from channels.layers import get_channel_layer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Transcendance.settings')
django.setup()

from .models import Play



class PongGame:
    def __init__(self, game_id, game_group_name):
        self.width = 800
        self.height = 600
        self.paddle_width = 10
        self.paddle_height = 100
        self.ball_radius = 10
        self.is_running = False
        self.play = Play.objects.get(pk=game_id)
        # self.game_id = game_id # Pour acceder a la partie et compter les points et identifier la partie concernee ?
        self.game_group_name = game_group_name
        self.channel_layer = get_channel_layer()

        # Initialisation des positions
        self.player1_y = self.height // 2 - self.paddle_height // 2
        self.player2_y = self.height // 2 - self.paddle_height // 2

        # Initialisation de la balle
        self.ball_x, self.ball_y = self.width // 2, self.height // 2
        self.ball_speed_x, self.ball_speed_y = 5 * random.choice((1, -1)), 5 * random.choice((1, -1))

        # if self.play.nb_players == 4:
            # Ajouter initialisation pour player 3 et $

        # Cas Remote a ajouter


    async def start_game(self):
        if not self.is_running:
            self.is_running = True
            # Cretion d'une tache en arreire plan pour que la fonction puisse terminer son execution alors meme que
            # la boucle tourne en arriere plan et ce pour que le Consumer ne soit pas bloque
            self.game_loop_task = asyncio.create_task(self.game_loop())

    async def stop_game(self):
        if self.is_running:
            self.is_running = False
            self.game_loop_task.cancel()# Gestion du score / fin de partie Avant?
            await self.game_loop_task

    async def update_game_state(self):
        # Update ball position
        self.ball_x += self.ball_speed_x
        self.ball_y += self.ball_speed_y

        # Rebond sur les murs du haut et du bas
        if self.ball_y - self.ball_radius <= 0 or self.ball_y + self.ball_radius >= self.height:
            self.ball_speed_y *= -1

        # Rebond sur les raquettes
        if (self.ball_x - self.ball_radius <= self.paddle_width and self.player1_y < self.ball_y < self.player1_y + self.paddle_height) or \
        (self.ball_x + self.ball_radius >= self.width - self.paddle_width and self.player2_y < self.ball_y < self.player2_y + self.paddle_height):
            self.ball_speed_x *= -1

        # Rebond sur les murs de gauche et de droite
        if self.ball_x - self.ball_radius <= 0 or self.ball_x + self.ball_radius >= self.width:
            self.ball_x, self.ball_y = self.width // 2, self.height // 2
            self.ball_speed_x *= random.choice((1, -1))
            self.ball_speed_y *= random.choice((1, -1))
        # Retourne les positions actuelles pour les envoyer via WebSocket
        return {
            'ball_x': self.ball_x,
            'ball_y': self.ball_y,
            'player1_y': self.player1_y,
            'player2_y': self.player2_y
        }

    # A modifier ???
    async def update_player_position(self, y):
        # self.player1_y = y
        if y.get('player1') is not None:
            self.player1_y = y['player1']
        elif y.get('player2') is not None:
            self.player2_y = y['player2']
        elif y.get('player3') is not None:
            self.player3_y = y['player3']
        elif y.get('player4') is not None:
            self.player4_y = y['player4']

    async def game_loop(self):
        while self.is_running:
            game_state = await self.update_game_state()
            await self.channel_layer.group_send(
                self.game_group_name,
                {
                    'type': 'update_game',
                    **game_state
                }
            )
            await asyncio.sleep(1 / 30)
        # Gestion du score en fin de partie ?

# A faire :
# Comprendre les formats de reception de message d'un client pour ajuster update_player1_position
# Mettre condition de fin a game_loop + Gestion du score en fin de partie ?



# PONG GAME DE JULIEN
# import random

# class PongGame:
#     def __init__(self, width=800, height=600, paddle_width=10, paddle_height=100, ball_radius=10):
#         self.width = width
#         self.height = height
#         self.paddle_width = paddle_width
#         self.paddle_height = paddle_height
#         self.ball_radius = ball_radius

#         # Initialisation des positions
#         self.player1_y = self.height // 2 - self.paddle_height // 2
#         self.player2_y = self.height // 2 - self.paddle_height // 2

#         # Initialisation de la balle
#         self.ball_x, self.ball_y = self.width // 2, self.height // 2
#         self.ball_speed_x, self.ball_speed_y = 5 * random.choice((1, -1)), 5 * random.choice((1, -1))

#     def update_player1_position(self, y):
#         self.player1_y = y

#     def update_game_state(self):
#         # Update ball position
#         self.ball_x += self.ball_speed_x
#         self.ball_y += self.ball_speed_y

#         # Rebond sur les murs du haut et du bas
#         if self.ball_y - self.ball_radius <= 0 or self.ball_y + self.ball_radius >= self.height:
#             self.ball_speed_y *= -1

#         # Rebond sur les raquettes
#         if (self.ball_x - self.ball_radius <= self.paddle_width and self.player1_y < self.ball_y < self.player1_y + self.paddle_height) or \
#            (self.ball_x + self.ball_radius >= self.width - self.paddle_width and self.player2_y < self.ball_y < self.player2_y + self.paddle_height):
#             self.ball_speed_x *= -1

#         # Rebond sur les murs de gauche et de droite
#         if self.ball_x - self.ball_radius <= 0 or self.ball_x + self.ball_radius >= self.width:
#             self.ball_x, self.ball_y = self.width // 2, self.height // 2
#             self.ball_speed_x *= random.choice((1, -1))
#             self.ball_speed_y *= random.choice((1, -1))

#         # Retourne les positions actuelles pour les envoyer via WebSocket
#         return {
#             'ball_x': self.ball_x,
#             'ball_y': self.ball_y,
#             'player1_y': self.player1_y,
#             'player2_y': self.player2_y
#         }
