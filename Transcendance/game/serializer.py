from rest_framework import serializers

from game.models import Play

class BallPositionSerializer(serializers.Serializer):
	x = serializers.FloatField()
	y = serializers.FloatField()

class PlayerPositionSerializer(serializers.Serializer):
	player_id = serializers.CharField()
	x = serializers.FloatField()
	y = serializers.FloatField()

class PlaySerializer(serializers.ModelSerializer):

	class Meta:
		model = Play
		fields = ['id','player1','player2']
