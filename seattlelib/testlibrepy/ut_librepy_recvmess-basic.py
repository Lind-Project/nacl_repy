"""
This unit test tries to test that recvmess() works at a basic level
by using a simple callback to send 2 messages.
"""
#pragma repy restrictions.threeports dylink.repy librepy.repy

# Count the number of incoming sockets
COUNTER=[0]

def incoming(ip, port, mess):
  COUNTER[0] += 1
  if COUNTER[0] == 1:
    assert(mess == "Test")
  elif COUNTER[0] == 2:
    assert(mess == "Ping")
  if COUNTER[0] > 2:
    print "Too many incoming messages!"

# Setup a listener
listen_ip = getmyip()
listen_port = libsocket.get_messports(listen_ip)[0]
stop_func = recvmess(listen_port, incoming, listen_ip)

# Send 2 messages
assert(sendmess(listen_ip, listen_port, "Test") == 4)
assert(sendmess(listen_ip, listen_port, "Ping") == 4)

# Sleep a bit
sleep(0.5)

# Check the counter
if COUNTER[0] != 2:
  print "Not enough messages accepted! Got: "+str(COUNTER[0])

# Stop listening
stop_func()

