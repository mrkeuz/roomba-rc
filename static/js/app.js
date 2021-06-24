'use strict';
var ws;

function connect() {
  ws = new WebSocket("ws://" + document.location.host + "/");

  ws.onmessage = function(e) {
    var event_data = JSON.parse(e.data);
    console.log(event_data)

    if (event_data.type == "moving_status") {
      document.getElementById("speed").innerHTML = event_data.speed;
      document.getElementById("turn_rad").innerHTML = event_data.turn_rad;
    }
  };

  ws.onclose = function(e) {
    console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
    setTimeout(function() {
      connect();
    }, 1000);
  };
}

document.addEventListener('keyup', (event) => {
  const keyName = event.key;
  ws.send(JSON.stringify({
    "event": "keyup",
    "keyName": keyName
  }));
});

document.addEventListener('keydown', (event) => {
  const keyName = event.key;
  ws.send(JSON.stringify({
    "event": "keydown",
    "keyName": keyName
  }));
});

connect();
