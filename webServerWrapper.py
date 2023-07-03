import rhyme, random

from flask import Flask
from flask import request, escape, redirect, url_for

app = Flask(__name__)  # create app with import name of "webServerWrapper" since that is the name of file

@app.route("/")  # set the function index to be called when user requests root path of url
def index():
	return "<h1>Index</h1>\n<br>\n<a href=\"/Rhyme\">Rhyming Game</a>"

@app.route("/Rhyme/")
def roomAssign():
	name = str(escape(request.args.get("name","")))
	code = str(escape(request.args.get("code","")))

	if name and code:
		chars = [*'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_']
		if code.startswith("#"):
			sword = code.replace("#","")
			code = ''
			for i in range(8):
				code += random.choice(chars)

		return redirect("/Rhyme/game/"+name+"/"+sword+"/"+code)

	elements = [
		"<h1>Rhyming Challenge</h1>",
		"<br>",
		"<p>Create or join a game?<br>If you are creating a game, input the starting word preceded by a #<br>If you are joining a game input the game code by itself<br><br>Finally input the name you will use during the game</p>",
		"<form action='' method='get'>",
		"<p>Code or #startword</p><input type='text' name='code'>",
		"<br>",
		"<p>Player Name</p><input type='text' name='name'>"
		"<input type='submit' Value='Guess'>",
		"</form>",
		"<br>",
		"<a href='/'>Main Page</a>"
	]

	# elements[2] = elements[2][0] if not name else elements[2][1]

	return '\n'.join(elements)

@app.route("/Rhyme/game/<name>/<sword>/<room>")
def Rhyme(room, name, sword):
	print(room)
	print(name)
	print(sword)
	guess = str(escape(request.args.get("guess", "")))
	title = ["Rhyming Challenge", "h1"]  # set title and header type
	LinkA = ["Leave current game", "a", "/Rhyme"]  # set link text, and href

	elements = []#"<{t}>{ti}</{t}>".format(t=title[1],ti=title[0]), "<{t} href='{a}'>{ti}</{t}>".format(t=LinkA[1],a=LinkA[2],ti=LinkA[0])]

	elements = rhyme.assembler(Title=title,MLink=LinkA, guess=guess)  # assemble elements (including body)
	
	html = '\n'.join(elements)
	return html#+"\n\n"+str(repr(guess))

if __name__ == "__main__":
	# run the application hosting at all addresses and port 5000
	debug = False #True if input("debug?\n- ").lower() == 'y' else False
	app.run(host='0.0.0.0',port=5000,debug=debug)
