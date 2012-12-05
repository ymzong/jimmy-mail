# appdata.py
# Yiming Zong - Carnegie Mellon University '16
# yzong (at) cmu.edu
# -----------------------------------------------------------------------
#     This file contains constant strings that are CRUCIAL to the running
# of program. Please do NOT edit unless you are absolutely sure about what
# are doing.

ARG_USAGE = ("Welcome to use Jimmy-Mail! (Smart enough to discover this " +
             "function!)\nUsage: python main.py" + " " * 21 + "Run Jimmy-" +
             "Mail in Traditional Mode\n" + " " * 7 + "python main.py " + 
             "[Email Address]     " +
             "Attempt to login using the given email address.\n" + " " * 7 +
             "python main.py help" + " " * 16 + "Display this help " + 
             "message again.\n")

THANK_YOU_MSG = "\nThank you for using Jimmy-Mail. :-)"
WELCOME_MSG = [None, None, None, None, None, None]
WELCOME_MSG[0] = "Hello, welcome to use Jimmy-Mail!"
WELCOME_MSG[1] = "All sources are written by Yiming Zong,"
WELCOME_MSG[2] = "Carnegie Mellon University SCS '16."
WELCOME_MSG[3] = "y z o n g @ c m u . e d u"
WELCOME_MSG[4] = " "
WELCOME_MSG[5] = "Press ENTER or SPACE to continue..."

EMAIL_PROMPT = "Please enter your email address: "
EMAIL_INVALID = "Email invalid. Please enter again. (Enter \"q\" to quit)"

IMAP_PROMPT = "Address for IMAP Server (press ENTER to use default: %s): "
SMTP_PROMPT = "Address for SMTP Server (press ENTER to use default: %s): "
IMAP_USERNAME_PROMPT = ("Username for IMAP server (press ENTER to use " + 
                        "default: %s): ")
IMAP_PASSWORD_PROMPT = "Password for IMAP server: "
SMTP_USERNAME_PROMPT = ("Username for SMTP server (press ENTER to reuse " + 
                        "IMAP username): ")
SMTP_PASSWORD_PROMPT = ("Password for SMTP server (press ENTER to reuse " + 
                        "IMAP password): ")

RETRY_PROMPT = "Bad username/password. Try again?"
CREDENTIAL_INVALID = "Invalid user credentials. Please check and try again."
MAX_TRY = 3
LOGIN_SUCCESS = "Login success as %s@%s!\n"
CONNECTION_ERR = ("Error occured while establishing connection with the " +
                  "server.\nThe program will now exit.")
INIT_COMPLETE = "Initialization complete! Now loading main modules..."

WAIT_FOR_ENTER = "\nPress ENTER to continue..."

LOGGED_IN_AS = "Logged in as: "
JIMMY_MAIL = "Jimmy-Mail v0.99"


# Main Menu Items Generator
MENU_ENTRIES = ["SMART-COMMAND", "HELP", "QUIT"]
menuItems = len(MENU_ENTRIES)
for i in xrange(menuItems):
    MENU_ENTRIES[i] = (str(i) + ": [" + MENU_ENTRIES[i][0] +
            "]" + MENU_ENTRIES[i][1:])


INSTRUCTIONS = ["Welcome to use Jimmy-Mail!",
                "Following are the command to control your mailbox:",
                "i/inbox: View Inbox   |   n/new/newmail: New Email",
                "search/find: search for specific emails",
                ("Smart-Mode: input any human command you want and see if we"+
                " understand!"),
                "q/quit: Exit Jimmy-Mail  |  h/help/?: Display this help again"
                , ""]

PLEASE_WAIT = "Loading email headers, please wait..."

INSTRUCT1 = [("Arrow Keys -  Move thru Email List   f - Flag/Unflag Msg   " + 
         "q - Quit Email List"),
             ("SPACE/ENTER - Read Mail   D (CAPITAL D) - Delete Mail   " + 
         "r - Reply Email")]

