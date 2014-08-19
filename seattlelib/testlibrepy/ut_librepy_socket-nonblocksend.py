"""
This unit test checks that we eventually get a
SocketWouldBlockError when using a non-blocking send.
"""
#pragma repy restrictions.widenet dylink.repy librepy.repy

def incoming(sock):
  sleep(5) # We should block within 5 seconds
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
s.settimeout(0.0) # Non-blocking

# Generate some random data
data = randombytes() * 4 # 4K of data

sent = 0
while True:
  try:
    sent += s.send(data)
  except SocketWouldBlockError:
    break

# Check that we sent something, min 20K
if sent <= 20000:
  print "Sent too little! Sent: "+str(sent)

# Close and cleanup
sleep(0.2)
s.close()
stop_func()

