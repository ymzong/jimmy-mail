import time
import curses
import curses.textpad
import sys
from appdata import *
from misc import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.message import MIMEMessage
from email.parser import Parser
from email.header import decode_header as Decode
import email.utils
from email import message_from_string as Proc
import imaplib
import locale
locale.setlocale(locale.LC_ALL,"en_US.UTF-8")
from html2text import html2text
from email.utils import parseaddr as ParseAddr

############################# KEY RESPOND UNIT #########################
keyResponse = dict()
keyResponse["WELCOME"] = [10, ord("q")]   # Enter
keyResponse["MAIN_MENU"] = [ord("0"), ord("1"), ord("2"),
                            ord("s"), ord("h"), ord("q"),
                            ord("S"), ord("H"), ord("Q")]
EML_LST_GEN = [ord('q'),ord('Q'),curses.KEY_UP,curses.KEY_DOWN,
            curses.KEY_PPAGE,curses.KEY_NPAGE]
EML_LST_EDT = [ord("D"), ord("r"), ord("R"), ord("F"), ord("f")]
EML_LST_GO = [ord(" "), 10, 13, ord("\n"), curses.KEY_ENTER]
# This is the key responder for Welcome Mode and Main Menu Mode (simple).
def keyRespond(stdscr, MainSession, Appdata, event):
    if Appdata.mode[0] == "WELCOME":
        respondWelcome(stdscr, MainSession, Appdata, event)
    if Appdata.mode[0] == "MAIN_MENU":
        respondMainMenu(stdscr, MainSession, Appdata, event)

# This is called when the program exits. Connection to server is closed.
def exitApp(stdscr):
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo
    curses.endwin()
    sys.exit(THANK_YOU_MSG)

# This is the key respond wrapper for Welcome Screen ("q" or ENTER).
def respondWelcome(stdscr, MainSession, Appdata, event):
    if event == ord("q"):
        exitApp(stdscr)
    elif event == 10:
        Appdata.mode = ("MAIN_MENU", None)

# This is the key respond wrapper for Main Menu (three options).
def respondMainMenu(stdscr, MainSession, Appdata, event):
    if event in [ord("s"), ord("S"), ord("0")]:
        smartCommand(stdscr, MainSession, Appdata, event)
    if event in [ord("h"), ord("H"), ord("1")]:
        displayHelp(stdscr)
    if event in [ord("2"), ord("q"), ord("Q")]:
        exitApp(stdscr)

############################# DRAW SCREEN UNIT #########################
# This is the dispatcher for drawing Main Menu and Welcome Screen.
def drawScr(stdscr, MainSession, Appdata):
    if Appdata.mode[0] == "WELCOME":
        drawScrWelcome(stdscr)
    elif Appdata.mode[0] == "MAIN_MENU":
        drawScrMainMenu(stdscr, MainSession)

# This function draws the welcome screen message.
def drawScrWelcome(stdscr):
    (maxY, maxX) = stdscr.getmaxyx()
    topMargin = max((maxY - 5) / 2, 1)
    for i in xrange(6):
        stdscr.addstr(min(topMargin + i, maxY - 1), max((maxX - 
            len(WELCOME_MSG[i])) / 2, 0),WELCOME_MSG[i])

# This function reads and respond to all Command Line inputs.
# (Command Line Interface Mainloop)
def smartCommand(stdscr, MainSession, Appdata, event):
    (maxY,maxX) = stdscr.getmaxyx()
    curses.raw(); curses.cbreak(); curses.curs_set(1); curses.setsyx(0,0)
    stdscr.erase(); stdscr.refresh(); curses.reset_shell_mode()
    SmartModeInstruct(maxX)
    command = raw_input(">> ")
    while True:
        if command.lower() in Q_LIST:   break
        elif command.lower() in H_LIST: SmartModeInstruct(maxX)
        elif command.lower() in I_LIST: displayInbox(MainSession, stdscr)
        elif command.lower() in S_LIST: searchMailApp(MainSession, stdscr)
        elif command.lower() in N_LIST: sendMailApp(MainSession)
        elif command != "": parseSmart(MainSession, command, stdscr)
        command = raw_input(">> ")
    exitApp(stdscr)

