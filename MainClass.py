# imports
import os, pickle, sys, random, time

from flask import Flask
from flask import request, redirect
from markupsafe import escape
from flask_socketio import SocketIO, emit, send


# define start variables
stresses = {}

interval = "1000" # ms

chars = [*'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_'] # chars used in room codes

# mode = ['PRODUCTION', 'TESTING', 'DEVELOPMENT']
# mode = [0]
# config = load_config(mode)

app = Flask(__name__) # create flask app

# app.config.from_object(config)

socketio = SocketIO(app)

# create list of stresses
for stress in open('stresses.txt', 'r').readlines():
	stresses[stress.split('  ')[0]] = stress.split('  ')[-1]

# is debug?
debug = False

# need this many rhymes to be allowed (for random)
limit = 15

# define clear (terminal)
clear = "cls" if "win" in sys.platform else "clear"

# define rhyming function
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

# define commands
commands = ['dispute', 'bail', 'pause', 'score', 'list', 'hint']

# main class
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
			self.startword = random.choice(choices)

			# set previous to none
			self.previous = None

			# set player to imported settings or empty list if settings not supplied
			self.player = Settings["player"] if Settings else []

			# set current player's turn to 0 (first player)
			self.player_turn = 0

			# create empty lists and dictionaries for words score finals and disallowed words
			self.words = []
			self.score = []
			self.finals = {}
			self.disallowed = []

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
					self.unsaid.append(word)

			# add startword to "said" words (prevent people getting cheat points)
			if self.startword not in self.words:
				self.words.append(self.startword.lower())

	# load settings
	def loadSettings(self, Settings):
		# try if fail then return false
		try:
			# set playerlimit to var from settings
			self.playerlimit = Settings['playerlimit']

			# if success return true
			return True
		except:
			return False

	# add player
	def addPlayer(self, playerName):
		# try if fail then return false
		try:
			# if game in progress then return false
			if self.in_progress:
				return False

			# if number of players in excess or equal to playerlimit return false
			if len(self.player) >= self.playerlimit:
				return False
			else:
				# otherwise add the player and their corresponding score
				self.player.append(playerName)
				self.score.append(0)

				# if success return true
				return True
		except:
			return False

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

		# return playername and result
		return [self.player[self.player_turn], result]

# set global vars
global rooms, wait_id, RhymeClass

# set rhymeclass for web
RhymeClass = Rhyme()

# create wait id (negative because it increments by 1 before going to next frame)
wait_id = -1

# create empty room dictionary
rooms = {}

# create root page (index)
@app.route("/", methods=['GET','POST'])
def index():
	# if get method
	if request.method == 'GET':
		# check if it failed
		fail = request.args.get("fail","")

		# create elements list (each element is 1 line of html)
		elements = [
			"<h1>Rhyming Challenge</h1>",
			"<br>",
			"<form action='' method='post'>",
			"<input type='submit' name='Game' value='Create Game'>",
			"<input type='submit' name='Game' value='Join Game'>",
			"</form>",
		]

		# if failed add text stating illegitimate action
		if fail == "True":
			elements.append("<p>Not a legitimate action.</p>")

		# return html
		return '\n'.join(elements)

	# if post method
	if request.method == 'POST':

		# if create game
		if request.form['Game'] == 'Create Game':
			# go to create
			return redirect("/Create")

		# if join game
		elif request.form['Game'] == 'Join Game':
			# go to join
			return redirect("/Join")
		else:
			# if it doesn't match then fail
			return redirect("/?fail=True")

