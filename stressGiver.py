import os, sys, random

running = True
debug = False
fullDebug = False

clear = "cls" if "win" in sys.platform else "clear"

while running:
	num_chars = input("number of chars:\n- ")
	match = input("number to match:\n- ")

	if num_chars.isdigit():
		num_chars = int(num_chars)
		if match.isdigit():
			match = int(match)
		else:
			running = False
			continue

	else:
		running = False
		continue

	stresses = {}
	ph_stresses = {}

	with open('phodict.txt', 'r') as f:
		for word in f.readlines():
			phonetics = word.split('  ')[-1]
			phonetics = phonetics.replace("\n","").split(" ")
			word = word.split('  ')[0].split('(')[0]
			# print(phonetics, word)
			if len(word) < num_chars:
				continue
			try:
				stresses[''.join(list(word)[-num_chars:])][0] += 1
				stresses[''.join(list(word)[-num_chars:])][1].append(word)
			except Exception as e:
				if fullDebug:
					print('Spelling Stresses;', type(e), e)
				stresses[''.join(list(word)[-num_chars:])] = []
				stresses[''.join(list(word)[-num_chars:])].append(1)
				stresses[''.join(list(word)[-num_chars:])].append([])
				stresses[''.join(list(word)[-num_chars:])][1].append(word)

			try:
				ph_stresses[' '.join(phonetics[-num_chars:])][0] += 1
				ph_stresses[' '.join(phonetics[-num_chars:])][1].append(word)
			except Exception as e:
				if fullDebug:
					print('Phonetic Stresses;', type(e), e)
				ph_stresses[' '.join(phonetics[-num_chars:])] = []
				ph_stresses[' '.join(phonetics[-num_chars:])].append(1)
				ph_stresses[' '.join(phonetics[-num_chars:])].append([])
				ph_stresses[' '.join(phonetics[-num_chars:])][1].append(word)

	# stresses = list(set(stresses))

	os.system(clear)

	if debug or fullDebug:
		print(len(stresses))
		print(len(ph_stresses))
		print(random.choice(list(ph_stresses.keys())))

	matches = []

	c = True if input("[P]honetic rhymes or [S]pelling rhymes?\n- ").lower() == "S" else False

	if c:
		if debug:
			print('Spelling')
		for stress in list(stresses.keys()):
			if stresses[stress][0] > match:
				matches.append([stresses[stress][0], stress, random.choice(stresses[stress][1])])

	else:
		if debug:
			print('Phonetic')
		for stress in list(ph_stresses.keys()):
			if ph_stresses[stress][0] > match:
				if debug:
					print(f"{stress} match")
				matches.append([ph_stresses[stress][0], stress, random.choice(ph_stresses[stress][1])])
			else:
				if debug:
					print(f"{stress} no match")

	matches.sort()

	for m in matches:
		print(m[1], m[0], m[2])