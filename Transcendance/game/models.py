import os
from dotenv import load_dotenv
import json
from django.db import models
from channels.db import database_sync_to_async
from authentication.models import User
from web3 import Web3, AsyncWeb3, AsyncHTTPProvider

load_dotenv()#A Faire dans settings plutot pour rendre cela disponible dans tout le projet
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
BLOCKCHAIN_NETWORK = os.getenv("BLOCKCHAIN_NETWORK")
# CONTRACT_ABI = os.getenv("CONTRACT_ABI")

# Create your models here.

class Play(models.Model):

	#Liason de ce joueur a cette partie, ce joueur peut etre lier a plusieurs parties
	player1 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='player1')
	player2 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='player2')
	player3 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='player3')
	player4 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='player4')

	#Lier la partie a un tournoi, la partie peut etre lier uniquemenr a ce tournoi
	#Liason a Tournament via une string car Django le permet pour eviter les boucles d'importations [Importer Tournament dans un fichier qui contient deja Tournament]
	#Django resout la string avec le model qui est declare plus tard dans le fichier
	tournament = models.ForeignKey('Tournament', related_name='plays', on_delete=models.SET_NULL, null=True)
	tournament_round = models.PositiveIntegerField(default=1)
	player_connected= models.PositiveIntegerField(default=0)#Nombre de joueurs connectes a la partie
	nb_players = models.IntegerField(choices=[(2, 'Deux joueurs'), (4, 'Quatre joueurs')], default=2)# Nombre de joueur = mode normal ou 2V2# Nombre de joueur = mode normal ou 2V2
	remote = models.BooleanField(default=False)# Remote ou pas
	date = models.DateTimeField(blank=True, null=True)
	is_finished = models.BooleanField(default=False)

	#Choix de stocker les resultats dans un JSONField pour permettre une flexibilite au client en terme d'affchage
	#Possibilite de modifier le field sans toucher a la base de donnee
	results = models.JSONField(null=True, blank=True)

	async def add_victory(self, nb_player):
		if nb_player == 1:
			player = self.player1
		elif nb_player == 2:
			player = self.player2
		elif nb_player == 3:
			player = self.player3
		elif nb_player == 4:
			player = self.player4
		else :
			player = None

		if player is not None :
			player.nbVictoires += 1
			await database_sync_to_async(player.save)()

	async def add_defeat(self, nb_player):
		if nb_player == 1:
			player = self.player1
		elif nb_player == 2:
			player = self.player2
		elif nb_player == 3:
			player = self.player3
		elif nb_player == 4:
			player = self.player4
		else :
			player = None

		if player is not None :
			player.nbDefaites += 1
			await database_sync_to_async(player.save)()

	def add_player(self, player):
		if self.player1 is None:
			self.player1 = player
		elif self.player2 is None:
			self.player2 = player
		elif self.player3 is None:
			self.player3 = player
		elif self.player4 is None:
			self.player4 = player
		else:
			return False
		self.save()
		return True

