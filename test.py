import curses
import sys
import locale
locale.setlocale(locale.LC_ALL,"en_US.UTF-8")

def run(win):
    stdscr = win
    curses.noecho()
    curses.cbreak()
    curses.noraw()
    curses.curs_set(0)
    stdscr.keypad(1)
    stdscr.clearok(1)
    event = None
    while True:
        stdscr.clear()
        stdscr.box()
        stdscr.addstr(0,0,"\xe8\xbf\x8e\xe6\x9d\xa5\xe5\x88\xb0\xe4\xb8\xad\xe5\x8d\x8e\xe8\x8b\xb1\xe6\x89\x8d\xe7\xbd\x91\xef\xbc\x81", curses.A_REVERSE)
        event = stdscr.getch()
        if event == ord("b"): 
            break
        event = None

curses.wrapper(run)

