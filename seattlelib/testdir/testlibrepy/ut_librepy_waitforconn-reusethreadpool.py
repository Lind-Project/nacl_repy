"""
This unit test tries to test that waitforconn() works at a basic level
by using a simple callback to connect 2 sockets. We connect 1 socket,
and then stop listening and then start listening again.

We use a single thread pool rather than callbacks.
"""
#pragma repy restrictions.threeports dylink.repy librepy.repy

# Count the number of incoming sockets
COUNTER=[0]

def incoming(sock):
  COUNTER[0] += 1
  if COUNTER[0] > 2:
    print "Too many incoming connections!"
  sock.close()

# Set a thread pool
tpool = ThreadPool()
tpool.start()

# Setup a listener
listen_ip = getmyip()
listen_port = libsocket.get_connports(listen_ip)[0]
stop_func = waitforconn(listen_port, incoming, listen_ip, tpool)

# Connect 1 socket
s1 = openconn(listen_ip, listen_port)

# Sleep a bit
sleep(0.2)

# Stop listening, then start again
stop_func(False) # DO NOT destroy the thread pool
stop_func = waitforconn(listen_port, incoming, listen_ip, tpool)

# Connect another socket
s2 = openconn(listen_ip, listen_port)

# Sleep a bit
sleep(0.2)

# Check the counter
if COUNTER[0] != 2:
  print "Not enough connections accepted! Got: "+str(COUNTER[0])

# Stop listening, this time destroy the pool
stop_func(True)

# Close the sockets
s1.close()
s2.close()

