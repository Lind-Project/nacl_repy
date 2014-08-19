"""
This unit test tries to test that waitforconn() works at a basic level
by using a thread pool to connect 2 sockets.
"""
#pragma repy restrictions.threeports dylink.repy librepy.repy

# How many times should we try to connect
# We need TRY_COUNT + 1 connports for this to work
TRY_COUNT = 2

# Count the number of incoming sockets
COUNTER=[0]

def incoming(sock):
  COUNTER[0] += 1
  if COUNTER[0] > TRY_COUNT:
    print "Too many incoming connections!"
  sock.close()

# Setup a thread pool
tpool = ThreadPool()
tpool.start()

# Setup a listener
listen_ip = getmyip()
listen_port = libsocket.get_connports(listen_ip)[0]
stop_func = waitforconn(listen_port, incoming, listen_ip, tpool)

# Connect 3 times
CONNECTED_SOCKS = []
for x in xrange(TRY_COUNT):
  CONNECTED_SOCKS.append(openconn(listen_ip, listen_port))

# Sleep a bit
sleep(0.5)

# Check the counter
if COUNTER[0] != TRY_COUNT:
  print "Not enough connections accepted! Got: "+str(COUNTER[0])

# Close all
for s in CONNECTED_SOCKS:
  s.close()

# Stop listening, destroy the thread pool
stop_func(True)

