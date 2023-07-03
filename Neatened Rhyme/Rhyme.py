import os, pickle, sys, random, time

stresses = {}

debug = False

limit = 15

for stress in open('stresses.txt', 'r').readlines():
	stresses[stress.split('  ')[0]] = stress.split('  ')[-1]

def rhymeswith(wordA, wordB, phonemes, rhyming):
	try:
		wordA = rhyming[wordA.upper()]
		wordB = rhyming[wordB.upper()]

		if wordA[-phonemes:] == wordB[-phonemes:]:
			return True
		return False
	except Exception as e:
		if debug:
			print(type(e), e)
		return None

class Rhyme:
	# init
	def __init__(self, game_file=None, phonetic_dict="phodict.txt", Settings:dict=None):
		# create rhyming dictionary
		self.rhyming = {}

		# fill dictionary
		for word in open(phonetic_dict, 'r').readlines():
			self.rhyming[word.split('  ')[0]] = word.split('  ')[-1].split(' ')
		
		# create unsaid list and hintwords dictionary
		self.unsaid = []
		self.hintWords = {}

		# set gamefile to input gamefile
		self.game_file = game_file
		if game_file:
			# if gamefile then load
			self.game_state = self.load(game_file)
			self.startword = self.game_state["startword"]
			self.previous = self.game_state["previous"]
			self.player = self.game_state["player"]
			self.player_turn = self.game_state['player_turn']
			self.words = self.game_state['words']
			self.num_phnm = self.game_state['num_phnm']
			self.score = self.game_state['score']
			self.finals = self.game_state['finals']
			self.disallowed = self.game_state['disallowed']
		else:
			# otherwise create new game
			# choices = []

			# setup stress selection vars
			satis = False
			stressed = []
			choices = []
			ch = []

			# select random stress and the choices for startwords
			try:
				while not satis:
					self.stress = random.choice(list(stresses.keys()))
					self.num_phnm = int(stresses[self.stress])
					stressed.append(self.stress)
					choices = []
					for word in list(self.rhyming.keys()):
						# print(self.rhyming[word][-int(stresses[self.stress]):])
						# print(self.stress)
						# print(' '.join(self.rhyming[word][-int(stresses[self.stress]):]))
						# time.sleep(0.5)
						if ' '.join(self.rhyming[word][-self.num_phnm:]).replace("\n","") == self.stress:
							choices.append(word)
					if len(choices) > limit:
						satis = True
					ch.append(len(choices))

			except KeyboardInterrupt:
				print(stressed)
				print()
				print(ch)

			# create startword from choices
			self.startword = random.choice(choices) if not Settings else Settings['startword']

			# set previous to none
			self.previous = None

			# set player to imported settings or empty list if settings not supplied
			self.player = []
			if Settings:
				if 'playerlimit' in Settings.keys():
					self.player_limit = Settings["playerlimit"]

			# set current player's turn to 0 (first player)
			self.player_turn = 0

			# create empty lists and dictionaries for words score finals and disallowed words
			self.words = []
			self.score = []
			self.finals = {}
			self.disallowed = []

			self.in_progress = False

			# for each player append a score of 0
			for i in range(len(self.player)):
				self.score.append(0)

			# create default game_state
			self.game_state = {"startword"		: self.startword,
								"previous"		: self.previous,
								"player"		: self.player,
								"player_turn"	: self.player_turn,
								"words"			: self.words,
								"num_phnm"		: self.num_phnm,
								"score"			: self.score,
								"finals"		: self.finals,
								"disallowed"	: self.disallowed,
			}

			# create list of unsaid words that rhyme with starting word (based on phonemes extracted from stress)
			for word in list(self.rhyming.keys()):
				if rhymeswith(word, self.startword, self.num_phnm, self.rhyming) and word != self.startword and word.lower() not in self.words:
					self.unsaid.append(word.upper())

			# add startword to "said" words (prevent people getting cheat points)
			if self.startword not in self.words:
				self.words.append(self.startword.lower())

	# load settings
	def loadSettings(self, Settings):
		# try if fail then return false
		# try:
		# set playerlimit to var from settings
		self.playerlimit = Settings['playerlimit'] if 'playerlimit' in Settings.keys() else None
		self.startword = Settings['startword'] if 'startword' in Settings.keys() else self.startword

		if 'phonemes' in list(Settings.keys()):
			self.num_phnm = Settings['phonemes']
		else:
			nowork = True
			with open('stresses.txt', 'r').readlines() as stresses:
				for stress in stresses:
					if ' '.join(self.rhyming[self.startword]).endswith(stress.split('  ')[0]):
						self.num_phnm = stress.split('  ')[0]
						nowork = False
						break
					else:
						nowork = True
			if nowork:
				return [False, f"Stress is not available, please add stress from {self.rhyming[self.startword]} to stresses.txt"]

		for word in list(self.rhyming.keys()):
			if rhymeswith(word, self.startword, self.num_phnm, self.rhyming) and word != self.startword and word.lower() not in self.words:
				self.unsaid.append(word.upper())

		# if success return true
		return [True]
		# except Exception as e:
		# 	return [False, str(repr(e))]

	# add player
	def addPlayer(self, playerName):
		# try if fail then return false
		try:
			# if game in progress then return false
			if self.in_progress:
				return False

			# if number of players in excess or equal to playerlimit return false
			if len(self.player) >= self.playerlimit:
				return [False, "player cap"]
			else:
				# otherwise add the player and their corresponding score
				self.player.append(playerName)
				self.score.append(0)

				# if success return true
				return [True]
		except Exception as e:
			return [False, str(repr(e))]

	# remove player
	def removePlayer(self, playerName):
		# try if fail return false
		try:
			# if number of players less than or equal to 1
			if len(self.player) <= 1:
				# remove last player and score
				self.player.pop(0)
				self.score.pop(0)

				# return success and warning (class has no players, best to delete)
				return [True, "WARNING, This class has no players!"]
			else:
				# remove the player and their score
				self.player.pop(self.player.index(playerName))
				self.score.pop(self.player.index(playerName))

				# if success return True
				return [True]
		except:
			return [False]

	# load game from file
	def load(self, game_file):
		# load pickle from file
		return pickle.load(game_file)

	# guess a word
	def guess(self, word):
		return self._guess(word)

	# generate a hint
	def genHint(self):
		# create empty list
		hw = []

		# add a random word minus newline char
		hw.append(random.choice(self.unsaid).replace("\n",""))
		# add first character of word to the "hint"
		hw.append(hw[0][:1])

		# for the current player add the hint list
		self.hintWords[self.player[self.player_turn]] = hw

		# return hint list
		return hw

	# save gamestate as pickle to gamefile
	def save_game_state(self, game_file):
		pickle.dump(self.game_state, game_file)

	# guess word (class function)
	def _guess(self, word):
		# result is empty string
		result = ''

		# if guess is command
		if word.startswith("#"):
			# remove hash
			command = word.replace("#","")

			# print to log
			print("command prefix recognized")

			# if command is viable
			if command in commands or command == "D4ragkn17" or command == "D4sn0fn1r":
				# if command is dispute
				if command == commands[0]:  # dispute
					# if there was a previous word
					if self.previous:
						# check if you actually want to dispute
						s = self.verify(f"disputing {previous}")

						# if verified
						if s:
							# if previous was an accepted word
							if self.previous in self.words:
								# deduct a point from previous player
								result += 'deduct a point from player\n'

								# remove previous word from accepted words
								self.words.pop(self.words.index(self.previous))

								# add previous word to disallowed
								self.disallowed.append(self.previous)

								# go back one turn
								self.player_turn -= 1
								if self.player_turn < 0:
									self.player_turn = len(self.player)-1

								# remove 1 point
								self.score[self.player_turn] -= 1
							else:
								# append a point to player
								result += 'append a point to player\n'

								# append previous words to said
								self.words.append(self.previous)

								# add point
								self.score[self.player_turn] += 1

								# continue one turn
								self.player_turn += 1
								if self.player_turn >= len(self.player):
									self.player_turn = 0
					else:
						# if previous is Nonetype result is \/
						result += 'no word to dispute\n'

				# if command is bail
				if command == commands[1]:  # bail
					# verify
					s = self.verify(f"{self.player[self.player_turn]} is giving up!")

					# if verified
					if s:
						# add current player's score to finals dictionary with name as key
						self.finals[self.player[self.player_turn]] = self.score[self.player_turn]

						# remove player and score
						self.player.pop(self.player_turn)
						self.score.pop(self.player_turn)

						# if player_turn is out of bounds set to 0
						if self.player_turn >= len(player):
							self.player_turn = 0

				# if command is pause
				if command == commands[2]:  # pause
					# save game_state
					filename = self.save_game_state(self.game_file)

					# append filename to result
					result += f"saved as {filename}"+"\n"

				# if command is score
				if command == commands[3]:  # score
					# display scores for active players
					result += "-------Active Players-------\n"
					for player_index in range(len(self.player)):
						result += f"{self.player[player_index]} - {self.score[self.player_index]}"+"\n"

					# if there are any bailed players display them
					if len(list(self.finals.keys())) > 0:
						result += "-------Bailed Players-------\n"
						for player_name in list(self.finals.keys()):
							result += f"{player_name} - {self.finals[player_name]}"+"\n"

				# if command is list
				if command == commands[4]:  # list
					# display all used words
					result += "---------Used Words---------\n"
					for word in self.words:
						result += word+"\n"

				# is command is hint
				if command == commands[5]:  # hint
					# pick random hint type (percentage)
					hintType = random.randint(0,100)
					if hintType < 25:  # phonetic
						result += self.stress + "\n"

					# show starting letter of hint word (in dict of users)
					if hintType >= 25:  
						if self.player[self.player_turn] in self.hintWords.keys():

							# get hint word
							hw = self.hintWords[self.player[self.player_turn]]
							
							# if hint word has been used then create new hint word
							if hw[0] in self.words:
								hw = self.genHint()

							# otherwise reveal next letter in hint word
							else:
								hw[1] = hw[0][:len(hw[1])+1]
						else:
							# if player has not had a hint word before create one
							hw = self.genHint()
						# add hint to result
						result += hw[1]+"\n"

				# if command is hidden command 1
				if command == "D4ragkn17":
					# return all unsaid words
					result += '\n'.join(self.unsaid)+'\n'

				# if command is hidden command 1
				if command == "D4sn0fn1r":
					# return a random word that rhymes with starting word
					result += random.choice(self.unsaid) + "\n"
			else:
				# if command is not viable say so
				result += "command not recognized\n"
		# input is guess and not command
		else:
			# check if guess rhymes with starting word
			s = rhymeswith(word, self.startword, self.num_phnm, self.rhyming)

			# if it rhymes, has not been said yet, and is allowed
			if s and not (word.lower() in self.words or word.lower() in self.disallowed):
				# append guess to words
				self.words.append(word.lower())

				# set previous to guess
				self.previous = word.lower()

				# add status to result
				result += f'Yes, {word.lower()} rhymes with {self.startword}'+'\n'

				# remove word from list of unsaid words
				self.unsaid.pop(self.unsaid.index(word.upper()))

				# add a point to player
				self.score[self.player_turn] += 1

				# continue to next player
				previous_player = self.player_turn
				self.player_turn += 1
				if self.player_turn >= len(self.player):
					self.player_turn = 0

			# if guess is not viable
			else:
				# set previous to guess
				self.previous = word.lower()

				# if guess already said
				if word.lower() in self.words:
					# say so
					status = f"{word} was already said"

				# if guess is not bool (doesn't exist in word list)
				elif not isinstance(s, bool):
					# say so
					status = f"{word} doesn't exist"

				# if word doesn't rhyme
				else:
					# say so
					status = f"{word} does not rhyme with {self.startword}"

				# return status
				result += f"No, {status}" + "\n"
				previous_player = self.player_turn

		# return playername and result
		return [self.player[previous_player], result]