# This function is Jimmy-Bot, the human language interpreter.
def parseSmart(MainSession, command, stdscr):
    cmdParts = command.lower().split(" ")
    if (("list" in command and "folder" in command)     # List all folders.
            or command.lower() in LFDR_LIST):
        print "Accessible Folders:", MainSession.IMAP.getFolderList()
    elif command in MainSession.IMAP.getFolderList():   # Browse one folder.
        MainSession.IMAP.session.select(command)
        if MainSession.IMAP.getMsgCount() == 0: print INBOX_EPT
        else: emailLister(MainSession, [int(msgNoStr) for msgNoStr in\
                MainSession.IMAP.session.search(None, "ALL")\
                [1][0].split(" ")], stdscr)
    elif (len(cmdParts) >= 3 and cmdParts[0] in N_LIST and # Send to given eml
          isValidEmail(cmdParts[2])): sendMailApp(MainSession, [cmdParts[2]])
    elif "about" in cmdParts or "from" in cmdParts:
        parseSearchCommand(MainSession, command, stdscr)
    else: print NOT_UNDSTD

# This function specifically concentrates on parsing "search" commands.
def parseSearchCommand(MainSession, command, stdscr):
    cmdParts = command.lower().split(" ")
    AboutPosi = cmdParts.index("about") if "about" in cmdParts else -1
    FromPosi = cmdParts.index("from") if "from" in cmdParts else -1
    # Both Keywords not found.
    if AboutPosi == -1 and FromPosi == -1:  print NOT_UNDSTD
    elif AboutPosi == -1:   # Only FROM is present.
        if " ".join(cmdParts[:FromPosi]) in EML_INDICATION:
            performSearch(MainSession, [MainSession.IMAP.getInboxFolder(),
                " ".join(cmdParts[FromPosi+1:]), True, None, None], stdscr)
    elif FromPosi == -1:    # Only ABOUT is present.
        if " ".join(cmdParts[:AboutPosi]) in EML_INDICATION:
            performSearch(MainSession, [MainSession.IMAP.getInboxFolder(),
                "", "", "", " ".join(cmdParts[AboutPosi+1:])], stdscr)
    else:                   # Both FROM and ABOUT are present.
        if " ".join(cmdParts[:min(AboutPosi, FromPosi)]) in EML_INDICATION:
            performSearch(MainSession, [MainSession.IMAP.getInboxFolder(),
                " ".join(cmdParts[FromPosi+1:AboutPosi if AboutPosi > FromPosi
                else len(cmdParts)]), "", "", " ".join(cmdParts[AboutPosi+1:
                FromPosi if FromPosi > AboutPosi else len(cmdParts)])],stdscr)

# This function lists all emails of Inbox.
def displayInbox(MainSession, stdscr):
    try: MainSession.IMAP.session.select(MainSession.IMAP.getInboxFolder())
    except Exception as err: print INBOX_ERR % err
    else:
        if MainSession.IMAP.getMsgCount() == 0:
            print INBOX_EPT
        else:
            emailLister(MainSession, [int(msgNoStr) for msgNoStr in\
                MainSession.IMAP.session.search(None, "ALL")\
                [1][0].split(" ")], stdscr)

# This function prompts (via command line) the user to input mail recipient.
def getEmailTo():
    EmailTo = list()
    CurrentEmail = raw_input("|To: ")
    while (CurrentEmail != "") or (len(EmailTo) == 0):
        if CurrentEmail.lower() == "#q#":
            return
        elif len(EmailTo) == 0 and (CurrentEmail == ""):
            print RECV_EMPTY
        elif isValidEmail(CurrentEmail):
            EmailTo.append(CurrentEmail)
        else:
            print RECV_INVALID
        CurrentEmail = raw_input("|To: ")
    return EmailTo

# This function reads the email's content from user.
def getEmailText():
    print EMLTXT_INTRO
    EmailText = list()
    CurrentLine = raw_input("% ")
    while (CurrentLine.lower() != "#end#"):
        if CurrentLine.lower() == "#q#": return None
        EmailText.append(CurrentLine)
        CurrentLine = raw_input("% ")
    result = ""
    for i in xrange(len(EmailText)):
        result += EmailText[i] + "\n"
    return result

