"""
This test checks what happens if there are 2 duplicate
calls to waitforconn.
"""
#pragma repy restrictions.threeports dylink.repy librepy.repy

# Count the number of incoming sockets
COUNTER=[0]

def incoming(sock):
  COUNTER[0] += 1
  if COUNTER[0] > 1:
    print "Too many incoming connections!"
  sock.close()

# Setup a listener
listen_ip = getmyip()
listen_port = libsocket.get_connports(listen_ip)[0]
stop_func = waitforconn(listen_port, incoming, listen_ip)

# Try a duplicate listen
try:
  stop_func_2 = waitforconn(listen_port, incoming, listen_ip)
  stop_func_2()
  print "Second waitforconn worked!"
except AlreadyListeningError:
  pass

# Try to connect
s = openconn(listen_ip, listen_port)
sleep(0.2)
s.close()

# Check the counter
if COUNTER[0] != 1:
  print "Not enough connections accepted! Got: "+str(COUNTER[0])

# Stop listening
stop_func()

