#pragma repy restrictions.default dylink.repy librepy.repy
"""
This unit test checks that the minimum threads are started
when the ThreadPool is started.
"""
# Create the thread pool
tpool = ThreadPool(min_threads=2, max_threads=2)

# Get the number of idle threads
idle = libthread.active_threads()

# Start the pool
try:
  tpool.start()
except:
  pass
sleep(0.2)

# Check the number of threads
started_threads = libthread.active_threads()

# This should be +2
if idle + 2 != started_threads:
  print "Should have started 2 threads!"

# Check what the thread pool reports
if tpool.threads() != 2:
  print "Thread pool does not report 2 threads!"

# Done
exitall()

