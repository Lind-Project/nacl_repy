"""
This unit test checks that stopping a waitforconn()
actually works.
"""
#pragma repy restrictions.threeports dylink.repy librepy.repy

def incoming(sock):
  print "Should not get incoming connections!"
  sock.close()

# Setup a listener
listen_ip = getmyip()
listen_port = libsocket.get_connports(listen_ip)[0]
stop_func = waitforconn(listen_port, incoming, listen_ip)

# Stop listening
stop_func()
sleep(0.1)

# Try to connect
try:
  s = openconn(listen_ip, listen_port)
  print "Should not connect!"
  s.close()
except ConnectionRefusedError:
  pass