#     This function gathers all information necessary for email, then
#  send the email using imaplib.
def sendMailApp(MainSession, emlTgt = None):
    curses.curs_set(1)                      # show the cursor
    print SEND_INTRO
    if emlTgt == None: print "|From: " + MainSession.Email_Addr
    if emlTgt == None: EmailTo = getEmailTo()
    else: EmailTo = emlTgt
    if processEmlTo(MainSession, EmailTo) == False: return
    EmailTitle = raw_input("|Subject: ")
    EmailTitle = processEmlTitle(EmailTitle)
    if EmailTitle == False: return
    EmailText = getEmailText()
    if EmailText == None: curses.curs_set(0); return
    EmailMIME = MIMEText(EmailText)
    EmailMIME["From"] = MainSession.Email_Addr
    EmailMIME["To"] = ";".join(EmailTo)
    EmailMIME["Subject"] = EmailTitle
    try: MainSession.SMTP.session.sendmail(MainSession.Email_Addr,
            EmailTo, EmailMIME.as_string())     # Send the Mail!
    except Exception as err: print SEND_ERR % err
    else:   confirmDraft(MainSession, EmailTo, EmailMIME)

# This function displays the Recipients of the email (if any).
def processEmlTo(MainSession, EmailTo):
    if EmailTo == None:
        return False
    ToDisplay =  "-"*10 + "\n"+"|From: "+MainSession.Email_Addr+"\n|To: "
    for i in xrange(len(EmailTo) - 1):
        ToDisplay += EmailTo[i] + "; "
    ToDisplay += EmailTo[len(EmailTo) - 1]
    print ToDisplay
    return True

# This function reads the email title of the email to be sent.
def processEmlTitle(EmailTitle):
    if EmailTitle.lower() == "#q#": return False
    while True:
        if len(EmailTitle) == 0:
            tmp = raw_input(NO_TITLE_CONF)
            if tmp == "y": break
            else: EmailTitle = raw_input("|Subject: ")
        else:   break
    return EmailTitle

# This function asks user whether to save sent message.
# If user chooses yes, then save a copy to Sent Folder.
def confirmDraft(MainSession, EmailTo, EmailMIME):
    EmailMIME["Date"] = email.utils.formatdate(None, True) # Time Tag!
    choice = raw_input(SAVE_MSG % ",".join(EmailTo))
    while True:
        if choice == "y":
            if MainSession.SentFolderName == None:
                MainSession.SentFolderName = MainSession.IMAP.setSentFolder()
            if MainSession.SentFolderName == "":
                print SND_FDR_NIL
            else:
                try: MainSession.IMAP.session.append(\
                        MainSession.SentFolderName, "(\\Seen)",
                        imaplib.Time2Internaldate(time.time()),
                        EmailMIME.as_string())
                except Exception: print SAVE_ERR % MainSession.SentFolderName
                else: print SAVE_SUCC % MainSession.SentFolderName
            break
        elif choice == "n": break
        else: choice = raw_input(Y_OR_N)

# This function draws the Main Menu on the screen.
# It is not "hard-coded" such that the menu items are easily changable.
def drawScrMainMenu(stdscr, MainSession):
    (maxY, maxX) = stdscr.getmaxyx()
    InitStr = LOGGED_IN_AS + MainSession.Email_Addr
    stdscr.addstr(0, max((maxX - len(JIMMY_MAIL)) / 2, 0), JIMMY_MAIL)
    stdscr.addstr(1, max((maxX - len(InitStr)) / 2, 0), InitStr)
    menuItems = len(MENU_ENTRIES)
    if maxY > 2 * menuItems + 2:
        topMargin = (maxY - menuItems * 2 - 3) / 2
        for i in xrange(menuItems):
            stdscr.addstr(min(topMargin + 2 * i + 2, maxY - 2),
                    max((maxX - len(MENU_ENTRIES[i])) / 2, 0),
                    MENU_ENTRIES[i])
    else:
        topMargin = max((maxY - menuItems - 3) / 2 + 2, 2)
        for i in xrange(menuItems):
            stdscr.addstr(min(topMargin + i, maxY - 2),
                    max((maxX - len(MENU_ENTRIES[i])) / 2, 0),
                    MENU_ENTRIES[i])

