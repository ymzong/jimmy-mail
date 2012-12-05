import curses

from itertools import cycle
import curses, contextlib, time

@contextlib.contextmanager
def curses_screen():
    """Contextmanager's version of curses.wrapper()."""
    try:
        stdscr=curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(1)
        try: curses.start_color()
        except: pass

        yield stdscr
    finally:
        stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()

with curses_screen() as stdscr:
    pad = curses.newpad(100, 100)
    pad.addstr(0,0, curses.longname())
    t = [None] * 10
    t[1] = "dfafsd'dfasdfasf'dfasdfasdf" * 20
    pad.addstr(t[1])
    for i in range(2, 10):
        pad.addstr(i,0, str(i))

    coord = 1, 1, 20, 75
    pad.refresh(0, 0, *coord)

    KEY_UP, KEY_DOWN = 'AB'
    y = 0
    for c in iter(pad.getkey, 'q'):
        if c in '\x1b\x5b': continue # skip escape seq
        y -= (c == KEY_UP)
        y += (c == KEY_DOWN)
        y = min(max(y, 0), 9)
        pad.refresh(y, 0, *coord)
