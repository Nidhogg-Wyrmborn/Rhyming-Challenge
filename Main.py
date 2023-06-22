#### Keep a list of words, and check if new words rhyme with it

import os, pickle

rhyming = {}
debug = True

for word in open('phodict.txt', 'r').readlines():
	# word and phonemes is split by double space by sounds are split by single space
	rhyming[word.split('  ')[0]] = word.split('  ')[-1].split(' ')

def rhymeswith(wordA, wordB, syllables):
	# try to check the words
	try:
		# print extra details if debug
		if debug:
			print(wordA)
			print(wordB)
			print('get wordA')

		# get wordA from the rhyming dictionary
		wordA = rhyming[wordA.upper()]

		# print extra if debug
		if debug:
			print('wordA')
			print('get wordB')

		# get wordB from the rhyming dictionary
		wordB = rhyming[wordB.upper()]

		# print extra if debug
		if debug:
			print('wordB')
			print(wordA)
			print(wordB)

		# check if the last x phonemes match
		if wordA[-syllables:] == wordB[-syllables:]:
			# yes the 2 words rhyme (return True)

			# if debug print the phonemes
			if debug:
				print(wordA[-syllables:])
				print(wordB[-syllables:])
			return True

		# if debug print the phonemes
		if debug:
				print(wordA[-syllables:])
				print(wordB[-syllables:])

		# if not rhyming return None
		return None

	# if there is an exception
	except Exception as e:
		# if debug print exception type and exception content
		if debug:
			print(type(e), e)

		# state that word doesn't exist (when keyerror)
		print("Error word doesn't exist!")

		# return None
		return None

# list commands
commands = ['dispute', "bail", "pause"]

# ask if new game
new = input("new game? [y/n]\n- ")

# if new game
if new.lower().startswith('y'):

	# create empty word list
	words = []
	
	# get start word from user
	startword = str(input("start word:\n- "))

	# while user is unhappy with number of phonemes
	unsatis = True

	while unsatis:
		# get number of phonemes
		num_syl = int(input("number of phonemes (pronounced sounds):\n- "))

		# get a test word (one that rhymes for clarification)
		print(f"please supply a word that rhymes with {startword}")

		# input
		t = input("- ")

		# show the phonemes the program will use for comparison
		print(f"the phonemes shown are what you designated:")

		# print phonemes and the word they belong to
		print(rhyming[startword.upper()][-num_syl:], startword)
		print(rhyming[t.upper()][-num_syl:], t)

		# ask if it is satisfactory
		unsats = input("is this satisfactory?\n- ")

		# if yes then continue
		if unsats.lower().startswith('y'):
			unsatis = False
		else:
			# else repeat
			unsatis = True

	# create empty player list
	player = []

	# number of players is string
	num_players = ''

	# while num_players is not int
	while not isinstance(num_players, int):
		# get num of players (not necessarily int on input)
		num_players = input("number of players:\n- ")

		# if it is entirely digits
		if num_players.isdigit():
			# convert to int
			num_players = int(num_players)

	# for each player in range of 0 to the number of players
	for player_index in range(num_players):
		# print player index and ask for their name
		print(f"What is player {player_index}'s name?")

		# append input to player list
		player.append(input("- "))

		# clear screen
		os.system("cls")

		# print player index and player name
		print(f"player {player_index} is named {player[player_index]}")

	# set previous to None
	previous = None

	# set player turn to 0 (first player)
	player_turn = 0

	# initialize gamestate
	game_state = {"previous": previous, "player": player, "player_turn": player_turn, "words": words, "startword": startword, "num_syl": num_syl}

else:
	# if not newgame

	while True:
		# load game file
		game_file = input("Game file to load:\n- ")

		# if the game file exists
		if os.path.exists(game_file):

			# print loading game
			print("loading game")

			# open the file and load the pickled data
			with open(game_file, 'rb') as f:
				game_state = pickle.load(f)

			# extract data into variables
			words = game_state["words"]
			previous = game_state["previous"]
			player = game_state["player"]
			player_turn = game_state["player_turn"]
			startword = game_state["startword"]
			num_syl = game_state["num_syl"]

			# if debug show the variable contents
			if debug:
				print(words)
				print(previous)
				print(player)
				print(player_turn)
				print(startword)
				print(num_syl)
			break
		else:
			os.system("cls")
			print("file does not exist")
			continue

running = True

os.system("cls")

if previous:
	if previous in words:
		print('yes')
	else:
		print('no')
	print(previous)

while running:

	# state which player's turn
	print(f"player {player[player_turn]} - ", end="")

	# ask for word
	word = str(input("word:\n- "))

	# clear screen
	os.system("cls")

	# is "word" a command?
	if word.startswith("#"):
		# if word is a viable command
		if word.replace("#", "") in commands:
			# say it's recognized
			print('command recognized')

			# if it is a dispute then fix
			if word.replace("#","") == commands[0]:  # dispute
				# if there is something in previous
				if previous:
					# state the word being disputed
					print(f"disputing {previous}")

					# check if player is sure
					s = input('are you sure?\n- ')

					# if yes then dispute
					if s.lower().startswith('y'):
						# if it was accepted then deduct a point from player
						# if it was rejected then add a point to player
						if previous in words:
							# state action taken
							print('deduct a point from player')

							# go back one player's turn
							player_turn -= 1
							if player_turn < 0:
								player_turn = len(player)-1
						else:
							# state action taken
							print('append a point to player')

							# go forward one player's turn
							player_turn += 1
							if player_turn >= len(player):
								player_turn = 0
				else:
					# if there is nothing in previous then there is no word to dispute
					print('no word to dispute')

			# check if they bail (give up)
			if word.replace("#","") == commands[1]:  # bail (give up)
				# state the warning
				print(f"{player[player_turn]} is giving up!")

				# ask if the player is sure
				s = input("are you sure?\n- ")

				# if yes then remove player from list
				if s.lower().startswith('y'):
					# pop player
					player.pop(player_turn)

					# player_turn is now larger than number of players then fix
					if player_turn >= len(player):
						player_turn = 0

			# check if it is a pause command
			if word.replace("#","") == commands[2]:  # pause (save game state)
				# save game state into a dict
				game_state = {"previous": previous, "player": player, "player_turn": player_turn, "words": words, "startword": startword, "num_syl": num_syl}

				# pickle the dict into a file (as defined by user)
				with open(input("save file as (Example.txt, Example.Game, etc.):\n- "), 'wb') as f:
					game_state = pickle.dump(game_state, f)

					# set running to false
					running = False
		else:
			# if command not recognized then just continue
			print("command not recognized")
		# after command is run continue (no word to test)
		continue

	# check if the 2 words rhyme according to number of phonemes (pronounced sounds)
	s = rhymeswith(word, startword, num_syl)

	# if it is rhyming and the word hasn't already been used
	if s and not (word.lower() in words):
		# append the word to used words
		words.append(word.lower())

		# set previous to the current word
		previous = word.lower()

		# print that it was accepted and the word
		print("Yes")
		print(word)
	else:
		# if it fails then set previous to the current word
		previous = word.lower()

		# if debug print extra details
		if debug:
			print(word)
			print(word.lower() in words)

		# if the word has been said already state it
		if word.lower() in words:
			status = f"{word} was already said"

		# if the word doesn't rhyme state it
		else:
			status = f"{word} does not rhyme with {startword}"
		# state rejection and reason
		print("No,", status)
		# continue (don't change active player)
		continue

	# change to next player
	player_turn += 1
	if player_turn >= len(player):
		player_turn = 0