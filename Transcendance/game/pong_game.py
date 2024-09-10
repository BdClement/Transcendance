import random
import asyncio
import django
import os

from channels.layers import get_channel_layer
from channels.db import database_sync_to_async

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
        self.game_group_name = game_group_name
        self.channel_layer = get_channel_layer()

        # Initialisation des positions Y
        self.players_y = {1: self.height // 2 - self.paddle_height // 2,
                          2: self.height // 2 - self.paddle_height // 2}
        # Initialisation des positions X
        self.players_x =    {1: 0,
                            2: self.width - 10}
        #initialisation des scores
        self.team_scores = { 1: 0,
                            2: 0}
        #Initialisation des positions des players 3 et 4 si necessaire
        if self.play.nb_players == 4:
            #Update pour mettre a  jour le dictionnaire (simialire a dictionnaire['nouvelle_Cle] = Valeur)
            self.players_y.update({
            3: self.players_y[1],
            4: self.players_y[1]
        })
            self.players_x.update({
            3: self.width // 4,
            4: (self.width // 4) * 3
        })

        # Initialisation de la balle
        self.ball_x, self.ball_y = self.width // 2, self.height // 2
        self.ball_speed_x, self.ball_speed_y = 5 * random.choice((1, -1)), 5 * random.choice((1, -1))

        # Cas Remote a ajouter


    async def start_game(self):
        if not self.is_running:
            self.is_running = True
            # Cretion d'une tache en arreire plan pour que la fonction puisse terminer son execution alors meme que
            # la boucle tourne en arriere plan et ce pour que le Consumer ne soit pas bloque
            self.game_loop_task = asyncio.create_task(self.game_loop())

    async def stop_game(self):
        print('Appel de STOP_GAME')
        # Stockage de resultats si la partie est terminee
        print(f'TEST de is_finished = {self.play.is_finished}')
        if self.play.is_finished:
            #Identification du winner et du loser (partie 1v1)
            if self.team_scores[1] == 3:
                #Listes d'objets contenant des Player
                winners = [self.play.player1]
                losers = [self.play.player2]
            else:
                winners = [self.play.player2]
                losers = [self.play.player1]
            #Ajout du winner et loser supplementaire en cas de mode multijoueur (2v2)
            if self.play.nb_players == 4:
                winners.append(self.play.player3 if self.team_scores[1] == 3 else self.play.player4)
                losers.append(self.play.player4 if self.team_scores[1] == 3 else self.play.player3)
            #Dictionnaire player concerne (cle): score du joueur (valeur)
            scores = {
                "player1": self.team_scores[1],#remplacer par winners[0].name
                "player2": self.team_scores[2]
            }
            if self.play.nb_players == 4:
                scores.update({
                    "player3": self.team_scores[1],
                    "player4": self.team_scores[2]
                })
            print(f'Affichage de scores pour TESTER = {scores}')
            # fonction du model Play qui enregistrera dans la base de donnee les resultats
            await self.play.end_game(winners, losers, scores)
        print("Arret de la tache en arriere plan")
        # Arret de la tache en arriere plan
        if self.is_running:
            self.is_running = False
            self.game_loop_task.cancel()
            await self.game_loop_task
        print("TEST dans stop_game apres l'arret de la tach en arriere plan")


# A modifier avec calcul ici !
    async def update_player_position(self, player_number, y):
        if player_number in self.players_y:
            if y == 'up' and self.players_y[player_number] != 0:
                self.players_y[player_number] -= 10
            elif y == 'down' and self.players_y[player_number] != self.height - self.paddle_height:
                self.players_y[player_number] += 10

    async def update_game_state(self):
        # Update ball position
        self.ball_x += self.ball_speed_x
        self.ball_y += self.ball_speed_y

        # Gestion des collisions avec les murs du haut et du bas
        if self.ball_y - self.ball_radius <= 0 or self.ball_y + self.ball_radius >= self.height:
            self.ball_speed_y *= -1
            # Ajuster la position de la balle pour éviter qu'elle ne reste au mur
            self.ball_y = max(self.ball_radius, min(self.height - self.ball_radius, self.ball_y))

        # Gestion des collisions avec les raquettes
        if (self.ball_x - self.ball_radius <= self.paddle_width and
            self.players_y[1] < self.ball_y < self.players_y[1] + self.paddle_height):
            self.ball_speed_x = abs(self.ball_speed_x)  # Rebond vers la droite
            self.ball_x = self.paddle_width + self.ball_radius  # Évite que la balle ne reste à la raquette
        elif (self.ball_x + self.ball_radius >= self.width - self.paddle_width and
            self.players_y[2] < self.ball_y < self.players_y[2] + self.paddle_height):
            self.ball_speed_x = -abs(self.ball_speed_x)  # Rebond vers la gauche
            self.ball_x = self.width - self.paddle_width - self.ball_radius  # Évite que la balle ne reste à la raquette

        if self.play.nb_players == 4:
            if (self.ball_x - self.ball_radius <= self.players_x[3] + self.paddle_width and
                self.players_x[3] <= self.ball_x and
                self.players_y[3] < self.ball_y < self.players_y[3] + self.paddle_height):
                self.ball_speed_x = abs(self.ball_speed_x)  # Rebond vers la droite
                self.ball_x = self.players_x[3] + self.paddle_width + self.ball_radius  # Repositionner la balle

            if (self.ball_x + self.ball_radius >= self.players_x[4] and
                self.players_x[4] >= self.ball_x and
                self.players_y[4] < self.ball_y < self.players_y[4] + self.paddle_height):
                self.ball_speed_x = -abs(self.ball_speed_x)  # Rebond vers la gauche
                self.ball_x = self.players_x[4] - self.ball_radius

        # Gestion des points et réinitialisation de la balle
        if self.ball_x - self.ball_radius <= 0:
            # Point pour le joueur 2
            self.team_scores[2] += 1
            await self.reset_ball()
            # Incrémenter le score du joueur 2 ici
        elif self.ball_x + self.ball_radius >= self.width:
            # Point pour le joueur 1
            self.team_scores[1] += 1
            await self.reset_ball()
        # if self.team_scores[1] == 3 or self.team_scores[2] == 3:
        #     print("FIN DE PARTIE !")
        #     await self.stop_game()

        #Retourne l'ensemble des donnees de la partie
        data = {
            'ball': (self.ball_x, self.ball_y),
            'player_1':(self.players_x[1], self.players_y[1],),
            'player_2': (self.players_x[2], self.players_y[2]),
            'score_team_1' :self.team_scores[1],
            'score_team_2' :self.team_scores[2]
        }

        if self.play.nb_players == 4:
            data['player_3'] = (self.players_x[3], self.players_y[3])
            data['player_4'] = (self.players_x[4], self.players_y[4])
        # Retourne les positions actuelles pour les envoyer via WebSocket
        return data

    async def reset_ball(self):
        # Réinitialiser la position de la balle au centre
        self.ball_x, self.ball_y = self.width // 2, self.height // 2
        # Donner une direction aléatoire à la balle
        self.ball_speed_x = 5 * random.choice((1, -1))
        self.ball_speed_y = 5 * random.choice((1, -1))

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
            await asyncio.sleep(1 / 60)
            if self.team_scores[1] == 3 or self.team_scores[2] == 3:
                print("Fin de partie detecte dans game_loop")
                self.play.is_finished = True
                print("Mise a True de is_finished")
                await database_sync_to_async(self.play.save)()
                print("Sauvegarde du model dans la DB")
                await self.stop_game()
                print("Appel de stop_game done ")
                ## TEST de logique d'enregistrement du score en cours, A FINIR !
        #Enregistrement dans l'objet Play du score ?

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
