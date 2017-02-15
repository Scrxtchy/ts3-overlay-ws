from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

clients = []

class SimpleEcho(WebSocket):

    def handleMessage(self):
        # echo message back to client
        for client in clients:
        	if client != self:
        		client.sendMessage(self.data)
        print(self.data)

    def handleConnected(self):
        print(self.address, 'connected')
        clients.append(self)

    def handleClose(self):
        print(self.address, 'closed')
        clients.remove(self)

server = SimpleWebSocketServer('', 8000, SimpleEcho)
server.serveforever()