"""
This unit test checks that stopping a recvmess()
actually works.
"""
#pragma repy restrictions.threeports dylink.repy librepy.repy

def incoming(ip, port, mess):
  print "Should not get incoming messages!"

# Setup a listener
listen_ip = getmyip()
listen_port = libsocket.get_messports(listen_ip)[0]
stop_func = recvmess(listen_port, incoming, listen_ip)

# Stop listening
stop_func()
sleep(0.1)

# Try to connect
s = sendmess(listen_ip, listen_port, "test")

# Sleep a bit
sleep(0.4)


