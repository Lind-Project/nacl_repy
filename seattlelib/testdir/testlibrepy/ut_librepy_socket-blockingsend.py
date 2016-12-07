"""
This unit test checks the behavior of a blocking send.
We fill up our send buffer, and then we do a blocking send.
"""
#pragma repy restrictions.widenet dylink.repy librepy.repy

SYNC_LOCK = Lock()
SYNC_LOCK.acquire()

def incoming(sock):
  SYNC_LOCK.acquire()
  sleep(0.2)
  sock.recv(100000)
  sock.send("got it")
  sleep(2) 
  sock.close()


# Get the IP, and some ports
ip = getmyip()
free_ports = libsocket.get_connports(ip)
listen_port = free_ports[0]
client_port = free_ports[1]

# Setup a listener
stop_func = waitforconn(listen_port, incoming, ip)

# Connect now
s = openconn(ip, listen_port, localip=ip, localport=client_port)
s.settimeout(0) # Non-blocking

# Generate some random data
data = randombytes() * 4 # 4K of data

sent = 0
while True:
  try:
    sent += s.send(data)
  except SocketWouldBlockError:
    break

# Release the other thread
SYNC_LOCK.release()

s.settimeout(None) # blocking
more = s.send(data) # We should now block for more

# Check that we sent something, min 20K
if more <= 96:
  print "Sent too little! Sent: "+str(sent)

# Close and cleanup
sleep(0.2)
s.close()
stop_func()