#     This function gathers user's response to Search Command, then
# display the result with performSearch function.
def searchMailApp(MainSession, stdscr):
    curses.curs_set(1)
    print SEARCH_PMPT
    sCriteria = list()
    sCriteria.append(getSourceFolder(MainSession))
    if sCriteria[0] == None: return
    for i in xrange(4):
        sCriteria.append(getSearchInfo(i))
        if sCriteria[-1] == None:   
            curses.curs_set(0); return  # Quit Search
        elif sCriteria[-1] == True:
            break
    performSearch(MainSession, sCriteria, stdscr)

#     This function constructs a search string and send it to IMAP server,
# which is in accordance with RFC 3501 standard. 
def performSearch(MainSession, sCriteria, stdscr):
    try: MainSession.IMAP.session.select(sCriteria[0])
    except: 
        print BROWSE_ERR
        return
    else:
        searchStr, existing = "(", 0
        for item in sCriteria:
            if (item != "") and (item != True):  existing += 1
        if existing <= 1:
            print CRITERIA_ERR
            return
        else:
            for i in xrange(1, 5):
                if sCriteria[i] == True: break
                elif sCriteria[i] != "":
                    searchStr += KEYWD_STR[i] + " \"" + sCriteria[i] + "\" "
            searchStr = searchStr[:-1] + ")"
            displayResult(MainSession, searchStr, stdscr)

#     This function constructs a message list from the Search Result,
# then call emailLister function to list the results.
def displayResult(MainSession, searchStr, stdscr):
    try:    msgIDs = MainSession.IMAP.session.search(None, searchStr)[1][0]
    except Exception as err: print SEARCH_ERR % err
    else:
        if msgIDs == "":    # If list is empty, return "Nothing Found".
            print SEARCH_EMPTY
            return
        else:
            msgNOs = [int(num) for num in msgIDs.split(" ")]
            raw_input(SEARCH_RESULT)
            emailLister(MainSession, msgNOs, stdscr)

#     This is the EmailLister function that handles requests from Search
# command, Inbox display, Folder display, etc.
#     Entries Per Page: MaxY - 5
def emailLister(MainSession, msgNOs, stdscr):
    curses.def_shell_mode(); curses.reset_prog_mode()    # Back to curses
    curses.curs_set(0); stdscr.clear(); stdscr.refresh() # Init curses
    maxY, maxX = stdscr.getmaxyx(); stdscr.clear(); stdscr.box()
    stdscr.addstr(0, max(0, (maxX - len(JIMMY_MAIL)) / 2), JIMMY_MAIL)
    stdscr.addstr(min(2,maxY-1),max(0,(maxX-len(PLEASE_WAIT))/2),PLEASE_WAIT)
    stdscr.refresh()
    emlData = fetchList(MainSession, msgNOs, stdscr)    # Retrieve Messages
    (maxDigit,flag,event,currentTop,currentSelect)=(digitNo(len(msgNOs)),
            True, None, 0, 0)
    while flag:
        maxY, maxX = stdscr.getmaxyx(); stdscr.clear(); stdscr.box()
        stdscr.addstr(0, max(0, (maxX - len(JIMMY_MAIL)) / 2), JIMMY_MAIL)
        # Draw the Email list by calling drawList().
        drawList(MainSession, stdscr, emlData, currentTop, currentSelect)
        # Draw the footnotes by calling drawInstruction().
        drawInstruction(MainSession, stdscr)
        event = stdscr.getch();
        # Respond to key stroke events.
        (flag, event, currentSelect, currentTop, maxY, msgNOs, emlData) =\
            emailListResponder(event, MainSession, emlData, currentSelect,
                    currentTop, maxY, msgNOs, flag, stdscr)
    stdscr.clear(); stdscr.refresh()
    curses.reset_shell_mode(); curses.curs_set(1)   # Restore to shell mode.

