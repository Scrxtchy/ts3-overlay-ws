import ts3lib, ts3defines

def getChannelName(serverConnectionHandlerID, channelID):
	return ts3lib.getChannelVariableAsString(serverConnectionHandlerID, channelID, ts3defines.ChannelProperties.CHANNEL_NAME)[1];

def getChannelID(serverConnectionHandlerID):
	return ts3lib.getChannelOfClient(serverConnectionHandlerID, ts3lib.getClientID(serverConnectionHandlerID)[1])[1]

def getNearbyClients(serverConnectionHandlerID):
	
	users = ts3lib.getChannelClientList(serverConnectionHandlerID, getChannelID(serverConnectionHandlerID))[1]
	userDetailed = []
	for user in users:
		userDetailed.append([user, ts3lib.getClientDisplayName(serverConnectionHandlerID, user)[1], ts3lib.getAvatar(serverConnectionHandlerID, user)])
	return userDetailed

def getClientInfo(serverConnectionHandlerID, clientID):
	return [clientID, ts3lib.getClientDisplayName(serverConnectionHandlerID, clientID)[1], ts3lib.getAvatar(serverConnectionHandlerID, clientID)]

def getServerName(serverConnectionHandlerID):
	return ts3lib.getServerVariableAsString(serverConnectionHandlerID, ts3defines.VirtualServerProperties.VIRTUALSERVER_NAME)[1]

class ClientInfo(object):
	"""docstring for ClientInfo"""
	CLIENT_ID = 0
	CLIENT_NAME = 1
	CLIENT_AVATAR = 2