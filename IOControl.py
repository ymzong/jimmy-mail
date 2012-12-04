import time
import curses
import curses.textpad
import sys
from appdata import *
from misc import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.parser import Parser
from email.header import decode_header as Decode
import email.utils
from email import message_from_string as Proc
import imaplib
import locale
locale.setlocale(locale.LC_ALL,"en_US.UTF-8")
from html2text import html2text

############################# KEY RESPOND UNIT #########################
keyResponse = dict()
keyResponse["WELCOME"] = [10, ord("q")]   # Enter
keyResponse["MAIN_MENU"] = [ord("0"), ord("1"), ord("2"), ord("3"),
                            ord("s"), ord("o"), ord("h"), ord("q")]

def keyRespond(stdscr, MainSession, Appdata, event):
    if Appdata.mode[0] == "WELCOME":
        respondWelcome(stdscr, MainSession, Appdata, event)
    if Appdata.mode[0] == "MAIN_MENU":
        respondMainMenu(stdscr, MainSession, Appdata, event)

def exitApp(stdscr):
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo
    curses.endwin()
    sys.exit(THANK_YOU_MSG)

def respondWelcome(stdscr, MainSession, Appdata, event):
    if event == ord("q"):
        exitApp(stdscr)
    elif event == 10:
        Appdata.mode = ("MAIN_MENU", None)

def respondMainMenu(stdscr, MainSession, Appdata, event):
    if event == ord("s") or event == ord("0"):
        smartCommand(stdscr, MainSession, Appdata, event)
    if event == ord("q") or event == ord("2"):
        exitApp(stdscr)

############################# DRAW SCREEN UNIT #########################
def drawScr(stdscr, MainSession, Appdata):
    if Appdata.mode[0] == "WELCOME":
        drawScrWelcome(stdscr)
    elif Appdata.mode[0] == "MAIN_MENU":
        drawScrMainMenu(stdscr, MainSession)

def drawScrWelcome(stdscr):
    (maxY, maxX) = stdscr.getmaxyx()
    topMargin = max((maxY - 5) / 2, 1)
    for i in xrange(6):
        stdscr.addstr(min(topMargin + i, maxY - 1), max((maxX - len(WELCOME_MSG[i])) / 2, 0),WELCOME_MSG[i])

def smartCommand(stdscr, MainSession, Appdata, event):
    (maxY,maxX) = stdscr.getmaxyx()
    curses.raw()
    curses.cbreak()
    curses.curs_set(1)
    curses.setsyx(0,0)
    stdscr.erase()
    stdscr.refresh()
    curses.reset_shell_mode()
    for instruction in INSTRUCTIONS:
        print ("{0:^" + str(maxX) + "}").format(instruction)
    command = raw_input(">> ")
    while True:
        if command.lower() in ("quit", "q", "exit"):
            break
        elif command.lower() in ("help", "h", "?", "h"):
            for i in xrange(1, len(INSTRUCTIONS)):
                print ("{0:^" + str(maxX) + "}").format(INSTRUCTIONS[i])
        elif command.lower() in ("i", "inbox", "ls"):
            displayInbox(MainSession, stdscr)
        elif command.lower() in ("search", "find", "f"):
            searchMailApp(MainSession, stdscr)
        elif command.lower() in ("n", "new", "newmail"):
            sendMailApp(MainSession)
        elif command != "":
            print "Processing Smart-Mode... Done!"
        command = raw_input(">> ")
    exitApp(stdscr)

def displayInbox(MainSession, stdscr):
    try: MainSession.IMAP.session.select(MainSession.IMAP.getInboxFolder())
    except Exception as err: print "Error occured when reading Inbox folder", err
    else:
        if MainSession.IMAP.getMsgCount() == 0:
            print "The Inbox is empty!"
        else:
            emailLister(MainSession, [int(msgNoStr) for msgNoStr in MainSession.IMAP.session.search(None, "ALL")[1][0].split(" ")], stdscr)

def getEmailTo():
    EmailTo = list()
    CurrentEmail = raw_input("|To: ")
    while (CurrentEmail != "") or (len(EmailTo) == 0):
        if CurrentEmail.lower() == "#q#":
            return
        elif len(EmailTo) == 0 and (CurrentEmail == ""):
            print "     You must enter at least one recipient to proceed!"
            print "     Enter '#q#' at any time to quit sending email."
        elif isValidEmail(CurrentEmail):
            EmailTo.append(CurrentEmail)
        else:
            print "     Invalid Email! Please check and enter again."
        CurrentEmail = raw_input("|To: ")
    return EmailTo


def getEmailText():
    print "|Email Text: (Enter ONLY '#end#' on one line to terminate the message)\n"
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