# Create page
@app.route("/Create", methods=['GET','POST'])
def roomAssign():
	# set required variable (to say required)
	required = " required"

	# if get method
	if request.method=='GET':
		# send website contents

		# custom start is false
		customStart = False

		# potential inputs
		t = ["<input type='submit' name='customStart' value='Custom Start'><br>", "<label for='customStart'>Start word: </label><br>\n<input type='text' id='customStart' name='start'><input type='submit' name='cancel' value='Cancel'>"]

		elements = [
			"<h1>Create a room</h1>",
			"<br>",
			"<form action='' method='post'>",
			t[1] if customStart else t[0],   # if custom start get text input otherwise get button to enable text input
			"<label for='name'>Player Name: </label><br>",
			"<input type='text' id='name' name='pName'"+(required if customStart else "")+">",  # if custom start set required
			"<input type='submit' name='submit' value='Create'>"
		]

		# return html
		return '\n'.join(elements)

	# if post method
	if request.method=='POST':
		# create room and redirect

		# print request form to console
		print(repr(request.form))

		# if customstart set custom start to true
		if request.form.get('customStart'):
			customStart = True
		else:
			# otherwise false
			customStart = False

		# if cancel set custom start to false
		if request.form.get('cancel'):
			customStart = False
		else:
			# otherwise true
			customStart = True

		# if submit check if valid then submit
		if request.form.get('submit'):
			# has player name?
			pName = request.form.get('pName')

			# has startword?
			startword = request.form.get('start')

			# if has player name
			if pName:
				# generate room code
				roomcode = ''.join([random.choice(chars) for x in range(8)])

				# redirect to /game/roomcode/player_name (keep post [code 307])
				return redirect(f"/game/{roomcode}/{pName}", code=307)
			else:
				# if no player name custom start = false
				customStart = False

		# potential form components
		t = ["<input type='submit' name='customStart' value='Custom Start'>", "<label for='customStart'>Start word: </label><br>\n<input type='text' id='customStart' name='start'><input type='submit' name='cancel' value='Cancel'>"]

		# html elements (each element = 1 line of html)
		elements = [
			"<h1>Create a room</h1>",
			"<br>",
			"<form action='' method='post'>",
			t[1] if customStart else t[0],
			"<label for='name'>Player Name: </label><br>",
			"<input type='text' id='name' name='pName'"+(required if customStart else "")+">",
			"<input type='submit' name='submit' value='Create'>"
		]

		# return html
		return '\n'.join(elements)

# wait function (waiting animation)
def wait(frame):
	# set frames
	frames = ["waiting","waiting.","waiting..","waiting..."]

	# if frame is more than length of frames
	if frame >= len(frames):
		# return none
		return None
	# otherwise return current frame
	return frames[frame]

# update function (at path /update/<roomcode>)
@app.get("/update/<roomcode>")
def update(roomcode):
	# get global vars (rooms, wait_id)
	global rooms, wait_id

	# set local result variable to current room's result
	result = rooms[roomcode]['result']

	# if there is a result
	if result:
		# if the result is a command result
		if result[1].startswith('command'):
			# return results
			return '\n'.join([f"{result[0]} used a command!",f"Result: {result[1]}"])
		if result[1].startswith('$'):
			return '\n'.join([f"{result[0]} has {result[1].replace('$','')}"])
		# return guess result
		return '\n'.join([f"{result[0]} Answered!",f"Result: {result[1]}"])
	# if there is no result
	else:
		# increment wait id
		wait_id += 1
		# get next frame
		frame = wait(wait_id)
		# if frame is not None or False
		if frame:
			# return frame
			return frame
		else:
			# otherwise set wait id to 0 (because it's out of range)
			wait_id = 0
			# get frame
			frame = wait(wait_id)
			# return frame
			return frame

# key exists function
def key_exists(element, roomcode, keys):
	# if keys is not list
	if not isinstance(keys, list):
		# keys is list with one element (keys)
		keys = [keys]
	# for each key in keys
	for key in keys:
		# try to get the element
		try:
			# get element and immediately discard (purely for error generation)
			_ = element[roomcode][key]
		except KeyError:
			# if error return False (key does not exist)
			return False
	# otherwise return true (key does exist)
	return True

@socketio.on('message')
def handle_message(data):
	print('MESsage: received message: '+data)

