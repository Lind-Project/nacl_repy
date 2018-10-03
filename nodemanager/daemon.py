"""
<Program Name>
  daemon.py

<Purpose>
  Daemon Module --- basic facilities for becoming a daemon process

  Goals of a daemon process:

  * Detaches from its ancestor processes so that it doesn't block 
    the launching terminal / script, and is not affected by their 
    fate (e.g. termination)
  * Detaches from any controlling TTY (interactive terminal or similar) 
    so it cannot be stopped or otherwise interacted with inadvertently, 
    and drops privileges that would allow it to reclaim a TTY
  * Can be created from any starting point -- interactive shell, Python 
    script, cron, ...
  * If done very correctly, also detaches from the creator's environment 
    such as mount points to minimize interference. (NOT IMPLEMENTED HERE!)


<Details>

  (See the Web for a more detailed write-up including references:
  https://github.com/SeattleTestbed/nodemanager/issues/115 )

  0. Terminology:
     PID=process ID, PPID=parent PID, PGRP=process group, SID=session ID.

  1. We start with the parent process that wants to create a daemonized 
     copy of itself. Let's assume we started Parent in an interactive 
     shell.
       Parent process: PID=parentID, PPID=shellID, PGRP=parentID, SID=shellID

  2. Parent calls fork() to fork off Child 1. The parent process wait()s 
     for Child 1 to exit.
       Child 1: PID=child1ID, PPID=parentID, PGRP=parentID, SID=shellID
       (Child 1 has the parent process as its parent, shares its process 
       group, and is in the shell's session.)

  3. We are not done yet, because Parent is wait()ing for Child 1 to terminate.

  4. Child 1 now calls setsid(), creating a new session, becoming its 
     leader, and also becoming the process group leader. (Its leadership 
     will become important only after the next fork(), see below).
       Child 1: PID=child1ID, PPID=parentID, PGRP=child1ID, SID=child1ID

  5. (Depending on the requirements of the implementation, Child 1 should 
     also close all of the file descriptors it inherited, chdir into /, 
     and set its umask to 0. Alternatively, this might be done in 
     Child 2 instead.)

  6. We are not done yet because
     * Parent is still wait()ing for Child 1, so if Child 1 would continue 
       to run, this would keep Parent alive too.
     * Child 1 is the leader of the new session, and can thus reacquire 
       the controlling terminal even if it closed the file descriptors that 
       it inherited from Parent. We specifically wanted to make this 
       impossible for the daemon process.

  7. Thus, Child 1 calls fork() itself, creating Child 2 which is neither 
     the process group nor session leader, and therefore cannot reacquire 
     the controlling terminal. Note that Parent does not wait() for 
     Child 2, as this is a grand-child.
       Child 2: PID=child2ID, PPID=child1ID, PGRP=child1ID, SID=child1ID

  8. Following the fork, Child 1 exits. This leaves Child 2 without a 
     parent for a moment, but an init process will adopt it soon. The 
     consequence of Child 1's exit is that Parent can exit now, too. 
     Eventually, we are left with only Child 2 which is now a daemon:
       Child 2: PID=child2ID, PPID=initID, PGRP=child1ID, SID=child1ID

  Note that in contrast to traditional lore, the process ID of the init 
  process (initID above) is not necessarily 1. Upstart (and possibly 
  other init replacements) has init --user processes with different PIDs 
  for graphical sessions aka "User Session Mode".


<Notes>
  Combines ideas from Steinar Knutsens daemonize.py and
  Jeff Kunces demonize.py

  Originally posted to python-list; an archive of the post is available
  here: http://aspn.activestate.com/ASPN/Mail/Message/python-list/504777
  Assumed is that the author intended for the (fairly trivial body of) code
  to be freely usable by any developer.

"""


import os
import time
import sys


class NullDevice:
  def write(self, s):
    pass


def daemonize():
  """
  daemonize:
    Purpose:
      Detach from stdin/stdout/stderr, return control of the term to the user.

    Returns:
      Nothing.

  """

  if os.name == "nt" or os.name == "ce":
    # No way to fork or daemonize on windows. Just do nothing for now?
    return

  if not os.fork():
    # get our own session and fixup std[in,out,err]
    os.setsid()
    sys.stdin.close()
    sys.stdout = NullDevice()
    sys.stderr = NullDevice()
    if not os.fork():
      # hang around till adopted by init
      while os.getppid() == os.getpgrp():
        time.sleep(0.5)
    else:
      # time for child to die
      os._exit(0)
  else:
    # wait for child to die and then bail
    os.wait()
    sys.exit()
