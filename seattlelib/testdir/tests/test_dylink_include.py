"""
Author: Armon Dadgar
Description:
  This test checks that the dylink pre-processor methods are working properly by "including"
  the sockettimeout library. We then check that the functions work.

  This test uses the old "include" directive
"""

# Import the sockettimeout library
include sockettimeout

def new_conn(ip,port,sock,ch1,ch2):
  # Wait 3 seconds, then send data
  sleep(2)
  sock.send("Ping! Ping!")
  sock.close()

if callfunc == "initialize":
  # Check that we have the basic openconn,waitforconn and stopcomm
  # This will throw an Attribute error if these are not set
  check = timeout_openconn
  check = timeout_waitforconn
  check = timeout_stopcomm

  # Get our ip
  ip = getmyip()
  port = 12345

  # Setup a waitforconn
  waith = timeout_waitforconn(ip,port,new_conn)

  # Try to do a timeout openconn
  sock = timeout_openconn(ip,port,timeout=2)

  # Set the timeout to 1 seconds, and try to read
  sock.settimeout(1)
  try:
    data = sock.recv(16)

    # We should timeout
    print "Bad! Got data: ",data
  except:
    pass

  # Close the socket, and shutdown
  sock.close()
  timeout_stopcomm(waith)

  

