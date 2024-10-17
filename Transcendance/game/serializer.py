from rest_framework import serializers

from game.models import Play, Tournament
from authentication.models import User

class PlayCreateSerializer(serializers.ModelSerializer):

	remote = serializers.BooleanField(required=True)
	nb_players = serializers.IntegerField(required=True)

	class Meta:
		model = Play
		fields = ['id', 'remote', 'nb_players']

	def validate(self, data):
		if not isinstance(data['remote'], bool):
			raise serializers.ValidationError({'Remote must be a boolean value.'})
		if data['nb_players'] not in [2, 4]:
			raise serializers.ValidationError('nb_players must be 2 or 4')
		return data

class PlayDetailSerializer(serializers.ModelSerializer):

	results = serializers.SerializerMethodField()#Personnalisation de la sortie de result

	class Meta:
		model = Play
		fields = ['nb_players', 'is_finished', 'results']

	# Methode responsable de transformer les id stocker dans la base de donnee en username pour les clients
	def get_results(self, obj):
		results = obj.results
		if results is None:
			return {}
		transformed_results = {}

		for key, value in results.items(): #iteration sur chaque element du dictionnaire results
			if isinstance(value, list):#Si l'element de results est une list (donc winners ou losers)
				transformed_players = []#stcoker les nouveau noms
				for item in value:#iteration sur chaque element d'un field de results
					if isinstance(item, int): #Si l'element est un ID
						player = User.objects.get(pk=item)
						if player:
							transformed_players.append(player.username)
						else:
							transformed_players.append(f'Unknown Player {item}')
					elif isinstance(item, str):#Si c'est un joueur inconnu on modifie rien
						transformed_players.append(item)
				transformed_results[key] = transformed_players
			else:
				transformed_results[key] = value
		return transformed_results







#La methode create d'un serializer est differente de la methode create d'un ViewSet
#Cette methode peut etre surchargee pour personnaliser la maniere dont un objet est cree a partir de donnees validees
#Ici, cela permet de valider alias_name pour s'en servir sans creer l'objet avec le field alias_names
#Tandis que la methode create du ViewSet gere la loqique HTTP (valider la requete, appel du serializer, envoi de reponses HTTP)
class TournamentSerializer(serializers.ModelSerializer):
	#Personnalisation des fields pour leur usages respectifs
	#Alias_name uniquement pour la validation
	alias_names = serializers.ListField(child=serializers.CharField(), write_only=True, required=True)
	nb_players = serializers.ChoiceField(choices=[ (4, 'Quatre joueurs'), (8, 'Huit joueurs')], required=True)
	is_finished = serializers.BooleanField(read_only=True)
	results = serializers.JSONField(read_only=True)
	id = serializers.IntegerField(read_only=True)

	class Meta:
		model = Tournament
		fields = ['id', 'nb_players', 'is_finished', 'results', 'alias_names']

	#Gerer la validation des alias_name dans validate
	def validate(self, data):
		# print(f'{data}')
		alias_name = data.get('alias_names', [])
		if len(alias_name) !=  data['nb_players']:
			raise serializers.ValidationError('Alias_names number must match nb_players')
		# Vérifier si alias_names contient des doublons
		if len(alias_name) != len(set(alias_name)):
			raise serializers.ValidationError('Alias_names must be unique')
		#Faire la validation des alias_name correspondant a players
		for alias in alias_name:
			if not User.objects.filter(alias=alias).exists():
				raise serializers.ValidationError(f'Player with alias {alias} does not exists')
		#Verifier que chaque alias n'est present qu'une fois sauf si dans Player on interdit les alias deja utilises
		return data

		#Recuperer tout les players correspondant aux alias_name recus
		#Verifier que tout les alias_names correspondent a un Player
		#ajouter les players au contexte de creation (data['players'])
		#return data

	def create(self, validated_data):
		#Retire les alias_names de validated_data car ils ne sont pas present dans l'objet Tournament
		alias_names = validated_data.pop('alias_names', [])
		# #Creation de l'objet Tournoi
		tournament = Tournament.objects.create(**validated_data)#Checker que le round ne puisse pas etre donne lors de la creation !
		#Recupuration des user ayant un alias dans alias_names
		players = User.objects.filter(alias__in=alias_names)
		#Ajouter les players a l'objet Tournament
		tournament.players.set(players)
		tournament.create_next_round()
		return tournament

