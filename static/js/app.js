'use strict';

const TOUCH_RADIUS = 80;

let ws;
let screen_height;
let screen_width;
let ongoingTouches = [];
let dx_koef = 0;
let dy_koef = 0;
let touch_move_timeout;


const debounce = (func, wait) => {

  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(touch_move_timeout);
      func(...args);
    };

    clearTimeout(touch_move_timeout);
    touch_move_timeout = setTimeout(later, wait);
  };
};


function copyTouch(touch) {
  return {
    identifier: touch.identifier,
    pageX: touch.pageX,
    pageXStart: touch.pageX,
    pageY: touch.pageY,
    pageYStart: touch.pageY
  };
}

function isFloat(n) {
  return Number(n) === n && n % 1 !== 0;
}

function debug_value(name, value) {
  if (isFloat(value)) {
    value = value.toFixed(2)
  }
  document.getElementById(name).innerHTML = value;
}

function ongoingTouchIndexById(idToFind) {
  for (let i = 0; i < ongoingTouches.length; i++) {
    if (ongoingTouches[i].identifier == idToFind) {
      return i;
    }
  }
  return -1;
}

function sendMoveEvent(dx_koef, dy_koef) {
  ws.send(JSON.stringify({
    type: "move_event",
    dx_koef: dx_koef,
    dy_koef: dy_koef
  }))
}

function handleStart(evt) {
  evt.preventDefault();
  let touches = evt.changedTouches;

  for (let i = 0; i < touches.length; i++) {
    let touch = copyTouch(touches[i], evt.timeStamp);
    let idx = ongoingTouchIndexById(touch.identifier);
    if (idx < 0) {
      ongoingTouches.push(touch);
    } else {
      ongoingTouches[idx] = touch;
    }
  }
}


function handleMove(evt) {
  let touches = evt.changedTouches;
  for (let i = 0; i < touches.length; i++) {
    let idx = ongoingTouchIndexById(touches[i].identifier);
    if (idx < 0) {
      continue;
    }

    let dx = touches[i].pageX - ongoingTouches[idx].pageX;
    let dy = touches[i].pageY - ongoingTouches[idx].pageY;

    dy_koef = dy / -TOUCH_RADIUS;
    dx_koef = dx / TOUCH_RADIUS;

    debugCalculatedKoefs();
    debug_value("dx", dx);
    debug_value("dy", dy);

    sendMoveEvent(dx_koef, dy_koef);
  }
}

function debugCalculatedKoefs() {
  debug_value("dx_koef", dx_koef);
  debug_value("dy_koef", dy_koef);
}

function handleEnd(evt) {
  clearTimeout(touch_move_timeout)

  dx_koef = 0;
  dy_koef = 0;

  debug_value("dx", "");
  debug_value("dy", "");
  debugCalculatedKoefs();

  sendMoveEvent(dx_koef, dy_koef);
}

function handle_keydown(event) {
  const keyName = event.key;
  ws.send(JSON.stringify({
    "type": "keydown",
    "keyName": keyName
  }));
}

function handle_keyup(event) {
  const keyName = event.key;
  ws.send(JSON.stringify({
    "type": "keyup",
    "keyName": keyName
  }));
}

function handle_resize(event) {
  fetchScreenSize();
}

function fetchScreenSize() {
  screen_height = window.innerHeight;
  screen_width = window.innerHeight;
  debug_value("screen", screen_width + "x" + screen_height);
}

function connect() {
  ws = new WebSocket("ws://" + document.location.host + "/");

  ws.onmessage = function (e) {
    var event_data = JSON.parse(e.data);

    if (event_data.type == "moving_status") {
      debug_value("speed", event_data.speed)
      debug_value("turn", event_data.turn_deg)
    }
  };

  ws.onclose = function (e) {
    console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
    setTimeout(function () {
      connect();
    }, 1000);
  };
}

window.addEventListener("load", function () {
  console.log("Document loaded.")
  connect();

  fetchScreenSize();
  window.addEventListener('resize', handle_resize);
  window.addEventListener('orientationchange', handle_resize);

  //Disable touch menu
  window.oncontextmenu = function (event) {
    event.preventDefault();
    event.stopPropagation();
    return false;
  };

  //Handle keys
  document.addEventListener('keyup', handle_keyup);
  document.addEventListener('keydown', handle_keydown);

  let pad = document.getElementById("pad");

  // //Handle touch
  pad.addEventListener("touchstart", handleStart);

  let debounced_touch_move = debounce(handleMove, 10);

  pad.addEventListener("touchmove", debounced_touch_move);
  pad.addEventListener("touchend", handleEnd);
})