def sendMailApp(MainSession):
    curses.curs_set(1)                      # show the cursor
    print "Please enter ONE email per line. Press ENTER to a recipient category to finish."
    print "|From: " + MainSession.Email_Addr
    EmailTo = getEmailTo()
    if EmailTo == None: return
    ToDisplay =  "-" * 10 + "\n"
    ToDisplay += "|From: " + MainSession.Email_Addr + "\n|To: "
    for i in xrange(len(EmailTo) - 1):
        ToDisplay += EmailTo[i] + "; "
    ToDisplay += EmailTo[len(EmailTo) - 1]
    print ToDisplay
    EmailTitle = raw_input("|Subject: ")
    if EmailTitle.lower() == "#q#": return
    while True:
        if len(EmailTitle) == 0:
            tmp = raw_input("        Really compose email with NO title? (y/n)")
            if tmp == "y": break
            else: EmailTitle = raw_input("|Subject: ")
        else:   break
    EmailText = getEmailText()
    if EmailText == None: curses.curs_set(0); return
    EmailMIME = MIMEText(EmailText)
    EmailMIME["From"] = MainSession.Email_Addr
    EmailMIME["To"] = ";".join(EmailTo)
    EmailMIME["Subject"] = EmailTitle
    try: MainSession.SMTP.session.sendmail(MainSession.Email_Addr, EmailTo, EmailMIME.as_string())
    except Exception as err: print "An error occured during sending.", err
    else:
        choice = raw_input("\nEmail Sent to " + ",".join(EmailTo) + "! Save a copy to Sent Folder? (y/n)")
        while True:
            if choice == "y":
                if MainSession.SentFolderName == None:
                    MainSession.SentFolderName = MainSession.IMAP.setSentFolder()
                if MainSession.SentFolderName == "":
                    print "No Sent Mail folder found. Sorry for the inconvenience."
                else:
                    try: MainSession.IMAP.session.append(MainSession.SentFolderName, "(\\Seen)", imaplib.Time2Internaldate(time.time()), EmailMIME.as_string())
                    except Exception: "Error occured when saving to folder: " + MainSession.SentFolderName + "."
                    else: print "Message saved to folder: " + MainSession.SentFolderName + "."
                break
            elif choice == "n":
                break
            else:
                choice = raw_input("Please ONLY enter \"y\" or \"n\":")

def drawScrMainMenu(stdscr, MainSession):
    (maxY, maxX) = stdscr.getmaxyx()
    InitStr = LOGGED_IN_AS + MainSession.Email_Addr
    stdscr.addstr(0, max((maxX - len(JIMMY_MAIL)) / 2, 0), JIMMY_MAIL)
    stdscr.addstr(1, max((maxX - len(InitStr)) / 2, 0), InitStr)
    menuItems = len(MENU_ENTRIES)
    if maxY > 2 * menuItems + 2:
        topMargin = (maxY - menuItems * 2 - 3) / 2
        for i in xrange(menuItems):
            stdscr.addstr(min(topMargin + 2 * i + 2, maxY - 2), max((maxX - len(MENU_ENTRIES[i])) / 2, 0), MENU_ENTRIES[i])
    else:
        topMargin = max((maxY - menuItems - 3) / 2 + 2, 2)
        for i in xrange(menuItems):
            stdscr.addstr(min(topMargin + i, maxY - 2), max((maxX - len(MENU_ENTRIES[i])) / 2, 0), MENU_ENTRIES[i])


def searchMailApp(MainSession, stdscr):
    curses.curs_set(1)
    print "Please enter searching criteria as follows."
    print "Press ENTER to skip the option."
    print "Enter \"#q#\" to quit to Smart Command-Line mode."
    print "Enter \"#f#\" to perform searching with existing criteria."
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

def performSearch(MainSession, sCriteria, stdscr):
    try: MainSession.IMAP.session.select(sCriteria[0])
    except: 
        print "Sorry, network error while browsing the email directory."
        return
    else:
        searchStr, existing = "(", 0
        for item in sCriteria:
            if (item != "") and (item != True):  existing += 1
        if existing <= 1:
            print "Sorry, search criteria not enough."
            return
        else:
            keyWd = ["", "FROM", "TO", "SUBJECT", "TEXT"]
            for i in xrange(1, 5):
                if sCriteria[i] == True: break
                elif sCriteria[i] != "":
                    searchStr += keyWd[i] + " \"" + sCriteria[i] + "\" "
            searchStr = searchStr[:-1] + ")"
            displayResult(MainSession, searchStr, stdscr)

def displayResult(MainSession, searchStr, stdscr):
    try:    msgIDs = MainSession.IMAP.session.search(None, searchStr)[1][0]
    except Exception as err: print "Search Error!", err
    else:
        if msgIDs == "":
            print "\nSearch result empty. Please change search criteria and try again.\n"
            return
        else:
            msgNOs = [int(num) for num in msgIDs.split(" ")]
            raw_input("\nPress ENTER to proceed to the search result...")
            emailLister(MainSession, msgNOs, stdscr)