#Pour acceder aux parties dans un tournoi, utiliser l'attribut reverse genere automatiquement par Django grace au related_name
#Exemple ici tournament.plays.all()
class Tournament(models.Model):

	#Nombre joueur d'un tournoi flexible, soumis a des choix predefinis tout de meme (possibilite d'etendre ce choix dans le futur)
	nb_players = models.IntegerField(choices=[ (4, 'Quatre joueurs'), (8, 'Huit joueurs')], default=4)
	players = models.ManyToManyField(User, related_name='tournaments_players')
	results = models.JSONField(null=True, blank=True)
	is_finished = models.BooleanField(default=False)
	current_round = models.IntegerField(default=0)

	def create_next_round(self):

		if self.current_round == 0: #Cas du premier round
			players = self.players.all()
			# print(f'TEST dans create_next_round pour le premier tour === {players}')
			self.create_plays_for_new_round(players)
		else: #recherche de toutes les parties finies du round actuel
			plays_from_last_round = Play.objects.filter(tournament=self, tournament_round=self.current_round, is_finished=True)

			if plays_from_last_round.count() == 1:#La finale a ete jouee
				# print(f'TEST dans create_next_round quand la finale a ete jouee === {plays_from_last_round}')
				#Stockage de results avec plays_from_last_round
				final_play = plays_from_last_round.first()
				self.results = {
					"players": [player.id for player in self.players.all()],
					"winner": final_play.results.get('winners', []),#protection contre absence de 'winners'
					"final_score": final_play.results.get('score', {})
				}
				self.is_finished = True
				#Stockage BLOCKCHAIN
				self.store_score_on_blockchain()
			else :#Creation de toutes les parties du prochain round
				winners = []
				for play in plays_from_last_round:
					winner_ids = play.results.get('winners', [])
					winners.extend(User.objects.filter(id__in=winner_ids))#recherche des id dans le dictionnaire winners_id

				if winners:
					self.create_plays_for_new_round(winners)
				else:
					print(f"PROBLEME: Aucun gagnant trouvé pour le round {self.current_round}")

		if not self.is_finished:
			self.current_round += 1
		# print(f'TEST dans create_next_round current_round en fin dappel === {self.current_round}')
		self.save()

	def create_plays_for_new_round(self, players):
		players = list(players)

		#Ajout d'un joueur fictif en cas de joueur impairs
		if len(players) % 2 != 0:
			# print(f'AVERTISSEMENT: Nombre impair de joueurs ({len(players)}). Ajout d\'un "bye".')
			players.append(None)

		for i in range(0, len(players), 2):
			player1 = players[i]
			player2 = players[i + 1] if i + 1 < len(players) else None

			#Creation de partie avec les 2 joueurs
			if player1 and player2:
				Play.objects.create(
					player1=player1,
					player2=player2,
					tournament=self,
					tournament_round=self.current_round + 1
				)
			elif player1:#Simulation de partie gagne sur tapis vert pour le joueur seul en cas d'impair
				# print(f"Joueur {player1.username} passe automatiquement au prochain tour (bye)")
				simulate_play = Play.objects.create(
					player1=player1,
					player2=None,
					tournament=self,
					tournament_round=self.current_round + 1
				)
				simulate_play.results = {'winners': [player1.id], 'losers': 'player2', 'score': '3-0'}
				simulate_play.is_finished = True
				simulate_play.save()


	#Stockage Blockchain (Essayer d'abord dans une console)
	async def store_score_on_blockchain(self):
		#Isolattion des arguments a passe au contrat a la foncton storeScore
		# players = tournament.results.get('players', [])
		# winner = tournament.results.get('winner', [])
		# score = tournament.results.get('final_score', '')
		players = self.results.get('players', [])
		winner = self.results.get('winner', [])
		score = self.results.get('final_score', '')

		#Connexion au noeud blockchain
		#Utilisation plutot de AsyncWeb3.AsyncHTTPProvider plutot pour ne pas bloquer le serveur
		#Et de
		# w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_NETWORK))
		w3 = AsyncWeb3(AsyncHTTPProvider(BLOCKCHAIN_NETWORK))
		if await w3.is_connected():
			print("La connexion au Provider Blockchain a reussie")
		else :
			print("La connexion au Provider Blockchain a echouee")
			return

		#Test de la cle privee
		if PRIVATE_KEY is None:
			print("You must set PRIVATE_KEY environment variable")
			return
		if  not PRIVATE_KEY.startswith("0x"):
			print("Private key must start with 0x hex prefix")
			return

		# 	w3.eth.get_block('latest') #OTHER

		#Accession a l'abi depuis un fichier
		with open('../TournamentStoreABI.json', 'r') as file:
			contract_data = json.load(file)
		contract_ABI = contract_data.get("abi")

		#Accession au contrat sur le reseau blockchain
		deployed_contract = w3.eth.contract(address=CONTRACT_ADDRESS,abi=contract_ABI)
		#set nonce (Entier unique pour chaque transaction envoyee depuis une address Ethereum pour garantir l'ordre des transactions)
		nonce = await w3.eth.get_transaction_count("0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")
		#estimation de gas en focntion du reseau
		# gas = w3.eth.estimate_gas(tx)
		gas = await w3.eth.estimate_gas({
			"from": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
			"to": CONTRACT_ADDRESS,
			"data": deployed_contract.encode_abi(
				abi_eleement_identifier="storeScore",
				args=[self.id, players, winner, score]
			),
		})
		#estimation du gas_price
		gas_price = await w3.eth.gas_price
		#Build transaction
		tx = deployed_contract.functions.storeScore(self.id, players, winner, score).build_transaction({
			#to : l'adresse du contrat (deja set via deployed_contract)
			"from": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
			"nonce": nonce,
			#gas: Limite de gas maximale que la transaction peut consommer
			"gas": gas,
			#gasPrice: Le prix que l'emetteur est pret a payer pour une unite de gas (par defaut le prix du gas recommande par le reseau)
			"gasPrice": gas_price
			#value: Montant en wei envoyer dans la transaciton (function payable, par defaut 0)
			#data: donnee envoye (ici les arguments deja envoyes par la fonciton a partir de laquelle j'appelle build_transaction)
		})

		signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
		tx_hash = await w3.eth.send_raw_transaction(signed_tx.raw_transaction)
		#Utilise pour attendre la confirmation de la transaciton sur la blockchain [Synchrone a voir dans contexte ASYNCHRONE !]
		tx_receipt = await w3.eth.wait_for_transaction_receipt(tx_hash)

		#Appel de fonction depuis le contrat, 2 possibilites :
			#Fonction view qui ne modifie pas l'etat de la blockchain peut etre appeler avec call()
		# 	owner = deployed_contract.functions.getOwner().call()
		# 	print(f'Le owner du contrat est {owner} dapres le contrat')
			#Fonction qui modifie l'etat de la blockchain :
				#Utilisation de transact (de Web.py) qui cree par defaut la transaction et la signe automatiquement (sur un reseau local)

				#Preparation manuelle de la transaction avec buildTransaction en specifiant tout les parametres de la tx
				#Signature de la transaction avec la cle privee
				#Envoi de la tx signee sur le reseau blockchain


		#Preparation par default pour plus de simplicite pour des contrats simple
		#Preparation manuelle de la transaciton pour plus de controle sur la transaction, pour des contrats complexes et des transacitons a signer


#Gestion des excepitons du au contrat (try and catch avec gestion d'erreur propre)
	#ValueError(Reception de mauvais parametre par le contrat)
	#ContractLogicError(La logique du smart contract n'est as respectee ex: onlyOwner)
	#BadFunctionCallOutput(Exception levee lorsque le contrat renvoie des donnees indecodables dans le type attendu)
	#TransactionNotFound(Levee lorsque la transaction nest pas trouve ex :w3.eth.wait_for_transaction_receipt(tx_hash))
	#InsuficientFunds(Levee lorsque le solde de l'adresse est insuffisant pour l'action a mener)
	#GasPriceTooLow(Levee lorsque le prix de gas propose pour la tx est inferieur a celui requis)
	#InvalidAddress(Lorsqu'une adresse ne correspond pas)
	#ConnectionError(Levee lorsque Web3.py ne parvient pas a ce connecter au Provider)

#Gestion de asynchrone / synchrone
#Scalling de la solution sur un vrai reseau externe de test (Testnet)
