"""
This unit test tries to test that recvmess() works at a basic level
by using a simple callback to recieve 2 messages. We send 1 message,
and then stop listening and then start listening again.
"""
#pragma repy restrictions.threeports dylink.repy librepy.repy

# Count the number of incoming messages
COUNTER=[0]

def incoming(ip, port, mess):
  COUNTER[0] += 1
  if COUNTER[0] > 2:
    print "Too many incoming connections!"

# Setup a listener
listen_ip = getmyip()
listen_port = libsocket.get_messports(listen_ip)[0]
stop_func = recvmess(listen_port, incoming, listen_ip)

# Send 1 message
s1 = sendmess(listen_ip, listen_port, "test")
assert(s1 == 4)

# Sleep a bit
sleep(0.2)

# Stop listening, then start again
stop_func()
stop_func = recvmess(listen_port, incoming, listen_ip)

# Connect another socket
s2 = sendmess(listen_ip, listen_port, "test")
assert(s2 == 4)

# Sleep a bit
sleep(0.2)

# Check the counter
if COUNTER[0] != 2:
  print "Not enough messages accepted! Got: "+str(COUNTER[0])

# Stop listening
stop_func()