@socketio.on('connect')
def handle_connect(json):
	print('Connected: received json: '+str(json))

@socketio.on('json')
def handle_json(json):
	print('JSON: received json: '+str(json))

@socketio.on('join')
def handle_join(json):
	global rooms
	roomcode = json['roomcode']
	name = json['name']
	try:
		if len(rooms[roomcode]['players']) >= rooms[roomcode]['num_players']:
			print(name+" tried to join "+roomcode+" but room was full")
			emit('Deny', json)
		else:
			rooms[roomcode]['players'].append(name)
			print(name+" has joined "+roomcode)
			emit('Accept', json)
	except Exception as e:
		print(name+" tried to join "+roomcode+" but "+str(type(e))+" occured\n"+str(repr(e)))
		emit('InternalError', json)

@socketio.on('guess')
def handle_guess(json):
	global rooms
	roomcode = json['roomcode']
	name = json['name']
	guess = json['guess']
	print(name+" guessed "+guess+" in "+roomcode)
	results = request.form.get('answer')
	print(results)

	if results:
		rooms[roomcode]['result'] = [name, results]

	else:
		pass


# game function (/game/roomcode/name) [allows get and post methods]
@app.route("/game/<roomcode>/<name>", methods=['GET','POST'])
def game(roomcode, name):
	# retrieve global variables rooms and rhymeclass
	global rooms, RhymeClass

	# set result to empty string
	result = ''

	# set title to room 'roomcode'
	Title = '<h1>Room \''+roomcode+'\'</h1>'

	# form to create class (number of players)
	CreateForm = [
		"<form action='' method='post'>",
		"<label for='num'>Number of players: </label><br>",
		"<input type='number' id='num' name='num_players' required>",
		"<input type='submit' name='submit' value='Continue'>"
	]

	# print rooms to console (representation)
	print(repr(rooms))

	# if room code not in rooms or room not setup
	if roomcode not in rooms.keys() or not key_exists(rooms, roomcode, 'num_players'):
		# add title to result
		result += Title

		# try to get number of players from form
		np = request.form.get('num_players')

		# get start word from previous page form (create page)
		sword = request.form.get('start')
		
		# if roomcode not in rooms
		if roomcode not in rooms.keys():
			# create dictionary under roomcode as key
			rooms[roomcode] = {}
			rooms[roomcode]['players'] = []

		# set start word
		rooms[roomcode]['sword'] = sword

		# 
		print(repr(np), type(np))
		if isinstance(np, str):
			if 'e' in np:
				try:
					np = float(np.split('e')[0])*10**(int(np.split('e')[-1]))
					rooms[roomcode]['num_players'] = int(np)
					rooms[roomcode]['game_state'] = {}
					rooms[roomcode]['result'] = None
					rooms[roomcode]['status'] = 'public'
					#rooms[roomcode]['players'].append(name)
					return redirect("/game/"+roomcode+"/"+name)
				except Exception as e:
					print(repr(e))
			try:
				if np.isdigit():
					rooms[roomcode]['num_players'] = int(np)
					rooms[roomcode]['game_state'] = {}
					rooms[roomcode]['result'] = None
					rooms[roomcode]['status'] = 'public'
					#rooms[roomcode]['players'].append(name)
					return redirect("/game/"+roomcode+"/"+name)
			except Exception as e:
				print(repr(e))
		else:
			result += '\n'.join(CreateForm)
	else:

		answerForm = [
			"<form action='' method='POST'>",
			f"<label for='answer'>What word rhymes with {rooms[roomcode]['sword']}?</label><br>",
			"<input type='text' id='answer' name='answer' required> <button onclick='guess()'>Guess</button>",
			"</form>"
		]

		script = [
			"<p id='output'></p>",
			"<script src='https://code.jquery.com/jquery-3.6.0.min.js' integrity='sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=' crossorigin='anonymous'></script>",  ## FINAL LINE (define fetch script)
			"<script>",
			"function update(){",
			"$.get('/update/"+roomcode+"', function(data){",
			"$('#output').html(data)",
			"});",
			"}",
			"update()",
			"var intervalId = setInterval(function() {",
			"update()",
			"}, "+interval+");",
			"</script>"
		]

		socketioJS = '<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js" integrity="sha512-q/dWJ3kcmjBLU4Qc47E4A9kTB4m3wuTY7vkFJDTZKjTs8jhyGQnaUrxa0Ytd0ssMZhbNua9hE+E7Qv1j+DyZwA==" crossorigin="anonymous"></script>'

		connectScript = [
			socketioJS,
			"<script type='text/javascript' charset='utf-8'>",
			"var socket = io();",
			"socket.on('connect', function() {",
			f"socket.emit('join', {{name: '{name}', roomcode: '{roomcode}'}});",
			"});",
			"function guess() {",
			f"socket.emit('guess', {{guess: document.getElementById('answer').value, name: '{name}', roomcode: '{roomcode}'}});",
			"}"
			"</script>"
		]

		elements = [
			"<h1>Game: "+roomcode+"</h1>",
			'\n'.join(script),
			'\n'.join(connectScript),
			'\n'.join(answerForm)
		]

		result += '\n'.join(elements)
	return result