# This function is the key stroke responder for EmailList().
def emailListResponder(event, MainSession, emlData, currentSelect,
        currentTop, maxY, msgNOs, flag, stdscr):
    if event in EML_LST_GEN:    # For position movements.
        (flag, event, currentSelect, currentTop, maxY, msgNOs) =\
          respondGeneral(flag,event,currentSelect,currentTop,maxY,msgNOs)
    elif event in EML_LST_EDT:  # For email property operations.
        (emlData, msgNOs) = modifyEml(MainSession, emlData, msgNOs,
                currentSelect, event, stdscr)
    elif event in EML_LST_GO:   # For entering View Mode
        try:
            emlData[1][currentSelect] = setRead(emlData[1][currentSelect])
            viewEmail(MainSession, emlData, msgNOs, currentSelect, stdscr)
        except Exception: pass  # If exception happens, do no operations.
    curses.napms(50)        # Anti-flashing
    return (flag, event, currentSelect, currentTop, maxY, msgNOs, emlData)

# This function sets the status of a locally stored email to "Read".
def setRead(inFlags):
    if inFlags.find("\\Seen") == -1:
        inFlags += "\\Seen"
    return inFlags

# This function sets the status of a locally stored email to "Replied".
def setReplied(inFlags):
    if inFlags.find("\\Answered") == -1:
        inFlags += "\\Answered"
    return inFlags

# This function snaps the Plain Text bit of raw email message.
def processCodec(msgCodec):
    txtMsg = None
    for part in msgCodec.walk():
        # If we have text/plain, then we are good.
        if part.get_content_type() == "text/plain":
            txtMsg = part.get_payload().replace("\r","").\
                    replace("\n\n","\n")
            break
    if txtMsg == None:  # If no plain text available, use html version.
        for part in msgCodec.walk():
            if part.get_content_type() == "text/html":
                try: txtMsg = FROM_HTML+html2text(part.get_payload())
                except Exception: txtMsg = ERR_PARSING
                else:break
    if txtMsg == None:  # No Text and HTML, show error.
        txtMsg = NO_TXT_AVAIL
    return txtMsg

# This function contains the mainloop for Email-Reading interface.
def viewEmail(MainSession, emlData, msgNOs, currentSelect, stdscr):
    # Set up curses.
    curses.def_prog_mode();curses.curs_set(0);stdscr.clear();stdscr.refresh()
    maxY, maxX = stdscr.getmaxyx(); stdscr.box()
    stdscr.addstr(0,max(0,(maxX-len(JIMMY_MAIL))/2),JIMMY_MAIL)
    stdscr.addstr(min(2,maxY-1),max(0,(maxX-len(PLEASE_WAIT))/2),
            PLEASE_WAIT)
    stdscr.refresh();
    txtMsg = processCodec(Proc(MainSession.IMAP.fetchMsg(\
            emlData[3][currentSelect])[1][0][1])) + EOM   # Retrieve message.
    (flag,event,currentTop)=(True, None, 0)
    while flag:
        maxY, maxX = stdscr.getmaxyx()
        maxLen = getMaxLen(txtMsg.split("\n"), maxX)
        createMailGraphics(MainSession, emlData, txtMsg, stdscr, currentSelect, currentTop)
        event = stdscr.getch()      # Get Keyboard Inputs
        if event in [ord('q'),ord('Q'),curses.KEY_UP,curses.KEY_DOWN,curses.KEY_PPAGE,curses.KEY_NPAGE]:
            (flag,currentTop)=respondMsgPg(flag,event,currentTop,maxY,maxLen)
        elif event in [ord("D"), ord("r"), ord("R"), ord("F"), ord("f")]:
            (emlData, msgNOs) = modifyEml(MainSession, emlData, msgNOs, currentSelect, event, stdscr)
            if event == ord("D"): flag = False   # Quit Email Viewing

#     Email texts are displayed on a "Pad" of curses, which supports
# scrolling options.
def createMailGraphics(MainSession, emlData, txtMsg, stdscr, currentSelect, currentTop):
    maxY, maxX = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.box()
    stdscr.addstr(0,max(0,(maxX-len(JIMMY_MAIL))/2),JIMMY_MAIL)
    stdscr.refresh()
    coord = (6, 1, maxY - 4, maxX - 1)
    maxLen = len(txtMsg) / (maxX - 2) + txtMsg.count("\n") + 1
    pad = curses.newpad(maxLen, maxX - 2)
    pad.clear()
    pad.refresh(currentTop, 0, *coord)
    drawBasicInfo(MainSession, emlData, currentSelect, stdscr)
    try: pad.addstr(0,0, txtMsg); pad.refresh(currentTop, 0, *coord)
    except: pass

