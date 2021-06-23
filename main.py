#!/usr/bin/env python3

import curses
import math
import traceback
from time import sleep

from pyroombaadapter import PyRoombaAdapter

PORT = "/dev/ttyUSB0"
adapter = PyRoombaAdapter(PORT)
adapter.change_mode_to_full()


def mini_sleep():
    sleep(0.03)


def deg2radians(f):
    return math.radians(f)


# noinspection PyBroadException
try:
    # -- Initialize --
    stdscr = curses.initscr()  # initialize curses screen
    curses.noecho()  # turn off auto echoing of keypress on to screen
    curses.cbreak()  # enter break mode where pressing Enter key
    #  after keystroke is not required for it to register
    stdscr.keypad(True)  # enable special Key values such as curses.KEY_LEFT etc

    # -- Perform an action with Screen --
    stdscr.border(0)
    stdscr.addstr(5, 5, 'Roomba controller ->>> ', curses.A_BOLD)
    stdscr.addstr(6, 5, ' UP, DOWN, LEFT, RIGHT', curses.A_BOLD)
    stdscr.addstr(7, 5, 'q w e', curses.A_BOLD)
    stdscr.addstr(8, 5, 'a s d', curses.A_BOLD)
    stdscr.addstr(9, 5, 'Press Ctrl-C to close this screen', curses.A_NORMAL)
    stdscr.nodelay(True)

    running = True

    while running:
        # stay in this loop till the user presses 'q'

        ch = -1
        last = None
        skip_count = 0

        # Skip repeats
        while True:
            skip_count += 1
            last = stdscr.getch()
            if (ch > 0 and last == -1) or skip_count > 10000:
                # print(skip_count)
                break
            ch = last

        if ch == curses.KEY_UP or ch == ord('w'):
            adapter.move(0.2, deg2radians(0.0))  # go straight
            mini_sleep()
        if ch == curses.KEY_DOWN or ch == ord('s'):
            adapter.move(-0.2, math.radians(0.0))  # go straight
            mini_sleep()
            # adapter.move(0, math.radians(0.0))
        if ch == curses.KEY_LEFT or ch == ord('a'):
            adapter.move(0, math.radians(40))  # turn left
            mini_sleep()
            # adapter.move(0, math.radians(0.0))
        if ch == curses.KEY_RIGHT or ch == ord('d'):
            adapter.move(0, math.radians(-40))  # turn right
            mini_sleep()
            # adapter.move(0, math.radians(0.0))
        if ch == ord('q'):
            adapter.move(0.2, math.radians(40))  # go straight
            mini_sleep()
        if ch == ord('e'):
            adapter.move(0.2, math.radians(-40))  # go straight
            mini_sleep()
        if ch == -1:
            pass
            # print("Stop" + str(skip_count))
            adapter.move(0, math.radians(0.0))
        if ch == ord('x'):
            adapter.move(0, math.radians(0.0))
            break

    # -- End of user code --

except:
    traceback.print_exc()  # print trace back log of the error

finally:
    # --- Cleanup on exit ---
    curses.echo()
    curses.nocbreak()
    curses.endwin()