@app.route("/Join", methods=['GET','POST'])
def joinGame():
	global rooms

	searchResults = None

	search = request.form.get('search')
	# submit = request.form.get('submit')
	code = request.form.get('code')
	name = request.form.get('name')

	if search:
		searchResults = []

		for rCode in rooms:
			if rooms[rCode]['status'] == 'public':
				searchResults.append(rCode)
			continue

		searchResults = '\n'.join(searchResults)

	else:
		if code:
			if code not in list(rooms.keys()):
				searchResults = "Code Invalid"
			else:
				if name:
					if name not in rooms[code]['players']:
						return redirect(f'/game/{code}/{name}')
					else:
						searchResults = "Name already in use"
				else:
					searchResults = "Please supply a name"

	joinForm = [
		"<form action='' method='post'>",
		"<label for='code'>Room Code:</label><br>",
		"<input type='text' id='code' name='code'><br>",
		"<label for='name'>Name:</label><br>",
		"<input type='text' id='name' name='name'>",
		"<input type='submit' name='submit' value='Join'> <input type=submit name='search' value='Search'>",
		"</form>",
	]

	joinForm = '\n'.join(joinForm)

	elements = [
		"<h1>Join Game</h1>",
		"<p>Join a Game, get the room code from a friend or press search</p>",
		joinForm,
		(f"<br><p>{searchResults}</p>" if searchResults else "")
	]

	return '\n'.join(elements)

if __name__ == '__main__':
	sublime = True
	if sublime:
		c = 'w'
	else:
		c = input("[W]eb or [T]erminal?\n- ")
	if c.lower() == 'w':
		print("Work in Progress")

		try:
			socketio.run(app, host="0.0.0.0", port=8080)
		except Exception as e:
			print(repr(e))
			quit()

	if c.lower() == 't':
		Settings = {}
		player = []

		num_plyrs = ''

		while not isinstance(num_plyrs, int):
			num_plyrs = input("number of players:\n- ")
			if num_plyrs.isdigit():
				num_plyrs = int(num_plyrs)

		for player_index in range(num_plyrs):
			player.append(input(f"Player {player_index+1}'s name:"+"\n- "))

		Settings["player"] = player

		r = Rhyme(Settings=Settings)
		running = True
		while True:
			guess = input("guess something:\n- ")
			if guess.startswith("#"):
				if guess == "#QUIT":
					break
			result = r.guess(guess)
			print(f"{result[0]} said {guess}")
			print(f"result: {result[1]}")
			print()
	if c.lower() != 'w' and c.lower() != 't':
		print("invalid, exiting")