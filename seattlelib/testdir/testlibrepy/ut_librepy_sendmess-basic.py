"""
This unit test checks the basics of sendmess() to make
sure it works.
"""
#pragma repy restrictions.default dylink.repy librepy.repy

# Sent to google
goog_sent = sendmess("google.com", 80, "Test")
assert(goog_sent == 4)

# Sent to Yahoo
yahoo_sent = sendmess("yahoo.com", 80, "Test")
assert(yahoo_sent == 4)

# Sent to MSN, bind the IP
msn_sent = sendmess("msn.com", 80, "Test", getmyip())
assert(msn_sent == 4)

