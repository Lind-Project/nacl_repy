import runonce
import time
import os
import random

lockname = "seattletestlock"

runonce.getprocesslock(str(os.getpid()))

print "my process id is:"+str(os.getpid())
retval = runonce.getprocesslock(lockname)


if retval == True:
  print "I have the mutex"
elif retval == False:
  print "Another process has the mutex (owned by another user most likely)"
else:
  print "Process "+str(retval)+" has the mutex!"

while True:
  for num in range(random.randint(0,5)):
    time.sleep(2)
    if runonce.stillhaveprocesslock(lockname):
      print "I have the mutex"
    else:
      print "I do not have the mutex"
    if runonce.stillhaveprocesslock(str(os.getpid())):
      print "I have my mutex"
    else:
      print "I do not have my mutex"


  time.sleep(2)
  print "releasing mutex (if possible)"
  runonce.releaseprocesslock(lockname)

