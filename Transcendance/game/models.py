from django.db import models

# Create your models here.

class Play(models.Model):
	# player1 = models.ForeignKey('autentication.User', on_delete=models.SET_NULL, related_name='player')
	# player2 = models.ForeignKey('autentication.User', on_delete=models.SET_NULL, related_name='player')
	player1 =  models.CharField(max_length=255, default='player1')
	player2 =  models.CharField(max_length=255, default='player2')
	player3 =  models.CharField(max_length=255, default='player3')
	player4 =  models.CharField(max_length=255, default='player4')

	current_payer = models.PositiveIntegerField(default=0)
	required_player = models.IntegerField(default=2)
	#clients_involved = models.IntegerField(default=1)

