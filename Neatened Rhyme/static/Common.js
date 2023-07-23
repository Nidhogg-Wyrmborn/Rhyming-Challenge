socket = io();
var connected = false;
socket.on('connect', function() {
	connected = true;
});

socket.on('disconnect', function() {
	connected = false;
});

function submit(){
	var pCount = document.getElementById('pCount').value;
	var pName = document.getElementById('pName').value;
	var sWord = document.getElementById('sWord').value;
	if ((pCount != null && pCount != '') && (pName != null && pName != '') && connected) {
		console.log('Success')
		console.log('pCount: '+pCount+', pName: '+pName+', Connected: '+connected)
		socket.emit('create', {pCount: pCount, pName: pName, sWord: sWord})
	} else {
		console.log('Fail')
		console.log('pCount: '+pCount+', pName: '+pName+', Connected: '+connected)
		socket.emit('fail', {pCount: pCount, pName: pName, sWord: sWord})
	}
}

socket.on('redirect', function(destination) {
	window.location.href = destination;
});

function showCustom() {
	document.getElementById('showButton').hidden = true;
	document.getElementById('sWord').hidden = false;
	document.getElementById('hideButton').hidden = false;
	document.getElementById('sLabel').hidden = false;
}

function hideCustom() {
	document.getElementById('showButton').hidden = false;
	document.getElementById('sWord').hidden = true;
	document.getElementById('hideButton').hidden = true;
	document.getElementById('sLabel').hidden = true;
}