import curses
from typing import List
import libvirt_remote_manager._db_types as db_types

class PairMenu():
    def __init__(self, selections: List[db_types.Device], intent: str):
        self.selections = selections
        self.intent = intent

    def select(self):
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.screen.keypad(True)

        selected = 0

        input_key = None
        while input_key != ord('\n'):
            max_y, max_x = self.screen.getmaxyx()

            self.screen.addstr(1, 1, "Select device to " + self.intent)
            self.screen.addstr(max_y - 1, 1, "Use Up and Down Arrows to choose, Enter to select, Q to cancel")

            for option in range(len(self.selections)):
                self.screen.addstr(3 + option, 4, str(self.selections[option]))
                self.screen.addch(3 + option, 2, ' ')

            self.screen.addch(3 + selected, 2, '>')

            self.screen.refresh()

            input_key = self.screen.getch()
            down_keys = [curses.KEY_DOWN]
            up_keys = [curses.KEY_UP]
            exit_keys = [ord('q')]

            if input_key in down_keys:
                if selected < len(self.selections) - 1:
                    selected += 1
                else:
                    selected = 0

            if input_key in up_keys:
                if selected > 0:
                    selected -= 1
                else:
                    selected = len(self.selections) - 1

            if input_key in exit_keys:
                selected = -1
                break

        self.screen.keypad(False)
        curses.curs_set(1)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        return selected
