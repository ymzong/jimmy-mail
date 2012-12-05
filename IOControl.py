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
        stdscr.addstr(min(topMargin + i, maxY - 1), max((maxX - 
            len(WELCOME_MSG[i])) / 2, 0),WELCOME_MSG[i])

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

def processEmlTo(MainSession, EmailTo):
    if EmailTo == None: return False
    ToDisplay =  "-"*10 + "\n"+"|From: "+MainSession.Email_Addr+"\n|To: "
    for i in xrange(len(EmailTo) - 1):  ToDisplay += EmailTo[i] + "; "
    ToDisplay += EmailTo[len(EmailTo) - 1]
    print ToDisplay
    return True

def processEmlTitle(EmailTitle):
    if EmailTitle.lower() == "#q#": return False
    while True:
        if len(EmailTitle) == 0:
            tmp = raw_input(NO_TITLE_CONF)
            if tmp == "y": break
            else: EmailTitle = raw_input("|Subject: ")
        else:   break
    return EmailTitle

def confirmDraft(MainSession, EmailTo, EmailMIME):
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
        else:   choice = raw_input(Y_OR_N)

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

def displayResult(MainSession, searchStr, stdscr):
    try:    msgIDs = MainSession.IMAP.session.search(None, searchStr)[1][0]
    except Exception as err: print SEARCH_ERR % err
    else:
        if msgIDs == "":
            print SEARCH_EMPTY
            return
        else:
            msgNOs = [int(num) for num in msgIDs.split(" ")]
            raw_input(SEARCH_RESULT)
            emailLister(MainSession, msgNOs, stdscr)

# Entries Per Page: MaxY - 5
def emailLister(MainSession, msgNOs, stdscr):
    curses.def_shell_mode(); curses.reset_prog_mode()    # Back to curses
    curses.curs_set(0); stdscr.clear(); stdscr.refresh()
    maxY, maxX = stdscr.getmaxyx(); stdscr.clear(); stdscr.box()
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
        event = stdscr.getch();
        (flag, event, currentSelect, currentTop, maxY, msgNOs, emlData) = emailListResponder(event, MainSession, emlData, currentSelect, currentTop, maxY, msgNOs, flag, stdscr)
    stdscr.clear(); stdscr.refresh()
    curses.reset_shell_mode(); curses.curs_set(1)


def emailListResponder(event, MainSession, emlData, currentSelect, currentTop, maxY, msgNOs, flag, stdscr):
    if event in [ord('q'),ord('Q'),curses.KEY_UP,curses.KEY_DOWN,curses.KEY_PPAGE,curses.KEY_NPAGE]:
        (flag, event, currentSelect, currentTop, maxY, msgNOs) =\
          respondGeneral(flag,event,currentSelect,currentTop,maxY,msgNOs)
    elif event in [ord("D"), ord("r"), ord("R"), ord("F"), ord("f")]:
        (emlData, msgNOs) = modifyEml(MainSession, emlData, msgNOs, currentSelect, event, stdscr)
    elif event in [ord(" "), 10, 13, ord("\n"), curses.KEY_ENTER]:
        try:
            emlData[1][currentSelect] = setRead(emlData[1][currentSelect])
            viewEmail(MainSession, emlData, msgNOs, currentSelect, stdscr)
        except Exception: pass
    curses.napms(50)        # Anti-flashing
    return (flag, event, currentSelect, currentTop, maxY, msgNOs, emlData)

def setRead(inFlags):
    if inFlags.find("\\Seen") == -1:
        inFlags += "\\Seen"
    return inFlags

def processCodec(msgCodec):
    txtMsg = None
    for part in msgCodec.walk():
        if part.get_content_type() == "text/plain":
            txtMsg = part.get_payload().replace("\r","").\
                    replace("\n\n","\n")
            break
    if txtMsg == None:  # If no plain text available, use html version.
        for part in msgCodec.walk():
            if part.get_content_type() == "text/html":
                try: txtMsg = FROM_HTML+html2text(part.get_payload())+EOM
                except Exception: txtMsg = ERR_PARSING
                else:break
    if txtMsg == None:  # No Text and HTML, show error.
        txtMsg = NO_TXT_AVAIL
    return txtMsg

