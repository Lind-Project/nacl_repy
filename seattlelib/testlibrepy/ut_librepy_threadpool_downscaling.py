#pragma repy restrictions.default dylink.repy librepy.repy
"""
This unit test checks the down-scaling behavior of the thread
pool. It ensures we scale down properly.
"""
# Create a lock
lock = Lock()
lock.acquire()

# Create a thread pool
tpool = ThreadPool(scaling_thres=1) # 1 task per-thread, 4 thread max

# If we schedule 8 tasks, then all 4 threads will be
# working on 1, and have 1 queued.
def noop():
  lock.acquire()

for x in xrange(8):
  tpool.add_task(noop)

# There should be 4 threads now
sleep(0.4)
if tpool.threads() != 4:
  print "There should be 4 threads running!"

# We expected that every other time lock.release() is
# called that a thread shuts down. This is because now
# all 4 threads are blocked on acquire(), and there is
# a queued task per thread. If I release twice, then
# there will be 6 tasks, which means 3 threads blocked,
# and 3 tasks queued (1 per thread). Etc, down until 0
# tasks are queued.
for x in xrange(8):
  lock.release()
  sleep(0.2)
  if x % 2 == 0:
    if tpool.threads() != 4 - x/2:
      print "Should have scaled down! x: "+str(x)+" Threads: "+str(tpool.threads())

# Done
exitall()


