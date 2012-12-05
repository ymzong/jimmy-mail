# mailbox.py
# Yiming Zong - Carnegie Mellon University '16
# yzong (at) cmu.edu
# ---------------------------------------------------------------
#     This files contains the fundamental definition of the class
# MailSession, MailBoxIMAP, MailBoxSMTP and their methods that are
# used throughout the program. Please DO NOT change this file for
# any reason as this can easily cause the program to malfunction.

import sys
import imaplib
import smtplib
import getpass
from appdata import *
from misc import parseListResponse

# MailSession is the whole Mail Object that our program operates on.
class MailSession(object):
    # Start validating and gaining user credentials.
    def __init__(self, Email_Addr):
        self.Email_Addr = Email_Addr
        self.Domain = Email_Addr[Email_Addr.index("@") + 1:]
        self.Username = Email_Addr[:Email_Addr.index("@")]
        IMAPAddr = "imap." + self.Domain
        IMAPAddr = raw_input(IMAP_PROMPT % IMAPAddr) or IMAPAddr
        self.IMAP = MailBoxIMAP(IMAPAddr, self.Username)
        self.Username = self.IMAP.Username
        self.Password = self.IMAP.Password
        self.SentFolderName = None
        self.InboxName = None
        SMTPAddr = "smtp." + self.Domain
        SMTPAddr = raw_input(SMTP_PROMPT % SMTPAddr) or SMTPAddr
        self.SMTP = MailBoxSMTP(SMTPAddr, self.Username, self.Password)
        print INIT_COMPLETE
    
    # Wrapper for closing connections.
    def close(self):
        self.IMAP.close()
        self.SMTP.close()