def viewEmail(MainSession, emlData, msgNOs, currentSelect, stdscr):
    curses.def_prog_mode();curses.curs_set(0);stdscr.clear();stdscr.refresh()
    maxY, maxX = stdscr.getmaxyx(); stdscr.box()
    stdscr.addstr(0,max(0,(maxX-len(JIMMY_MAIL))/2),JIMMY_MAIL)
    stdscr.addstr(min(2,maxY-1),max(0,(maxX-len(PLEASE_WAIT))/2),
            PLEASE_WAIT)
    stdscr.refresh();
    msgCodec = Proc(MainSession.IMAP.fetchMsg(\
            emlData[3][currentSelect])[1][0][1])
    txtMsg = processCodec(msgCodec) + EOM;
    (flag,event,currentTop)=(True, None, 0)
    while flag:
        maxY, maxX = stdscr.getmaxyx(); stdscr.clear(); stdscr.box()
        stdscr.addstr(0,max(0,(maxX-len(JIMMY_MAIL))/2),JIMMY_MAIL);
        stdscr.refresh(); coord = (6, 1, maxY - 4, maxX - 1) 
        maxLen = len(txtMsg) / (maxX - 2) + txtMsg.count("\n") + 1 
        pad = curses.newpad(maxLen, maxX - 2)
        pad.clear(); pad.refresh(currentTop,0,*coord)
        drawBasicInfo(MainSession, emlData, currentSelect, stdscr)
        try: pad.addstr(0,0, txtMsg); pad.refresh(currentTop, 0, *coord)
        except: pass
        event = stdscr.getch()      # Get Keyboard Inputs
        if event in [ord('q'),ord('Q'),curses.KEY_UP,curses.KEY_DOWN,curses.KEY_PPAGE,curses.KEY_NPAGE]:
            (flag,currentTop)=respondMsgPg(flag,event,currentTop,maxY,maxLen)
        elif event in [ord("D"), ord("r"), ord("R"), ord("F"), ord("f")]:
            (emlData, msgNOs) = modifyEml(MainSession, emlData, msgNOs, currentSelect, event, stdscr)
            if event == ord("D"): flag = False   # Quit Email Viewing

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
    stdscr.addstr(2,1,"From: " + currentEml[0]["From"][:maxX - 2])
    stdscr.addstr(3,1,"To: " + (currentEml[0]["To"].replace("\r","").\
            replace("\n", "")[:maxX - 6] or UNDISCLOSED_RCP))
    stdscr.addstr(4,1,"Subject: " + currentEml[0]["Subject"].\
            replace("\r","").replace("\n", "")[:maxX - 11] or NO_TITLE)
    stdscr.addstr(5,1,"*"*(2 * maxX / 3))

def drawInstruction(MainSession, stdscr):
    for i in xrange(len(INSTRUCT1)):
        maxY, maxX = stdscr.getmaxyx()
        stdscr.addstr(max(maxY-len(INSTRUCT1)+i-1, 0),
                max((maxX - len(INSTRUCT1[i])) / 2, 0),INSTRUCT1[i])

def modifyEml(MainSession, emlData, msgNOs, currentSelect, event, stdscr):
    if event == ord("f") or event == ord("F"):
        emlData[1][currentSelect] = MainSession.IMAP.setFlagged(\
                emlData[3][currentSelect], emlData[1][currentSelect])
    elif event == ord("D"):
        originalMsgNo = emlData[3][currentSelect]
        succeed = MainSession.IMAP.setDelete(originalMsgNo, emlData)
        if succeed == True:
            msgNOs.pop(currentSelect)
            for part in emlData:  part.pop(currentSelect)
            MainSession.IMAP.setPurge(originalMsgNo)
    elif event == ord("R") or event == ord("r"):
        curses.def_prog_mode(); stdscr.clear(); stdscr.refresh()
        curses.reset_shell_mode(); print PROC_ORIGINAL
        msgCodec = Proc(MainSession.IMAP.fetchMsg(\
                emlData[3][currentSelect])[1][0][1])
        toSendMsg = constructReply(MainSession, msgCodec)
        try: MainSession.SMTP.session.sendmail(toSendMsg["From"], 
                toSendMsg["To"], toSendMsg.as_string())
        except Exception as err: print SEND_ERR % err
        else: confirmDraft(MainSession, toSendMsg["To"], toSendMsg)
        curses.reset_prog_mode(); stdscr.clear(); stdscr.refresh()
    return emlData, msgNOs

def constructReply(MainSession, msgCodec):
    curses.curs_set(1)
    newMsg = MIMEMultipart("alternative")
    newMsg["Message-ID"] = email.utils.make_msgid()
    newMsg["In-Reply-To"] = newMsg["References"] = msgCodec["Message-ID"]
    newMsg["Subject"] = "Re: " + msgCodec["Subject"]
    newMsg["To"] = msgCodec["Reply-To"] or msgCodec["From"]
    newMsg["From"] = MainSession.Email_Addr
    print "From: " + newMsg["From"]
    print "To: " + newMsg["To"]
    print "Subject: " + newMsg["Subject"]
    newText = getEmailText()
    originalText = ("> " + processCodec(msgCodec)).replace("\n","\n> ") 
    transitionText = "\n\n> On %s, %s wrote:\n" % (msgCodec["Date"],
            msgCodec["From"])
    newMsg.attach(MIMEText(newText + transitionText + originalText, "plain"))
    curses.curs_set(0)
    return newMsg

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
            strSpan(decodeHeader(currentEml[0]["Subject"]).replace('\n', '')\
                    .replace('\r', ''), strLen))
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
