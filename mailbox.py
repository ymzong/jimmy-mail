import sys
import imaplib
import smtplib
import getpass
from appdata import *
from misc import parseListResponse

class MailSession(object):
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
    
    def close(self):
        self.IMAP.close()
        self.SMTP.close()

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
            try: 
                self.session.login(self.Username, self.Password)
            except: Login_Try += 1
            else: Login_Success = True
        if Login_Success == True:
            self.session.select()
            print LOGIN_SUCCESS % (self.Username, self.Server)
        else:   print CREDENTIAL_INVALID
    
    def getInboxFolder(self):
        FolderList = self.session.list()[1]
        for folder in FolderList:
            if parseListResponse(folder.lower())[2] == "inbox":
                return parseListResponse(folder)[2]

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
                    choice = raw_input("Is " + currentChoice + " your Sent Mail folder? (y/n)")
                    if choice == "y":
                        return currentChoice
                    elif choice == "n":
                        break
                    else:
                        print "Please enter only \"y\" or \"n\"."
        return ""

    def fetchMsg(self, msgID, arg = "ALL"):
        if arg == "PREVIEW":
            return self.session.fetch(str(msgID), "(BODY.PEEK[HEADER] FLAGS)")
        elif arg == "FLAG":
            return self.session.fetch(str(msgID), "FLAGS")
        elif arg == "ALL":
            return self.session.fetch(str(msgID), "(RFC822)")

    def getMsgCount(self):
        msgStr = self.session.search(None, "ALL")[1][0]
        if len(msgStr) == 0:
            return 0
        else:
            msgList = msgStr.split(" ")
            return int(msgList[-1])

    def close(self):
        self.session.close()
        self.session.logout()

class MailBoxSMTP(object):
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
        else:   print CREDENTIAL_INVALID

    def close(self):
        self.session.quit()
