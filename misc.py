# misc.py
# Yiming Zong - Carnegie Mellon University '16
# yzong (at) cmu.edu
# ---------------------------------------------------------------
#     This file contains miscellaneous functions for email processing.
# Please DO NOT modify the code here unless you are absolutely sure
# about what you are doing.

import re
from email.utils import parsedate as ParseDate
from email.utils import parseaddr as ParseAddr
from email.header import decode_header
from appdata import *

# This function checks whether a given email is valid.
def isValidEmail(emailAddr):
    match= r"^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$"
    return bool(re.match(match, emailAddr)) and len(match) >= 7

list_response_pattern = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)"'+
                                   r' (?P<name>.*)')

# This function parses the LIST response from IMAP server.
def parseListResponse(line):
    flags, delimiter, mailbox_name = list_response_pattern.match(line).groups()
    mailbox_name = mailbox_name.strip('"')
    return (flags, delimiter, mailbox_name)

# This function returns the number of digits of a number.
def digitNo(num):
    return 1 if num < 10 else digitNo(num/10) + 1

# This function converts the IMAP date format for human-friendly format.
def convertDate(imapDate):
    try:
        DateList = ParseDate(imapDate)
        MonthList = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
               "Sep", "Oct", "Nov", "Dec"]
        return (MonthList[DateList[1]] +" "+ str(DateList[2]).rjust(2, "0")+
                " '" + str(DateList[0])[2:])
    except Exception:
        return "ERR-DATE-STR"

#     This function parse the name and email from an email string like:
# "Example Name <example@example.org>".
def displayEml(wholeAddr):
    tupled = ParseAddr(wholeAddr)
    return tupled[0] or tupled[1]

# This function decodes the header of email for non-ASCII cases.
def decodeHeader(inputStr):
    info = decode_header(inputStr)
    defaultCharset = "ASCII"
    return "".join([unicode(char[0], char[1] or defaultCharset) for char in info])

# This function adjusts ths length of a given string to given length.
def strSpan(inputStr, width):
    return inputStr.ljust(width, " ")[:width]

# This function returns the Size String of an email for given Byte Info.
def sizeString(size):
    size = int(size)
    if size < 995:         # Less than 1KB: (.xK)
        sizeStr = ("%.1fK" % (float(size)/1000)).lstrip("0")
    elif size < 99500:     # Less than 100KB: (xxK)
        sizeStr = ("%.0fK" % (float(size)/1000))
    elif size < 995000:    # Less than 1MB: (.xM)
        sizeStr = ("%.1fM" % (float(size)/1000000)).lstrip("0")
    elif size < 99500000:  # Less than 100MB: (xxM)
        sizeStr = ("%.0fM" % (float(size)/1000000))
    else: sizeStr = "ERR"
    return ("(" + sizeStr + ")").rjust(5)

# This function prints basic help for Command Line Interface.
def SmartModeInstruct(maxX):
    for instruction in INSTRUCTIONS:
        print ("{0:^" + str(maxX) + "}").format(instruction)
