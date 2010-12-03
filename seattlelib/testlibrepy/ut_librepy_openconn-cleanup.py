"""
This unit test checks that openconn() waits for
socket cleanup.
"""
#pragma repy restrictions.default dylink.repy librepy.repy

# Get the IP address of intel.com
intel_IP = gethostbyname("intel.com")
intel_port = 80
localip = getmyip()
localport = libsocket.get_connports(localip)[0]

# Connect to intel
sock = openconn(intel_IP, intel_port, localip, localport)
sock.close()

# Re-use the sample tuple, set a long timeout
try:
  sock2 = openconn(intel_IP, intel_port, localip, localport, timeout=300)
  sock2.close()
except CleanupInProgressError:
  print "Openconn should handle socket cleanup! We should have blocked!"
except TimeoutError:
  print "Openconn timed out! We should have cleaned up by now."