def exampleMain(startword:str, playerlimit:int, players:list=None, phonemes:int=None, debug:bool=False):
	r = Rhyme()

	settings = {}
	settings['playerlimit'] = playerlimit
	settings['startword'] = startword
	if isinstance(phonemes, int):
		settings['phonemes'] = phonemes

	result = r.loadSettings(settings)
	if not result[0]:
		raise Exception("Load settings Failed", result[1])

	if players:
		for player in players:
			result = r.addPlayer(player)
			if result[0]:
				print(f"successfully add {player}")
			else:
				print(failed, result[1])

	if debug:
		print(r.player)
		print(r.player_turn)

	running = True
	while running:
		if debug:
			guess = random.choice(list(r.rhyming.keys()))
		else:
			guess = input('Guess - ')
		if guess == "#quit":
			running = False
			continue
		else:
			print(''.join(r.guess(guess)))

if __name__ == '__main__':
	test = input('[T]est or [P]lay?\n- ').lower()[0]
	# test = 't'
	if test == 't':
		r = Rhyme()
		# debug possible scenarios
		start = {'nation': 4, 'section':5, 'fly':2, 'tresspass':2, 'ration':4}

		# create and load players
		settings = {}
		settings['playerlimit'] = 4
		settings['startword'] = random.choice(list(start.keys()))
		settings['phonemes'] = start[settings['startword']]
		result = r.loadSettings(settings)
		if result[0]:
			# success
			pass
		else:
			if len(result) > 1:
				print(result[1])
			# fail
			raise Exception("Load Settings Failed")
			quit()

		players = [f'dummy {i}' for i in range(5)]

		for player in players:
			if r.addPlayer(player):
				print(f'successfully add {player}')
			else:
				print('Failed')

		print(r.player)
		print(r.player_turn)

		# list of words to guess
		toGuess = ["station", "insurrection", "lie", "constant", "brass", "passion"]

		result = []
		# guess words including each command
		for word in toGuess:
			print(f'guessing {word}')
			result.append(r.guess(word))

		for res in result:
			print(repr(res))
	else:
		debug = True if input('debug? ').lower().startswith('y') else False
		startword = input('Start word:\n- ').lower()
		playerlimit = input('player limit:\n- ')
		if playerlimit.isdigit():
			playerlimit = int(playerlimit)
		else:
			playerlimit = -1

		players = ['']

		playerNames = [f'dummy {i}' for i in range(25)]
		playerNames.append('#?quit')

		while players[-1].lower() != '#?quit':
			if debug:
				if players[0] == '':
					players.pop(-1)
				players.append(random.choice(playerNames))
				if players[-1] == '#?quit' and len(players) == 1:
					players.pop(-1)
					players.append(random.choice(playerNames[0:-2]))
			else:
				players.append(input(f"player name:\n- "))
		players.pop(-1)

		phonemes = input('phonemes (optional [unless error]):\n- ')

		if phonemes.isdigit():
			phonemes = int(phonemes)

		else:
			phonemes = None

		exampleMain(startword, playerlimit, players, phonemes, debug)
