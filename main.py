#!/usr/bin/env python3

import argparse
import asyncio
import functools
import json
import logging
import math
import os
import sys
import time
from enum import Enum
from http import HTTPStatus

import websockets
from pyroombaadapter import PyRoombaAdapter

logger = logging.getLogger(__name__)

SPEED = 0.2
TURN_DEG = 40

SERVER = "0.0.0.0"
PORT = 8765
TTY = "/dev/ttyUSB0"


class DummyAdapter:
    @staticmethod
    def move(speed, turn):
        pass


adapter = None

MIME_TYPES = {
    "html": "text/html",
    "js": "text/javascript",
    "css": "text/css"
}


class Key(Enum):
    UP = 1
    DOWN = 2
    RIGHT = 3
    LEFT = 4
    SHIFT = 5


key_loop = {}

cur_koef = 1
cur_speed = 0
cur_turn_rad = 0


async def rc_input(websocket, path):
    while True:
        event_json = await websocket.recv()
        # print(f"< {event_json}")

        event = json.loads(event_json)

        if event['event'] == 'keydown':
            ev_time = time.time()  # Need to trace press order

            if event['keyName'] in ['Shift']:
                key_loop[Key.SHIFT] = ev_time
            if event['keyName'] in ['ArrowUp', 'w', 'W']:
                key_loop[Key.UP] = ev_time
            if event['keyName'] in ['ArrowDown', 's', 'S']:
                key_loop[Key.DOWN] = ev_time
            if event['keyName'] in ['ArrowLeft', 'a', 'A']:
                key_loop[Key.LEFT] = ev_time
            if event['keyName'] in ['ArrowRight', 'd', 'D']:
                key_loop[Key.RIGHT] = ev_time

        if event['event'] == 'keyup':
            if event['keyName'] in ['Shift']:
                del key_loop[Key.SHIFT]

            if event['keyName'] in ['ArrowUp', 'w', 'W']:
                del key_loop[Key.UP]
            if event['keyName'] in ['ArrowDown', 's', 'S']:
                del key_loop[Key.DOWN]
            if event['keyName'] in ['ArrowLeft', 'a', 'A']:
                del key_loop[Key.LEFT]
            if event['keyName'] in ['ArrowRight', 'd', 'D']:
                del key_loop[Key.RIGHT]

        koef = 1
        speed = 0
        turn_rad = 0

        if Key.SHIFT in key_loop:
            koef = 1.5

        if Key.LEFT in key_loop and (not key_loop.get(Key.RIGHT) or key_loop[Key.LEFT] > key_loop[Key.RIGHT]):
            turn_rad = koef * TURN_DEG

        if Key.RIGHT in key_loop and (not key_loop.get(Key.LEFT) or key_loop[Key.RIGHT] > key_loop[Key.LEFT]):
            turn_rad = koef * -TURN_DEG

        if Key.UP in key_loop:
            speed = koef * SPEED

        if Key.DOWN in key_loop:
            speed = koef * -SPEED

        global cur_koef
        global cur_speed
        global cur_turn_rad

        if (cur_koef, cur_speed, cur_turn_rad) != (koef, speed, turn_rad):
            """ Process only when changes (for optimize) """

            cur_koef, cur_speed, cur_turn_rad = (koef, speed, turn_rad)
            adapter.move(speed, math.radians(turn_rad))
            print(f'Moving: {speed=} , {turn_rad=}', flush=True)

            await mini_sleep()
            await websocket.send(json.dumps({"type": "moving_status", "speed": speed, "turn_rad": turn_rad}))


async def mini_sleep():
    await asyncio.sleep(0.03)


async def serve_static(sever_root, path, request_headers):
    """Serves a file when doing a GET request with a valid path."""

    if "Upgrade" in request_headers:
        return  # Probably a WebSocket connection

    if path in ['/']:
        path = '/index.html'

    response_headers = [
        ('Server', 'asyncio websocket server'),
        ('Connection', 'close'),
    ]

    # Derive full system path
    full_path = os.path.realpath(os.path.join(sever_root, path[1:]))

    # Validate the path
    if os.path.commonpath((sever_root, full_path)) != sever_root or \
            not os.path.exists(full_path) or not os.path.isfile(full_path):
        print("HTTP GET {} 404 NOT FOUND".format(path))
        return HTTPStatus.NOT_FOUND, [], b'404 NOT FOUND'

    # Guess file content type
    extension = full_path.split(".")[-1]
    mime_type = MIME_TYPES.get(str(extension), "application/octet-stream")
    response_headers.append(('Content-Type', mime_type))

    # Read the whole file into memory and send it out
    body = open(full_path, 'rb').read()
    response_headers.append(('Content-Length', str(len(body))))
    print("HTTP GET {} 200 OK".format(path))
    return HTTPStatus.OK, response_headers, body


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("-d", "--dummy", help="use dummy adapter (for test)",
                        action="store_true")
    args = parser.parse_args()

    if args.dummy:
        adapter = DummyAdapter()
    else:
        adapter = PyRoombaAdapter(TTY)

    try:
        handler = functools.partial(serve_static, os.getcwd() + "/static")
        start_server = websockets.serve(rc_input, SERVER, PORT, process_request=handler)
        print("Roomba RC starting...", flush=True)
        print(f"Server: http://{SERVER}:{PORT}", flush=True)
        print(f"WebSocket: ws://{SERVER}:{PORT}", flush=True)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
        sys.exit(0)
    except Exception as e:
        print(e)
        adapter.move(0, math.radians(0))
        sys.exit(1)
    finally:
        del adapter
