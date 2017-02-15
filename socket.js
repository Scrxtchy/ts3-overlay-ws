	websocket = new WebSocket('ws://localhost:8000/');
	websocket.onopen = function(evt) { onOpen(evt) };
	websocket.onclose = function(evt) { onClose(evt) };
	websocket.onmessage = function(evt) { onMessage(evt) };
	websocket.onerror = function(evt) { onError(evt)};

	function onOpen(evt)
	{
		console.log("Connected to WebSocket");
	}

	function onClose(evt)
	{
		console.log("disconnected from WebSocket");
	}

	function onMessage(evt)
	{
		handleMessage(JSON.parse(evt.data));
	}

	function onError(evt)
	{
		console.log('error: ' + evt.data + '\n');
		websocket.close();
	}

	function doSend(message)
	{
		console.log(message);
	}