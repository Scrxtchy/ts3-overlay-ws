
from ts3plugin import ts3plugin
import ts3lib, ts3defines, json, subprocess
try:
	from websocket import create_connection
except ImportError:
	ts3lib.printMessageToCurrentTab("Installing websocket-client")
	from devtools import PluginInstaller
	try:
		PluginInstaller.installPackages(PluginInstaller, ['websocket-client'])
	except TypeError as e:
		pass
	from websocket import create_connection
from os import path
from os import name as osName

class tshelp:
	@staticmethod
	def getChannelName(serverConnectionHandlerID, channelID):
		return ts3lib.getChannelVariableAsString(serverConnectionHandlerID, channelID, ts3defines.ChannelProperties.CHANNEL_NAME)[1]
	
	@staticmethod
	def getChannelID(serverConnectionHandlerID):
		return ts3lib.getChannelOfClient(serverConnectionHandlerID, ts3lib.getClientID(serverConnectionHandlerID)[1])[1]
	
	@staticmethod
	def getNearbyClients(serverConnectionHandlerID):
		users = ts3lib.getChannelClientList(serverConnectionHandlerID, tshelp.getChannelID(serverConnectionHandlerID))[1]
		userDetailed = []
		for user in users:
			userDetailed.append([user, ts3lib.getClientDisplayName(serverConnectionHandlerID, user)[1], tshelp.getAvatar(serverConnectionHandlerID, user)])
		return userDetailed
	
	@staticmethod
	def getClientInfo(serverConnectionHandlerID, clientID):
		return [clientID, ts3lib.getClientDisplayName(serverConnectionHandlerID, clientID)[1], tshelp.getAvatar(serverConnectionHandlerID, clientID)]
	
	@staticmethod
	def getServerName(serverConnectionHandlerID):
		return ts3lib.getServerVariableAsString(serverConnectionHandlerID, ts3defines.VirtualServerProperties.VIRTUALSERVER_NAME)[1]

	@staticmethod
	def getAvatar(serverConnectionHandlerID, clientID):
		avatar = ts3lib.getAvatar(serverConnectionHandlerID, clientID)
		if avatar[0] != 0:
			return ""
		else:
			return path.relpath(avatar[1], ts3lib.getConfigPath())
	
	class ClientInfo(object):
		"""docstring for ClientInfo"""
		CLIENT_ID = 0
		CLIENT_NAME = 1
		CLIENT_AVATAR = 2

class socketplugin(ts3plugin):
	"""docstring for overlayplugin"""
	name = "socket"
	requestAutoload = False
	version = "0.1"
	apiVersion = 21
	author = "Scratch"
	description = "Overlay helper"
	offersConfigure = False
	commandKeyword = ""
	infoTitle = ""
	tshelp = tshelp()
	menuItems = [
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Start/Stop Overlay", "scripts/%s/icon.png"%__name__),
		(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "Refresh Overlay", "scripts/%s/icon.png"%__name__)
	]
	hotkeys = []

	def __init__(self):
		self.ws = None
		self.wsserver = None
		self.currentActiveServer = ts3lib.getCurrentServerConnectionHandlerID()


	def send(self, message):
		if self.ws != None:
			try:
				self.ws.send(json.dumps(message))
			except Exception as e:
				self.stop()

	def onMenuItemEvent(self, serverConnectionHandlerID, atype, menuItemID, selectedItemID):
		if menuItemID == 0:
			if self.ws == None:
				startupinfo = None
				if osName == 'nt':
					startupinfo = subprocess.STARTUPINFO()
					startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
				self.wsserver = subprocess.Popen(path.realpath(path.dirname(__file__) + '/ws.exe'), startupinfo=startupinfo, cwd=path.realpath(path.dirname(__file__)))
				#path.realpath(__file__)

				#Open Socket
				ts3lib.printMessageToCurrentTab("Openning Overlay Socket Connection")
				self.ws = create_connection("ws://localhost:58008/ws")
				self.send({'debug': 'teamspeak connect'})
				self.send({'event': 'updateChannelClients', 'clients': tshelp.getNearbyClients(self.currentActiveServer), 'channelName': tshelp.getChannelName(self.currentActiveServer,tshelp.getChannelID(self.currentActiveServer))})
			else:
				self.stop()

		elif menuItemID == 1:
			self.send({'event': 'updateChannelClients', 'clients': tshelp.getNearbyClients(self.currentActiveServer), 'channelName': tshelp.getChannelName(self.currentActiveServer,tshelp.getChannelID(self.currentActiveServer))})			

	def stop(self):
		#Close Socket
		if self.ws != None:
			self.send({'debug': 'teamspeak disconnect'})
			self.ws.close()
			ts3lib.printMessageToCurrentTab("Closing Overlay Socket Connection")
			self.ws = None
		if self.wsserver != None:
			self.wsserver.kill()
			self.wsserver = None

	def onTalkStatusChangeEvent(self, serverConnectionHandlerID, status, isReceivedWhisper, clientID):
		name = ts3lib.getClientDisplayName(serverConnectionHandlerID, clientID)[1]
		if serverConnectionHandlerID == self.currentActiveServer:
			self.send({'event': 'onTalkStatusChangeEvent', 'clientID': clientID, 'status': status})

