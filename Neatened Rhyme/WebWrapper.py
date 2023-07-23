from flask import Flask
from flask import request, redirect, render_template, url_for
from markupsafe import escape
from flask_socketio import SocketIO, emit, send

import time
import Rhyme, random

app = Flask(__name__, static_folder='static', template_folder='templates')

socketio = SocketIO(app)

socketioJS = '<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js" integrity="sha512-q/dWJ3kcmjBLU4Qc47E4A9kTB4m3wuTY7vkFJDTZKjTs8jhyGQnaUrxa0Ytd0ssMZhbNua9hE+E7Qv1j+DyZwA==" crossorigin="anonymous"></script>'
jQuery = "<script src='https://code.jquery.com/jquery-3.6.0.min.js' integrity='sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=' crossorigin='anonymous'></script>"

global rooms, present

present = {}
rooms = {}

chars = [*'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_']


def generateRoomCode():
	return ''.join([random.choice(chars) for x in range(8)])



@socketio.on('disconnect')
def handle_disconnect(json=None):
	print('Disconnect: ', repr(json))

@socketio.on('connect')
def handle_connect(json=None):
	print('Connect: ', repr(json))

@socketio.on('create')
def handle_create(json):
	global rooms
	print('Create: ', repr(json))
	if not debug:
		pCount = json['pCount']
		pName = json['pName']
		startword = json['sWord']

		roomcode = generateRoomCode()

		rooms[roomcode] = {}
		rooms[roomcode]['Class'] = Rhyme.Rhyme()

		Settings = {}
		Settings['playerlimit'] = pCount
		if startword != '':
			Settings['startword'] = startword

		rooms[roomcode]['Class'].loadSettings(Settings)
		rooms[roomcode]['sWord'] = rooms[roomcode]['Class'].startword
		emit('redirect', f'/Game/{roomcode}/{pName}')

@socketio.on('fail')
def handle_fail(json):
	print('Fail: ', repr(json))

@app.route("/", methods=['GET','POST'])
def index():
	if request.method == 'GET':
		return render_template('index.html')

	if request.method == 'POST':
		if request.form['Game'] == 'Create Game':
			return redirect("/Create")

		elif request.form['Game'] == 'Join Game':
			return redirect("/Join")
		else:
			return redirect("/")

@app.route("/Create", methods=['GET', 'POST'])
def Create():
	if request.method=='GET':
		return render_template('Create.html')

@socketio.on('join')
def handle_join(json=None):
	global rooms
	print('join: ', repr(json))
	name = json['name']
	roomcode = json['roomcode']

	if roomcode in rooms.keys():
		a = rooms[roomcode]['Class'].addPlayer(name)
		print(a)
		print(repr(rooms[roomcode]['Class'].player))
		print(repr(rooms[roomcode]['Class'].player_turn))
	else:
		print('room doesn\'t exist')
		emit('redirect', '/')

@socketio.on('leave')
def handle_leave(json=None):
	global rooms
	print('leave: ', repr(json))
	name = json['name']
	roomcode = json['roomcode']
	if roomcode in rooms.keys():
		a = rooms[roomcode]['Class'].removePlayer(name)
		print(a)
		print(repr(rooms[roomcode]['Class'].player))
		print(repr(rooms[roomcode]['Class'].player_turn))
	else:
		pass
		#emit('redirect', '/')

@socketio.on('guess')
def handle_guess(json=None):
	global rooms
	print('guess: ', repr(json))
	guess = json['guess']
	name = json['name']
	roomcode = json['roomcode']
	print(repr(rooms[roomcode]['Class'].player))
	print(repr(rooms[roomcode]['Class'].player_turn))
	response = rooms[roomcode]['Class'].guess(guess, name)

	response = ': '.join(response).replace('\n', '')
	print(response)

	emit('response', {'response': response, 'roomcode': roomcode})

@socketio.on('present')
def handle_present(json=None):
	global present, rooms
	print('present: ', repr(json), end='\t')
	roomcode = json['roomcode']
	name = json['name']

	if roomcode not in present.keys() and roomcode in rooms.keys():
		print('new room', end='\t')
		present[roomcode] = {}

	if roomcode not in rooms.keys():
		print('room doesn\'t exist')
		if roomcode in present.keys():
			del present[roomcode]
		print(repr(list(present)))
	else:
		previous = present[roomcode][name]['time'] if name in present[roomcode].keys() else None
		print(previous, end='\t')
		if name not in present[roomcode].keys():
			present[roomcode][name] = {}
		present[roomcode][name]['time'] = time.time()
		new = present[roomcode][name]['time']
		if previous:
			print(f'diff: {new-previous}')
		present[roomcode][name]['diff'] = new-previous if previous else 0

		# check if active player is present (has reported in at least 15 seconds ago)
		# if they haven't automatically bail them
		player_turn = rooms[roomcode]['Class'].player_turn
		aName = rooms[roomcode]['Class'].player[player_turn]

		if aName in present[roomcode].keys():
			diff = time.time() - present[roomcode][aName]['time']
			if diff > 15:
				rooms[roomcode]['Class'].removePlayer(aName)
				print(f'active player {aName} not present')


@app.route('/Game/<roomcode>/<name>')
def Game(roomcode, name):
	global rooms
	if not roomcode in rooms.keys():
		return redirect('/Join')
	else:
		if name in rooms[roomcode]['Class'].player:
			return redirect('/Join')
		return render_template('Game.html', gamecode=roomcode, name=name, word=rooms[roomcode]['sWord'])


@app.route('/Join')
def Join():
	return render_template('Join.html')

if __name__ == '__main__':
	print('running')
	debug = False
	socketio.run(app, host='0.0.0.0', port=5000, debug=debug)