def getMaxLen(msgList, maxX):
    maxLen = -2
    for line in msgList:
        maxLen += len(line) / (maxX - 2) + 1
    return max(maxLen, 0)

def displayHelp(stdscr):
    stdscr.clear();
    maxY, maxX = stdscr.getmaxyx();
    stdscr.box()
    stdscr.addstr(0,max(0,(maxX-len(JIMMY_MAIL))/2),JIMMY_MAIL)
    stdscr.refresh()
    flag, currentTop = True, 0
    # Read data from readme file.
    with open('readme.txt', 'r') as readmeF:
        textList = readmeF.readlines()
    maxLen = getMaxLen(textList, maxX)
    while flag:
        maxY, maxX = stdscr.getmaxyx()
        drawHelp(stdscr, textList, currentTop)
        event = stdscr.getch()
        (flag,currentTop) = respondMsgPg(flag,event,currentTop,maxY,maxLen)
    return

def drawHelp(stdscr, textList, currentTop):
    maxY, maxX = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.box()
    stdscr.addstr(0,max(0,(maxX-len(JIMMY_MAIL))/2),JIMMY_MAIL)
    stdscr.addstr(maxY - 2, max(0, (maxX - len(HLP_INSTR)) / 2), HLP_INSTR)
    stdscr.refresh()
    coord = (1, 1, maxY - 3, maxX - 1)
    maxLen = 10
    for line in textList:
        maxLen += len(line) / (maxX - 2) + 1
    pad = curses.newpad(maxLen, maxX - 2)
    pad.clear()
    pad.addstr(0,0, "".join(textList));
    pad.refresh(currentTop, 0, *coord)

# This function responds to Message Scrolling key strokes.
def respondMsgPg(flag, event, currentTop, maxY, maxLen):
    if event == ord('q') or event == ord('Q'):
        flag = False
    else:
        currentTop -= (event == curses.KEY_UP)
        currentTop += (event == curses.KEY_DOWN)
        currentTop += (event == curses.KEY_NPAGE) * maxY / 3
        currentTop -= (event == curses.KEY_PPAGE) * maxY / 3
        currentTop = min(max(currentTop, 0), maxLen - 2)
    return flag, currentTop

# This function draws information from email Header then prints basic data.
def drawBasicInfo(MainSession, emlData, currentIndex, stdscr):
    maxY, maxX = stdscr.getmaxyx()
    for i in xrange(len(INSTRUCT_MSG)):
        stdscr.addstr(max(maxY-len(INSTRUCT_MSG)+i-1, 0), 
                max((maxX - len(INSTRUCT_MSG[i])) / 2, 0),INSTRUCT_MSG[i])
    emlHeader, emlFlg, emlSize, toDisplayNOs = emlData
    currentEml = (emlHeader[currentIndex], emlFlg[currentIndex],
            emlSize[currentIndex])
    stdscr.addstr(1,1,"Date: " + currentEml[0]["Date"])
    stdscr.addstr(2,1,"From: " + currentEml[0]["From"][:maxX - 2])
    stdscr.addstr(3,1,"To: " + (currentEml[0]["To"].replace("\r","").\
            replace("\n", "")[:maxX - 6] or UNDISCLOSED_RCP))
    stdscr.addstr(4,1,"Subject: " + currentEml[0]["Subject"].\
            replace("\r","").replace("\n", "")[:maxX - 11] or NO_TITLE)
    stdscr.addstr(5,1,"*"*(2 * maxX / 3))

# This function prints key stroke helps at the bottom of View Mail Mode.
def drawInstruction(MainSession, stdscr):
    for i in xrange(len(INSTRUCT1)):
        maxY, maxX = stdscr.getmaxyx()
        stdscr.addstr(max(maxY-len(INSTRUCT1)+i-1, 0),
                max((maxX - len(INSTRUCT1[i])) / 2, 0),INSTRUCT1[i])

