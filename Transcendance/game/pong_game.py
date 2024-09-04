import random

class PongGame:
    def __init__(self, width=800, height=600, paddle_width=10, paddle_height=100, ball_radius=10):
        self.width = width
        self.height = height
        self.paddle_width = paddle_width
        self.paddle_height = paddle_height
        self.ball_radius = ball_radius

        # Initialisation des positions
        self.player1_y = self.height // 2 - self.paddle_height // 2
        self.player2_y = self.height // 2 - self.paddle_height // 2

        # Initialisation de la balle
        self.ball_x, self.ball_y = self.width // 2, self.height // 2
        self.ball_speed_x, self.ball_speed_y = 5 * random.choice((1, -1)), 5 * random.choice((1, -1))

    def update_player1_position(self, y):
        self.player1_y = y

    def update_game_state(self):
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