#     MailBoxIMAP is the IMAP part of MailSession, which extends Python's
# native imaplib library.
class MailBoxIMAP(object):
    def __init__(self, serv_name, defaultUser):
        try: self.session = imaplib.IMAP4_SSL(serv_name)
        except: print CONNECTION_ERR; sys.exit(THANK_YOU_MSG)
        self.Server = serv_name
        (Login_Success, Login_Try) = (False, 0)
        while (not Login_Success) and (Login_Try < MAX_TRY):
            if Login_Try > 0: print RETRY_PROMPT
            self.Username = raw_input(IMAP_USERNAME_PROMPT %
                    defaultUser) or defaultUser
            self.Password = getpass.getpass(IMAP_PASSWORD_PROMPT)
            try: self.session.login(self.Username, self.Password)
            except: Login_Try += 1
            else: Login_Success = True
        if Login_Success == True:
            self.session.select()
            print LOGIN_SUCCESS % (self.Username, self.Server)
        else:
            print CREDENTIAL_INVALID
            self.session.logout()
            sys.exit(THANK_YOU_MSG)
    
    # This function Flag/Unflag a given message.
    def setFlagged(self, msgNo, msgStatus):
        if msgStatus.find("\\Flagged") != -1:
            newFlag = msgStatus.replace("\\Flagged","")
            self.session.store(str(msgNo), '-FLAGS', '\\Flagged')
        else:
            newFlag = msgStatus + "\\Flagged"
            self.session.store(str(msgNo), "+FLAGS", "\\Flagged")
        return newFlag
    
    # This function "moves" an email to Trash folder. (Realistically, it
    # is done by first copying to Trash then purging the original copy.)
    def setDelete(self, msgNo, emlData):
        try:
            self.session.copy(str(msgNo), self.getTrashFolder())
        except Exception: return False
        else: return True

    # This function sets the property of a locally stored mail to Deleted.
    def setPurge(self, msgNo):
        self.session.store(str(msgNo), "+FLAGS", "\\Deleted")
        self.session.expunge()
    
    # This function sets the property of a locally stored mail to Answered.
    def setAnswered(self, msgNo):
        self.session.store(str(msgNo), "+FLAGS", "\\Answered")

    # This function searches for the INBOX folder of a given IMAP instance.
    def getInboxFolder(self):
        FolderList = self.session.list()[1]
        for folder in FolderList:
            if parseListResponse(folder.lower())[2] == "inbox":
                return parseListResponse(folder)[2]
    
    # This function obtains the full folder list of a given IMAP instance.
    def getFolderList(self):
        result = list()
        if self.Server == "imap.andrew.cmu.edu":    # For CMU campus mail.
            for folder in self.session.list()[1]:
                if parseListResponse(folder)[2].lower()[:5] == "inbox":
                    result.append(parseListResponse(folder)[2])
        else:
            for folder in self.session.list()[1]:
                result.append(parseListResponse(folder)[2])
        return result

    # This function obtains the Sent Folder of a given IMAP instance.
    def getSentFolder(self):
        sentFolders = list()
        if self.Server == "imap.andrew.cmu.edu":    # For CMU campus mail.
            FolderList = self.session.list("INBOX")[1]
        else:
            FolderList = self.session.list()[1]
        for folder in FolderList:
            if parseListResponse(folder.lower())[2].find("sent") != -1:
                sentFolders.append(parseListResponse(folder)[2])
        return sentFolders

    # This function obtains the Trash Folder of a given IMAP instance.
    # (Special treatment is given to Gmail because its 'Trash' is done by
    #  moving to 'All Mails'.)
    def getTrashFolder(self):
        trashFolder = ""
        if self.Server == "imap.andrew.cmu.edu":
            FolderList = self.session.list("INBOX")[1]
            isGoogle = False
        elif self.Server in ["imap.gmail.com", "imap.googlemail.com"]:
            FolderList = self.session.list("")[1]
            isGoogle = True
        else:
            FolderList = self.session.list("")[1]
            isGoogle = False
        for folder in FolderList:
            if not isGoogle:
                if (folder.lower().find("trash") != -1 or 
                        folder.lower().find("deleted") != -1):
                    return parseListResponse(folder)[2]
            # This case is for gmail only.
            elif folder.lower().find("\\all") != -1:
                return parseListResponse(folder)[2]

    # This function obtains the Sent Folder for a give IMAP instance.
    # (Special treatment is given to CMU Cyrus Mail due to its special
    #  mail structure.)
    def setSentFolder(self):
        selections = self.getSentFolder()
        if len(selections) == 0:
            return ""
        elif len(selections) == 1:
            return selections[0]
        else:
            while len(selections) > 0:
                currentChoice = selections.pop()
                while True:
                    choice = raw_input(SND_FDR_CONF % currentChoice)
                    if choice == "y":
                        return currentChoice
                    elif choice == "n":
                        break
                    else:
                        print Y_OR_N
        return ""
    
    # This function fetches designated part of a given message.
    def fetchMsg(self, msgID, arg = "ALL"):
        if arg == "PREVIEW":
            return self.session.fetch(str(msgID), "(BODY.PEEK[HEADER] FLAGS)")
        elif arg == "FLAG":
            return self.session.fetch(str(msgID), "FLAGS")
        elif arg == "SIZE":
            return self.session.fetch(str(msgID), "RFC822.SIZE")
        elif arg == "ALL":
            return self.session.fetch(str(msgID), "(RFC822)")

    # THis function obtains the number of messages in a given folder.
    def getMsgCount(self):
        msgStr = self.session.search(None, "ALL")[1][0]
        if len(msgStr) == 0:
            return 0
        else:
            msgList = msgStr.split(" ")
            return int(msgList[-1])
    
    # Close connection for IMAP.
    def close(self):
        try:
            self.session.close()
            self.session.logout()
        except Exception: pass

#     MailBoxSMTP is the SMTP part of MailSession, which extends Python's
# native smtplib library.
class MailBoxSMTP(object):
    # Initial authentication and log in.
    def __init__(self, serv_name, defUsr, defPwd):
        try: self.session = smtplib.SMTP_SSL(serv_name, 465)
        except: print CONNECTION_ERR; sys.exit(THANK_YOU_MSG)
        self.session.connect(serv_name)
        self.Server = serv_name
        (Login_Success, Login_Try) = (False, 0)
        while (not Login_Success) and (Login_Try < MAX_TRY):
            if Login_Try > 0: print RETRY_PROMPT
            self.Username = raw_input(SMTP_USERNAME_PROMPT) or defUsr
            self.Password = getpass.getpass(SMTP_PASSWORD_PROMPT) or defPwd
            try:
                self.session.login(self.Username, self.Password)
            except: Login_Try += 1
            else: Login_Success = True
        if Login_Success == True:
            print LOGIN_SUCCESS % (self.Username, serv_name)
        else:
            print CREDENTIAL_INVALID
            self.session.quit()
            sys.exit(THANK_YOU_MSG)
    
    # Close the connection for SMTP.
    def close(self):
        try: self.session.quit()
        except Exception: pass
