"""
This unit test tries to test that recvmess() works at a basic level
by using a thread pool to send 2 messages
"""
#pragma repy restrictions.threeports dylink.repy librepy.repy

# How many times should we try to connect
# We need TRY_COUNT + 1 connports for this to work
TRY_COUNT = 2

# Count the number of incoming sockets
COUNTER=[0]

def incoming(ip, port, mess):
  assert(mess == "test")
  COUNTER[0] += 1
  if COUNTER[0] > TRY_COUNT:
    print "Too many incoming messages!"


# Setup a thread pool
tpool = ThreadPool()
tpool.start()

# Setup a listener
listen_ip = getmyip()
listen_port = libsocket.get_messports(listen_ip)[0]
stop_func = recvmess(listen_port, incoming, listen_ip, tpool)

# Connect 3 times
for x in xrange(TRY_COUNT):
  sendmess(listen_ip, listen_port,"test")

# Sleep a bit
sleep(0.5)

# Check the counter
if COUNTER[0] != TRY_COUNT:
  print "Not enough messages accepted! Got: "+str(COUNTER[0])

# Stop listening, destroy the thread pool
stop_func(True)