# Entries Per Page: MaxY - 5
def emailLister(MainSession, msgNOs, stdscr):
    curses.def_shell_mode(); curses.reset_prog_mode()    # Back to curses
    curses.curs_set(0); stdscr.clear(); stdscr.refresh()
    maxY, maxX = stdscr.getmaxyx()
    stdscr.clear(); stdscr.box()
    stdscr.addstr(0, max(0, (maxX - len(JIMMY_MAIL)) / 2), JIMMY_MAIL)
    stdscr.addstr(min(2,maxY-1),max(0,(maxX-len(PLEASE_WAIT))/2),PLEASE_WAIT)
    stdscr.refresh()
    emlData = fetchList(MainSession, msgNOs, stdscr)
    (maxDigit,flag,event,currentTop,currentSelect)=(digitNo(len(msgNOs)),
            True, None, 0, 0)
    while flag:
        maxY, maxX = stdscr.getmaxyx(); stdscr.clear(); stdscr.box()
        stdscr.addstr(0, max(0, (maxX - len(JIMMY_MAIL)) / 2), JIMMY_MAIL)
        drawList(MainSession, stdscr, emlData, currentTop, currentSelect)
        drawInstruction(MainSession, stdscr)
        event = stdscr.getch()
        if event in [ord('q'),ord('Q'),curses.KEY_UP,curses.KEY_DOWN,curses.KEY_PPAGE,curses.KEY_NPAGE]:
            (flag, event, currentSelect, currentTop, maxY, msgNOs) =\
              respondGeneral(flag,event,currentSelect,currentTop,maxY,msgNOs)
        elif event in [ord("D"), ord("r"), ord("R"), ord("F"), ord("f")]:
            (emlData, msgNOs) = modifyEml(MainSession, emlData, msgNOs, currentSelect, event)
        elif event in [ord(" "), 10, 13, ord("\n"), curses.KEY_ENTER]:
            try:
                emlData[1][currentSelect] = setRead(emlData[1][currentSelect])
                viewEmail(MainSession, emlData, msgNOs, currentSelect, stdscr)
            except Exception: pass
    stdscr.clear(); stdscr.refresh()
    curses.reset_shell_mode(); curses.curs_set(1)

def setRead(inFlags):
    if inFlags.find("\\Seen") == -1:
        inFlags += "\\Seen"
    return inFlags

def viewEmail(MainSession, emlData, msgNOs, currentSelect, stdscr):
    curses.def_prog_mode()
    curses.curs_set(0); stdscr.clear(); stdscr.refresh()
    maxY, maxX = stdscr.getmaxyx()
    stdscr.clear(); stdscr.box()
    stdscr.addstr(0, max(0, (maxX - len(JIMMY_MAIL)) / 2), JIMMY_MAIL)
    stdscr.addstr(min(2,maxY-1),max(0,(maxX-len(PLEASE_WAIT))/2),PLEASE_WAIT)
    stdscr.refresh(); txtMsg = None
    msgCodec = Proc(MainSession.IMAP.fetchMsg(emlData[3][currentSelect])[1][0][1])
    for part in msgCodec.walk():
        if part.get_content_type() == "text/plain": txtMsg = part.get_payload().replace("\r","") + EOM
    if txtMsg == None: txtMsg = html2text(list(msgCodec.walk())[0].get_payload())
    (flag,event,currentTop)=(True, None, 0)
    while flag:
        maxY, maxX = stdscr.getmaxyx()
        stdscr.clear(); stdscr.box()
        stdscr.addstr(0, max(0, (maxX - len(JIMMY_MAIL)) / 2), JIMMY_MAIL)
        stdscr.refresh();
        maxLen = len(txtMsg) / (maxX - 2) + txtMsg.count("\n") + 1 
        coord = (6, 1, maxY - 4, maxX - 1)
        pad = curses.newpad(maxLen, maxX - 2)
        pad.clear(); pad.refresh(currentTop,0,*coord)
        stdscr.addstr(0, max(0, (maxX - len(JIMMY_MAIL)) / 2), JIMMY_MAIL)
        drawBasicInfo(MainSession, emlData, currentSelect, stdscr)
        pad.addstr(0,0, txtMsg)
        try: pad.refresh(currentTop, 0, *coord)
        except: pass
        event = stdscr.getch()      # Get Keyboard Inputs
        if event in [ord('q'),ord('Q'),curses.KEY_UP,curses.KEY_DOWN,curses.KEY_PPAGE,curses.KEY_NPAGE]:
            (flag, currentTop) = respondMsgPg(flag,event,currentTop,maxY,maxLen)
        elif event in [ord("D"), ord("r"), ord("R"), ord("F"), ord("f")]:
            (emlData, msgNOs) = modifyEml(MainSession, emlData, msgNOs, currentSelect, event)
            if event == ord("D"): flag = False   # Quite Email Viewing

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

