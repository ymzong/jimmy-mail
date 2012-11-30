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
IMAP_USERNAME_PROMPT = "Username for IMAP server (press ENTER to use default: %s): "
IMAP_PASSWORD_PROMPT = "Password for IMAP server: "
SMTP_USERNAME_PROMPT = "Username for SMTP server (press ENTER to reuse IMAP username): "
SMTP_PASSWORD_PROMPT = "Password for SMTP server (press ENTER to reuse IMAP password): "

RETRY_PROMPT = "Bad username/password. Try again?"
CREDENTIAL_INVALID = "Invalid user credentials. Please check and try again."
MAX_TRY = 3
LOGIN_SUCCESS = "Login success as %s@%s!\n"
CONNECTION_ERR = ("Error occured while establishing connection with the server.\n" +
        "The program will now exit.")
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
                "Smart-Mode: input any human command you want and see if we understand!",
                "q/quit: Exit Jimmy-Mail  |  h/help/?: Display this help again", ""]

PLEASE_WAIT = "Loading email headers, please wait..."
