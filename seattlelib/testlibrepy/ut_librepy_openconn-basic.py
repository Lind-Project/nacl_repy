"""
This unit test checks the basics of openconn() to make
sure it works.
"""
#pragma repy restrictions.default dylink.repy librepy.repy

# Connect to google
goog_sock = openconn("google.com", 80)
goog_sock.close()

# Connect to Yahoo
yahoo_sock = openconn("yahoo.com", 80)
yahoo_sock.close()

# Connect to MSN
msn_sock = openconn("msn.com", 80, getmyip())
msn_sock.close()

