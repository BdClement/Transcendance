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

	remote = serializers.BooleanField(required=True)
	nb_players = serializers.IntegerField(required=True)

	class Meta:
		model = Play
		fields = ['id', 'remote', 'nb_players']

	def validate(self, data):

		# print("Received data:", data) #TEST
		if not isinstance(data['remote'], bool):
			raise serializers.ValidationError({'Remote must be a boolean value.'})
		if data['nb_players'] not in [2, 4]:
			raise serializers.ValidationError('nb_players must be 2 or 4')
		return data


