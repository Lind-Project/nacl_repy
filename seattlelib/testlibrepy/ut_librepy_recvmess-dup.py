"""
This test checks what happens if there are 2 duplicate
calls to recvmess.
"""
#pragma repy restrictions.threeports dylink.repy librepy.repy

# Count the number of incoming messages
COUNTER=[0]

def incoming(ip, port, mess):
  assert(mess == "test")
  COUNTER[0] += 1
  if COUNTER[0] > 1:
    print "Too many incoming messages!"

# Setup a listener
listen_ip = getmyip()
listen_port = libsocket.get_messports(listen_ip)[0]
stop_func = recvmess(listen_port, incoming, listen_ip)

# Try a duplicate listen
try:
  stop_func_2 = recvmess(listen_port, incoming, listen_ip)
  stop_func_2()
  print "Second recvmess worked!"
except AlreadyListeningError:
  pass

# Try to connect
sent = sendmess(listen_ip, listen_port, "test")
assert(sent == 4)
sleep(0.2)

# Check the counter
if COUNTER[0] != 1:
  print "Not enough messages accepted! Got: "+str(COUNTER[0])

# Stop listening
stop_func()

