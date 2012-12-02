import re
from email.utils import parsedate as ParseDate
from email.utils import parseaddr as ParseAddr
from email.header import decode_header

def isValidEmail(emailAddr):
    match= r"^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(\]?)$"
    return bool(re.match(match, emailAddr)) and len(match) >= 7

list_response_pattern = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')

def parseListResponse(line):
    flags, delimiter, mailbox_name = list_response_pattern.match(line).groups()
    mailbox_name = mailbox_name.strip('"')
    return (flags, delimiter, mailbox_name)

def digitNo(num):
    return 1 if num < 10 else digitNo(num/10) + 1

def convertDate(imapDate):
    DateList = ParseDate(imapDate)
    MonthList = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
            "Sep", "Oct", "Nov", "Dec"]
    return MonthList[DateList[1]] + " " + str(DateList[2]).rjust(2, "0") + " '" + str(DateList[0])[2:]

def displayEml(wholeAddr):
    tupled = ParseAddr(wholeAddr)
    return tupled[0] or tupled[1]

def decodeHeader(inputStr):
    info = decode_header(inputStr)
    defaultCharset = "ASCII"
    return "".join([unicode(char[0], char[1] or defaultCharset) for char in info])

def strSpan(inputStr, width):
    return inputStr.ljust(width, " ")[:width]

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