INSTRUCT_MSG = ["Arrow Keys - Move along Email   f - Flag/Unflag Msg",
                ("D (CAPITAL D) - Delete Mail   r - Reply Email   " +
                "q - Quit to Parent Folder")]
EOM = "### END OF EMAIL TEXT ###"

INBOX_ERR = "Error occured when reading Inbox folder %s"
INBOX_EPT = "The mail folder is empty!"

RECV_EMPTY = "     You must enter at least one recipient to proceed!"
RECV_INVALID = "     Invalid Email! Please check and enter again."

EMLTXT_INTRO = ("|Email Text: (Enter ONLY '#end#' on one line to "
              + "SEND the message)\n")
SEND_INTRO = ("Please enter ONE email per line.\nPress ENTER to a " + 
              "recipient category to finish.\nEnter ONLY '#q#' on any " + 
              "input to DISCARD the message.")
NO_TITLE_CONF = "        Really compose email with NO title? (y/n)"
SEND_ERR = "An error occured during sending. %s"
SAVE_MSG = "\nEmail Sent to %s! Save a copy to Sent Folder? (y/n)"
SND_FDR_NIL = "No Sent Mail folder found. Sorry for the inconvenience."
SAVE_ERR = "Error occured when saving to folder: %s."
SAVE_SUCC = "Message saved to folder: %s."
Y_OR_N = "Please ONLY enter \"y\" or \"n\":"

SEARCH_PMPT = ("Please enter searching criteria as follows.\n" + 
               "Press ENTER to skip the option.\n" +
               "Enter \"#q#\" to quit to Smart Command-Line mode.\n" +
               "Enter \"#f#\" to perform searching with existing criteria.\n")
BROWSE_ERR = "Sorry, network error while browsing the email directory."
CRITERIA_ERR = "Sorry, search criteria not enough."
KEYWD_STR = ["", "FROM", "TO", "SUBJECT", "TEXT"]
SEARCH_ERR = "Search Error! %s"
SEARCH_EMPTY = ("\nSearch result empty. Please change search criteria and " + 
            "try again.\n")
SEARCH_RESULT = "\nPress ENTER to proceed to the search result..."
SEARCH_SOURCE_INTRO = ("\nEnter the folder to search from: (press ENTER to " + 
        "search in INBOX; enter \"#l#\" for a list of searchable folders) ")
SEARCH_PSB_FDR = "Following are the searchable folders: %s"
FOLDER_NOT_FND = "Folder not found."
SEARCH_FDR_INTRO = "Please enter the folder you want to search from: "
SEARCH_PROMPT = ("Enter the %s of email (a part of email or name would " + 
                "suffice): (press ENTER to skip this criteria) ")
SEARCH_PROMPT1 = ("Please enter any part of the %s of email: (press ENTER " +
                    "to skip this criteria)")
NO_TXT_AVAIL = "\n### No Text Available for This Email. ###"
NO_TITLE = "(Untitled Email)"

PROC_ORIGINAL = ("Processing original message, please wait...\n\n" + 
        "Compose Reply Message:")
ERR_PARSING = "\n An error occured when parsing HTML message.\n"
FROM_HTML = "\n (Following text is parsed from HTML message.) \n"
UNDISCLOSED_RCP = "Undisclosed Recipients"

Q_LIST = ["quit", "q", "exit", "x", ":q", "bye"]
H_LIST = ["help", "h", "--help", "?", "??", "help!"]
I_LIST = ["inbox", "i", "mails", "check mail", "check email"]
S_LIST = ["search", "find", "f", "s", "filter"]
N_LIST = ["new", "newmail", "compose", "compose email", "compose mail",
        "n", "nm", "write", "send"]
LFDR_LIST = ["dir", "ls", "folders"]
NOT_UNDSTD = ("Sorry, Jimmy-Bot does not understand your command. Try" +
              " some others maybe? :-)")
EML_INDICATION = ["mails", "mail", "email", "emails", "all mails",
                "all emails", "all messages"]

