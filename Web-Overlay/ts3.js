CLIENTINFO = {
	CLIENT_ID: 0,
	CLIENT_NAME: 1,
	CLIENT_AVATAR: 2
}

TALKING_STATUS = {
	NOT_TALKING: 0,
	TALKING: 1,
	TALKING_WHILE_DISABLED: 2
}

CLIENT_MOVE = {
	JOINED : 0,
	LEFT: 1
}

function parseAvatarPath(argument) {
	if (argument == ""){
		avatars = ['https://discordapp.com/assets/322c936a8c8be1b803cd94861bdfa868.png','https://discordapp.com/assets/6debd47ed13483642cf09e832ed0bc1b.png','https://discordapp.com/assets/0e291f67c9274a1abdddeb3fd919cbaa.png','https://discordapp.com/assets/dd4dbc0016779df1378e7812eabaa04d.png','https://discordapp.com/assets/1cbd08c76f8af6dddce02c5138971129.png']
		return avatars[Math.floor(Math.random()*avatars.length)];
	} else {
		//return 'file:///' + argument[AVATAR_CODE.PATH].replace(/\\/g,'/');
		return 'http://localhost:58008/'+argument;
	}
}

function createClientDiv(argument) {
	var item = document.createElement('DIV');
	item.className = 'useritem';
	item.id = 'client_' + argument[CLIENTINFO.CLIENT_ID];
	item.innerHTML = createClientAvatar(argument).outerHTML;
	item.innerHTML += createClientName(argument[CLIENTINFO.CLIENT_NAME]).outerHTML;
	return item
}

function createClientName(argument) {
	var item = document.createElement('SPAN');
	item.innerText = argument;
	return item;
}

function createClientAvatar(argument){
	var item = document.createElement('IMG');
	item.id = 'avatar_' + argument[CLIENTINFO.CLIENT_ID];
	item.src= parseAvatarPath(argument[CLIENTINFO.CLIENT_AVATAR]);
	return item;
}

function updateChannelClients(argument){
	document.getElementsByClassName('channelName')[0].innerText = argument.channelName;
	var userlist = document.getElementById('userlist');
	userlist.innerHTML = "";
	for (var client in argument.clients){
		userlist.appendChild(createClientDiv(argument.clients[client]));
	}
}

function toggleTalkingBorder(argument){
	var avatar = document.getElementById('avatar_' + argument.clientID);
	switch (argument.status){
		case TALKING_STATUS.TALKING:
			avatar.className = 'talking';
			break;
		case TALKING_STATUS.NOT_TALKING:
			avatar.className = '';
			break;
	}
}

function nearbyClientMoveEvent(data){
	
	switch(data.status){
		case CLIENT_MOVE.JOINED:
			document.getElementById('userlist').appendChild(createClientDiv(data.client));
			break;
		case CLIENT_MOVE.LEFT:
			var user = document.getElementById('client_' + data.client[CLIENTINFO.CLIENT_ID]).remove();
			break;
	}
}

function ActiveServerSwap(data){
	updateChannelClients(data);
}

function onClientMoveEvent(data){
	updateChannelClients(data);
}

function onClientDisplayNameChanged(argument){
	document.getElementById('client_' + argument.client[CLIENTINFO.CLIENT_ID]).childNodes[1].innerText = argument.client[CLIENTINFO.CLIENT_NAME];
}

function handleMessage(data){
	console.log(data);
	if (data.debug == undefined){
		switch (data.event){
			case 'updateChannelClients':
				updateChannelClients(data);
				break;
			case 'onTalkStatusChangeEvent':
				toggleTalkingBorder(data);
				break;
			case 'nearbyClientMoveEvent':
				nearbyClientMoveEvent(data);
				break;
			case 'ActiveServerSwap':
				ActiveServerSwap(data);
				break;
			case 'onClientMoveEvent':
				onClientMoveEvent(data);
				break;
			case 'onClientDisplayNameChanged':
				onClientDisplayNameChanged(data);
			default:
				return;
		}
	}
}