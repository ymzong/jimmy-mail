#!/usr/bin/env python

# TODO:
# Story-board
# Different?
# Due SUNDAY
# 
# FEATURES:
# GROUP, IMPORT, TRASH, ... ...
# HUMAN LANGUAGE INTERPRETER
#
# DECEMBER!!!

import os
import sys
import curses                               # for console
import getpass                              # for password entering
import time                                 # for timing purposes
from appdata import *                       # Application constants
from mailbox import MailBoxIMAP, MailBoxSMTP, MailSession # Self-defined mailbox classes
from misc import *                          # Miscellaneous Functions
from IOControl import *
#import readline

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

def init():
    #readline.parse_and_bind('tab: complete')    # Tab Completion
    #readline.parse_and_bind('set editing-mode vi')  # Arrow Key Support
    validEmail = False
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

init()

#try: init()
#except: sys.exit(THANK_YOU_MSG)