# This function dispatchs email-related events to sub-functions.
def modifyEml(MainSession, emlData, msgNOs, currentSelect, event, stdscr):
    if event == ord("f") or event == ord("F"):  # Flag/Unflag
        emlData[1][currentSelect] = MainSession.IMAP.setFlagged(\
                emlData[3][currentSelect], emlData[1][currentSelect])
    elif event == ord("D"):                     # Move to Trash
        originalMsgNo = emlData[3][currentSelect]
        succeed = MainSession.IMAP.setDelete(originalMsgNo, emlData)
        if succeed == True:
            msgNOs.pop(currentSelect)
            for part in emlData:  part.pop(currentSelect)
            MainSession.IMAP.setPurge(originalMsgNo)
    elif event == ord("R") or event == ord("r"):    # Reply to Message
        emlData = replyEmailApp(MainSession, emlData, currentSelect, stdscr)
    return emlData, msgNOs

# This function handles the Reply-to-Email request.
def replyEmailApp(MainSession, emlData, currentSelect, stdscr):
    curses.def_prog_mode(); stdscr.clear(); stdscr.refresh()
    curses.reset_shell_mode(); print PROC_ORIGINAL
    msgCodec = Proc(MainSession.IMAP.fetchMsg(\
            emlData[3][currentSelect])[1][0][1])        # Fetch original Msg
    toSendMsg = constructReply(MainSession, msgCodec)   # Gather reply MIME
    try: MainSession.SMTP.session.sendmail(toSendMsg["From"], 
            ParseAddr(toSendMsg["To"])[1], toSendMsg.as_string())
    except Exception as err: print SEND_ERR % err; raw_input()
    else:       # If sending is successful, then ask whether save to draft.
        confirmDraft(MainSession, [toSendMsg["To"]], toSendMsg)
        emlData[1][currentSelect] = setReplied(emlData[1][currentSelect])
        MainSession.IMAP.setAnswered(emlData[3][currentSelect])
    curses.reset_prog_mode(); stdscr.clear(); stdscr.refresh()
    return emlData

# This function contructs the Reply Message MIME according to RFC 3501.
def constructReply(MainSession, msgCodec):
    curses.curs_set(1)
    newMsg = MIMEMultipart("alternative")
    newMsg["Message-ID"] = email.utils.make_msgid()
    newMsg["In-Reply-To"] = newMsg["References"] = msgCodec["Message-ID"]
    newMsg["Subject"] = "Re: " + msgCodec["Subject"]
    newMsg["To"] = msgCodec["Reply-To"] or msgCodec["From"]
    newMsg["From"] = MainSession.Email_Addr
    print "From: " + newMsg["From"]
    print "To: " + ",".join([newMsg["To"]])
    print "Subject: " + newMsg["Subject"]
    newText = getEmailText()    # Gain the main text of email.
    originalText = ("> " + processCodec(msgCodec)).replace("\n","\n> ") 
    transitionText = "\n\n> On %s, %s wrote:\n" % (msgCodec["Date"],
            msgCodec["From"])
    newMsg.attach(MIMEText(newText + transitionText + originalText, "plain"))
    curses.curs_set(0)
    return newMsg

# This function deals with Quit/Scrolling events in Email View Mode.
def respondGeneral(flag, event, currentSelect, currentTop, maxY, msgNOs):
    if event == ord('q') or event == ord('Q'): flag = False
    elif event == curses.KEY_UP:
        if currentSelect - currentTop > 0:   currentSelect -= 1
        elif currentTop > 0:    currentTop -= 1; currentSelect -= 1
    elif event == curses.KEY_DOWN:
        if currentSelect < currentTop + maxY - 6: currentSelect += 1
        elif (len(msgNOs) > currentSelect + 1):
            currentTop += (maxY - 6); currentSelect += 1
    elif event == curses.KEY_PPAGE: # PageUp
        if currentTop == 0: currentSelect = 0
        else:
            newTop = max(currentTop - maxY / 2, 0)
            currentSelect -= currentTop - newTop; currentTop = newTop
    elif event == curses.KEY_NPAGE: # PageDn
        if currentTop + maxY - 5 >= len(msgNOs): currentSelect = len(msgNOs)
        else:
            newTop = min(currentTop + maxY / 2, len(msgNOs) - 1)
            currentSelect += newTop - currentTop; currentTop = newTop
    return (flag, event, currentSelect, currentTop, maxY, msgNOs)

