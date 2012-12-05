Jimmy-Mail v0.99
Yiming Zong
yzong (at) cmu.edu
School of Computer Science
Carnegie Mellon University '16
-------------------------------

1. OVERVIEW:
        This is a console-based email client built on Python's Curses library.
    Basic functions such as mail retrieval, email reply, Flag/Unflag, and
    email search are supported. Furthermore, this program features a
    simplistic robot that can understand human commands such as 'list folders'
    (mailbox viewing is triggered) and 'all emails from Kevin about basketball'
    (email searching is triggered). More functions will be added in the
    future, including more customizable options and better human-language
    understanding capability.

2. DESIGN IDEAS:
        Because currently mainstream email clients tend to consume substantial
    amount of system resources, while most functions are not utilized by most
    users, the author has been seeking for simplistic email clients, e.g.
    console-based email client. After trying some such softwares (Mutt,
    Alpine, etc) as instructed, the author found the control of those programs
    hard to learn (similar to Vim and Emacs), so a great focus of this program
    is the "user-friendliness", which initiates the idea of "Jimmy-Bot"
    human-language interpretation function. 

2. CODE STRUCTURE:
    This program's code structure is mainly as follows:
        - main.py: the main 'executable' code that is triggered when running;
        - mailbox.py: defines the extension of Python's IMAP and SMTP class,
          including: MainSession (encloses both of following classes),
          MailBoxIMAP (extension class for Python's IMAP class), MailBoxSMTP
          (extension class for Python's SMTP class).
        - IOControl.py: the singe file that realize most of the program's
          functionalities, including the menu appearance, key stroke
          responder, email data processing, Bot-command parsing, etc.
        - appdata.py: the file includes all string constants as screen output.
          The file is separated from the rest part of code to feature
          flexibility in User-Interface.
        - misc.py: the file containing small functions for miscellaneous
          purposes, such as "size string" generation, "date string" parsing
          and email validation check.
        - run.sh: the script file executable in Linux that can run main.py
          uwing Python.
        - html2text.py: an external module to convert a HTML string to plain
          text. The script is written by Aaron Swartz.
    All sources other than the last file are my personal work.

3. RUNNING OPTIONS:
    ./run.sh                        Default mode for Jimmy-Mail
    ./run.sh EMAIL_ADDRESS          Call Jimmy-Mail with designated email
    ./run.sh help                   Display help for calling parameters

    (Note 1: All "./run.sh" can be substitued with "python main.py" for non-
             Linux systems.)
    (Note 2: More parameter options will be supported, such as IMAP/SMTP
             server auto-completion)

4. PROGRAM FUNCTIONS:
    - Command Line Interface:
        * Compose Email: enter "n", "nm", "compose", etc. to command line.
        * Check Inbox: enter "i", "inbox", etc to command line.
        * View Folder List: enter "ls", "folders", "dir", etc. to command line.
        * Check out specific folder: enter only folder name to command line.
        * Search for emails: enter "s", "f", "search", etc. to command line.
        * View brief help: enter "?", "help", etc. to command line.
        * Smart-Command Interpretation: speak to Jimmy-bot in human-language!
    - Email List Mode:
        * Up/Down/PgUp/PgDn/Mouse Scroll: move through the email list
        * f/F: flag/unflag any specific email
        * SPACE/ENTER: read the specific email
        * r/R: reply to the specific email
        * D: delete the specific email (move to Trash Folder)
        * q/Q: quit to Command Line Interface
    - Email Viewing Mode:
        * All keys other than SPACE/ENTER option are active.
    - Smart-Command Interpretation:
        * <email/msg> from <sender>: search all emails from a sender
        * <email/msg> about <keywords>: search all emails with given keywords
        * Feel free to try some combinations!
        (Note: Jimmy-Bot will be smarter in the future)

5. TECHNICAL DETAILS:
    - Python's imaplib and smtplib libraries are used when communicating with
      email servers. All flags and commands are strictly compatible with the
      IMAP standards outlined in RFC3501, which can be found at:
      <ftp://ftp.rfc-editor.org/in-notes/rfc3501.txt>.
    - Only IMAP and SMTP protected by SSL is supported to enhance security.
    - Python's email library is used when encoding/decoding email messages.
      All operations are in accordance with MIME (Multipurpose Internet
      Mail Extensions).
    - Non-ASCII (like UTF-8) headers (like in French, Chinese and Japanese)
      are supported for display.

6. KNOWN ISSUES:
    - Because this email client retrieves all emails of a given list at once,
      it can be slow (>10s) for more than 300 messages per list. Effort will
      be made to retrieve message headers page by page.
    - Although internalization is supported with best effort, some issues may
      still appear for Chinese, Korean and Japanese characters. Those issues
      will be fixed when possible.

7. ACKNOWLEDGEMENTS:
    - First of all, this whole project is sincerely dedicated to Sunny C.,
      whose support and understanding enables me to finalize the project;
    - Thanks Professor David Kosbie for his wonderful introductory course of
      Python and his suggestions for my project;
    - And, thanks my Project Mentor Disha Bora who tracked the progress of
      this project, and my friends who gave me feedback on the performance of
      this program;
    - At last, the thank goes to Aaron Swartz, whose html2text module is a
      great help for displaying HTML-only messages.


