#!/usr/bin/env python

# main.py
# Yiming Zong - Carnegie Mellon University '16
# yzong (at) cmu.edu
# ----------------------------------------------------------------
#     This file is the main code that executes the program. Please
# DO NOT modify this file unless you are absolutely sure about what
# you are doing.

import os
import sys
import curses                               # for console
import getpass                              # for password entering
import time                                 # for timing purposes
from appdata import *                       # Application constants
from mailbox import MailBoxIMAP, MailBoxSMTP, MailSession # Mailbox classes
from misc import *                          # Miscellaneous Functions
from IOControl import *
import locale
locale.setlocale(locale.LC_ALL,"en_US.UTF-8")# Internalization purpose
reload(sys)
sys.setdefaultencoding("utf-8")

def run(win, MainSession):
    stdscr = win                            # Initiate Curses screen
    curses.noecho()                         # no output of keypress
    curses.cbreak()                         # Instant keystroke response
    curses.curs_set(0)                      # hide the cursor
    stdscr.keypad(1)                        # Enable keystroke response
    stdscr.clearok(1)
    class Struct(object): pass
    Appdata = Struct()
    Appdata.mode = ("WELCOME", None)
    event = None
    while True:
        stdscr.clear()
        stdscr.box()
        drawScr(stdscr, MainSession, Appdata)
        event = stdscr.getch()
        if event in keyResponse[Appdata.mode[0]]:
            keyRespond(stdscr, MainSession, Appdata, event)
        event = None
    # Terminate the program
    exitApp(stdscr)

#     This function processes arguments passed from terminal,
# then calls the curses window for program execution.
def init():
    validEmail = False
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and
            not isValidEmail(sys.argv[1].lower())):
        print ARG_USAGE
        sys.exit(0)
    elif len(sys.argv) == 2 and isValidEmail(sys.argv[1].lower()):
        validEmail, EmailAddr = True, sys.argv[1].lower()
    while not validEmail:
        EmailAddr = raw_input(EMAIL_PROMPT)
        validEmail = isValidEmail(EmailAddr)
        if EmailAddr == "q":
            sys.exit(THANK_YOU_MSG);
        if not validEmail:
            print EMAIL_INVALID 
    MainSession = MailSession(EmailAddr)
    print WAIT_FOR_ENTER; tmp = raw_input()
    runWithSession = lambda win : run(win, MainSession)
    curses.wrapper(runWithSession)
    MainSession.close()

try: init()
except: sys.exit(THANK_YOU_MSG)