# This function draws the list of emails. Selected email is highlighted.
def drawList(MainSession, stdscr, emlData, currentTop, currentSelect):
    maxY, maxX = stdscr.getmaxyx()
    for i in xrange(0, maxY - 5):
        if i != currentSelect - currentTop:
            fontStyle = curses.A_NORMAL
        else:
            fontStyle = curses.A_REVERSE
        stdscr.addstr(min(maxY - 1, i + 2), 1, getInfoStr(MainSession,
            emlData, currentTop+i, maxX - 2), fontStyle)

# This function gathers an email's basic info from its Header.
def getInfoStr(MainSession, emlData, currentIndex, strLen):
    emlHeader, emlFlg, emlSize, toDisplayNOs = emlData
    maxDigit = digitNo(len(emlFlg) + 1)
    if currentIndex >= len(emlData[0]): return "~"
    currentEml = (emlHeader[currentIndex], emlFlg[currentIndex],
            emlSize[currentIndex])
    emlString, emlFlg = [" "] * 4, currentEml[1].lower()
    if emlFlg.find("flagged") != -1:    emlString[1] ="F"
    if emlFlg.find("seen") == -1:       emlString[0] = "N"
    if emlFlg.find("answered") != -1:   emlString[2] = "R"
    emlString = "".join(emlString)
    emlString += (" " * (maxDigit - digitNo(currentIndex + 1)) +
            str(currentIndex + 1) + " " +
            convertDate(currentEml[0]["Date"]) + "   " +
            strSpan(decodeHeader(displayEml(currentEml[0]["From"])),
                (strLen-21-maxDigit)/3) + " " +
            sizeString(currentEml[2]) + " " + 
            strSpan(decodeHeader(currentEml[0]["Subject"]).replace('\n', '')\
                    .replace('\r', ''), strLen))
    return "".join(emlString)[:strLen]

#     This function, by using the self-defined, extended IMAP class
# (MailBoxIMAP), retrieve the info needed to display message list
# (Size, Title, Sender, Date).
def fetchList(MainSession, msgNOs, stdscr):
    maxY, maxX = stdscr.getmaxyx()
    toDisplayNOs = list(reversed(msgNOs))
    emlHeader = [None] * len(toDisplayNOs)
    emlFlg = [None] * len(toDisplayNOs)
    emlSize = [None] * len(toDisplayNOs)
    for msgIndex in xrange(len(toDisplayNOs)):
        emlHeader[msgIndex]=MainSession.IMAP.fetchMsg(toDisplayNOs[msgIndex],
                "PREVIEW")[1][0][1]
        emlHeader[msgIndex] = Parser().parsestr(emlHeader[msgIndex])
        emlFlg[msgIndex] = MainSession.IMAP.fetchMsg(toDisplayNOs[msgIndex],
                "FLAG")[1][0]
        emlSize[msgIndex] = MainSession.IMAP.fetchMsg(toDisplayNOs[msgIndex],
                "SIZE")[1][0][:-1].split()[-1]
    return (emlHeader, emlFlg, emlSize, toDisplayNOs)

# Controlling the prompt to obtain the Source Folder for searching.
def getSourceFolder(MainSession):
    SourceFolder = raw_input(SEARCH_SOURCE_INTRO)
    while True:
        if SourceFolder == "#q#":   return
        if SourceFolder == "#f#":   print CRITERIA_ERR
        if SourceFolder == "":
            SourceFolder = MainSession.IMAP.getInboxFolder()
            break
        elif SourceFolder in MainSession.IMAP.getFolderList():     break
        elif SourceFolder == "#l#":
            print SEARCH_PSB_FDR % MainSession.IMAP.getFolderList()
            print
        else: print FOLDER_NOT_FND,
        SourceFolder = raw_input(SEARCH_FDR_INTRO)
    print
    return SourceFolder

# Obtain searching details from user.
def getSearchInfo(flag):
    keyWrd = ["sender", "receiver", "subject", "text"]
    if flag < 2:
        EmailInfo = raw_input(SEARCH_PROMPT % keyWrd[flag])
    else:
        EmailInfo = raw_input(SEARCH_PROMPT1 % keyWrd[flag])
    if EmailInfo == "#q#":  return None
    elif EmailInfo == "#f#":    return True
    else:
        print
        return EmailInfo