def drawBasicInfo(MainSession, emlData, currentIndex, stdscr):
    maxY, maxX = stdscr.getmaxyx()
    for i in xrange(len(INSTRUCT_MSG)):
        stdscr.addstr(max(maxY-len(INSTRUCT_MSG)+i-1, 0), 
                max((maxX - len(INSTRUCT_MSG[i])) / 2, 0),INSTRUCT_MSG[i])
    emlHeader, emlFlg, emlSize, toDisplayNOs = emlData
    currentEml = (emlHeader[currentIndex], emlFlg[currentIndex],
            emlSize[currentIndex])
    stdscr.addstr(1,1,"Date: " + currentEml[0]["Date"])
    stdscr.addstr(2,1,"From: " + currentEml[0]["From"])
    stdscr.addstr(3,1,"To: " + currentEml[0]["To"])
    stdscr.addstr(4,1,"Subject: " + currentEml[0]["Subject"])
    stdscr.addstr(5,1,"*"*(maxX/3))

def drawInstruction(MainSession, stdscr):
    for i in xrange(len(INSTRUCT1)):
        maxY, maxX = stdscr.getmaxyx()
        stdscr.addstr(max(maxY-len(INSTRUCT1)+i-1, 0),
                max((maxX - len(INSTRUCT1[i])) / 2, 0),INSTRUCT1[i])

def modifyEml(MainSession, emlData, msgNOs, currentSelect, event):
    if event == ord("f") or event == ord("F"):
        emlData[1][currentSelect] = MainSession.IMAP.setFlagged(emlData[3][currentSelect],
                emlData[1][currentSelect])
    elif event == ord("D"):
        originalMsgNo = emlData[3][currentSelect]
        succeed = MainSession.IMAP.setDelete(originalMsgNo, emlData)
        if succeed == True:
            msgNOs.pop(currentSelect)
            for part in emlData:
                part.pop(currentSelect)
            MainSession.IMAP.setPurge(originalMsgNo)
    return emlData, msgNOs

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
        if currentTop + maxY - 5 >= len(msgNOs):
            currentSelect = len(msgNOs)
        else:
            newTop = min(currentTop + maxY / 2, len(msgNOs) - 1)
            currentSelect += newTop - currentTop; currentTop = newTop
    return (flag, event, currentSelect, currentTop, maxY, msgNOs)

def drawList(MainSession, stdscr, emlData, currentTop, currentSelect):
    maxY, maxX = stdscr.getmaxyx()
    for i in xrange(0, maxY - 5):
        if i != currentSelect - currentTop:
            fontStyle = curses.A_NORMAL
        else:
            fontStyle = curses.A_REVERSE
        stdscr.addstr(min(maxY - 1, i + 2), 1, getInfoStr(MainSession,
            emlData, currentTop+i, maxX - 2), fontStyle)

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
            strSpan(decodeHeader(currentEml[0]["Subject"]).replace('\n', '').replace('\r', ''), strLen))
    return "".join(emlString)[:strLen]

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

# Controlling the prompt to obtain the Folder to search from.
def getSourceFolder(MainSession):
    SourceFolder = raw_input("\nEnter the folder to search from: (press ENTER to search in INBOX; enter \"#l#\" for a list of searchable folders) ")
    while True:
        if SourceFolder == "#q#":   return
        if SourceFolder == "#f#":   print "Search criteria not enough!"
        if SourceFolder == "":
            SourceFolder = MainSession.IMAP.getInboxFolder()
            break
        elif SourceFolder in MainSession.IMAP.getFolderList():     break
        elif SourceFolder == "#l#":
            print "Following are the searchable folders:", MainSession.IMAP.getFolderList()
            print
        else: print "Folder not found.",
        SourceFolder = raw_input("Please enter the folder you want to search from: ")
    print
    return SourceFolder

# Obtain searching details from user.
def getSearchInfo(flag):
    keyWrd = ["sender", "receiver", "subject", "text"]
    if flag < 2:
        EmailInfo = raw_input("Enter the " + keyWrd[flag] + " of email (a part of email or name would suffice): (press ENTER to skip this criteria) ")
    else:
        EmailInfo = raw_input("Please enter any part of the " + keyWrd[flag] + " of email: (press ENTER to skip this criteria)")
    if EmailInfo == "#q#":  return None
    elif EmailInfo == "#f#":    return True
    else:
        print
        return EmailInfo