#			{'event': 'onTalkStatusChangeEvent', 'cilentID': clientID, 'status': status}

			# if status == ts3defines.TalkStatus.STATUS_TALKING:
			#	ts3lib.printMessageToCurrentTab("%s started talking" % name)
			#elif status == ts3defines.TalkStatus.STATUS_NOT_TALKING:
			#	ts3lib.printMessageToCurrentTab("%s stopped talking" % name)
			

	def onClientSelfVariableUpdateEvent(self, serverConnectionHandlerID, flag, oldValue, newValue):
		if flag == ts3defines.ClientProperties.CLIENT_INPUT_HARDWARE:
			self.currentActiveServer = serverConnectionHandlerID
#			{'event': 'onClientSelfVariableUpdateEvent', 'flag': flag, 'data': [oldValue, newValue]}
			self.send({'event': 'ActiveServerSwap', 'serverConnectionHandlerID': serverConnectionHandlerID,'channelName': tshelp.getChannelName(serverConnectionHandlerID,tshelp.getChannelID(serverConnectionHandlerID)), 'serverName': tshelp.getServerName(serverConnectionHandlerID), 'clients': tshelp.getNearbyClients(self.currentActiveServer)})
			
			#ts3lib.printMessageToCurrentTab("Switched Server Mic to %s" % tshelp.getServerName(serverConnectionHandlerID))
			

	def onClientMoveEvent(self, serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility, moveMessage):
		#Log Channel Change
		#ts3lib.printMessageToCurrentTab("Switched room from %s to %s" % (tshelp.getChannelName(serverConnectionHandlerID,oldChannelID), tshelp.getChannelName(serverConnectionHandlerID,newChannelID)))
		if self.currentActiveServer == serverConnectionHandlerID and clientID == ts3lib.getClientID(serverConnectionHandlerID)[1]: #If User Moves
			self.send({'event': 'onClientMoveEvent', 'channelID' : newChannelID, 'channelName': tshelp.getChannelName(serverConnectionHandlerID,newChannelID), 'clients': tshelp.getNearbyClients(self.currentActiveServer)})
#			self.send({'event': 'updateChannelClients', 'clients': tshelp.getNearbyClients(self.currentActiveServer)}))
	#		updateChannelClients()
		elif self.currentActiveServer == serverConnectionHandlerID and clientID != ts3lib.getClientID(serverConnectionHandlerID)[1] and (tshelp.getChannelID(serverConnectionHandlerID) == oldChannelID or tshelp.getChannelID(serverConnectionHandlerID) == newChannelID):
			EVENT = 0
			if tshelp.getChannelID(serverConnectionHandlerID) == newChannelID:
				EVENT = 0
			else:
				EVENT = 1
			self.send({'event': 'nearbyClientMoveEvent', 'client': tshelp.getClientInfo(serverConnectionHandlerID, clientID), 'status': EVENT})

	def onClientMoveTimeoutEvent(self, serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility, timeoutMessage):
		if self.currentActiveServer == serverConnectionHandlerID and oldChannelID == tshelp.getChannelID(serverConnectionHandlerID):
			self.send({'event': 'nearbyClientMoveEvent', 'client': tshelp.getClientInfo(serverConnectionHandlerID, clientID), 'status': 1})

	
	def onConnectStatusChangeEvent(self, serverConnectionHandlerID, newStatus, errorNumber):
		#if newStatus == ts3defines.ConnectStatus.STATUS_DISCONNECTED:
		if newStatus == ts3defines.ConnectStatus.STATUS_CONNECTED:
			self.currentActiveServer = serverConnectionHandlerID
			self.send({'event': 'ActiveServerSwap', 'serverConnectionHandlerID': serverConnectionHandlerID,'channelName': tshelp.getChannelName(serverConnectionHandlerID,tshelp.getChannelID(serverConnectionHandlerID)), 'serverName': tshelp.getServerName(serverConnectionHandlerID), 'clients': tshelp.getNearbyClients(self.currentActiveServer)})

	def onClientDisplayNameChanged(self, serverConnectionHandlerID, clientID, displayName, uniqueClientIdentifier):
		if self.currentActiveServer == serverConnectionHandlerID:
			self.send({'event': 'onClientDisplayNameChanged', 'client':[clientID, displayName]})

	def onClientKickFromServerEvent(self, serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility, kickerID, kickerName, kickerUniqueIdentifier, kickMessage):
		if self.currentActiveServer == serverConnectionHandlerID and oldChannelID == tshelp.getChannelID(serverConnectionHandlerID):
			self.send({'event': 'nearbyClientMoveEvent', 'client': tshelp.getClientInfo(serverConnectionHandlerID, clientID), 'status': 1})

	def onClientMoveMovedEvent(self, serverConnectionHandlerID, clientID, oldChannelID, newChannelID, visibility, moverID, moverName, moverUniqueIdentifier, moveMessage):
		if self.currentActiveServer == serverConnectionHandlerID and oldChannelID == tshelp.getChannelID(serverConnectionHandlerID):
			self.send({'event': 'nearbyClientMoveEvent', 'client': tshelp.getClientInfo(serverConnectionHandlerID, clientID), 'status': 1})

