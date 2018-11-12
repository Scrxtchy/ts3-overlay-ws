package main

import (
	"flag"
	"log"
	"net/http"
	"regexp"

	"github.com/gorilla/websocket"
)
var wsClient = []*websocket.Conn{}

var addr = flag.String("port", "58008", "port")
var  lastUpdate = []byte("")

var upgrader = &websocket.Upgrader{CheckOrigin: func(r *http.Request) bool{ return true}} 

func echo(w http.ResponseWriter, r *http.Request) {
	c, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Print("upgrade:", err)
		return
	}
	wsClient = append(wsClient, c)
	defer c.Close()
	if len(lastUpdate) > 3{
		log.Printf("start: %s", lastUpdate)
		c.WriteMessage(websocket.TextMessage, lastUpdate)
	}
	for {
		mt, message, err := c.ReadMessage()
		if err != nil {
			log.Println("read:", err)
			break
		}
		log.Printf("recv: %s", message)
		matched, _ := regexp.MatchString("updateChannelClients", string(message[:]))
		if matched{
			lastUpdate = message
			log.Println("info: lastUpdate")
		}
		if wsClient != nil{
			for i, client := range wsClient{
				err = client.WriteMessage(mt, message)
				if err != nil {
					log.Println("write:", err)
					wsClient = append(wsClient[:i], wsClient[i+1:]...)
					client.Close()
					break
				}
			}

		}
	}
}

func main() {
	flag.Parse()
	log.SetFlags(0)
	fs := http.FileServer(http.Dir("./Web-Overlay/"))
	cache := http.StripPrefix("/cache/", http.FileServer(http.Dir("./../../../../cache/")))
	http.Handle("/", fs)
	http.Handle("/cache/", cache)
	http.HandleFunc("/ws", echo)
	log.Fatal(http.ListenAndServe("localhost:" + *addr, nil))
}
