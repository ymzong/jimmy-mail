import curses

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
        stdscr.addstr(0,0,"hi")
        event = stdscr.getch()
        if event == ord("b"): 
            break
        event = None

curses.wrapper(run)

