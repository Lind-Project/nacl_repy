"""

This test irritates a bug which causes the inode table to get
mucked up.  After a socket operations, a regular file close
will through an unexpected exception:

Traceback (most recent call last):
  File "ut_lind_fs_broken_close.py", line 52, in <module>
    lind_test_server.close_syscall(myfd)
  File "/home/lind/tmp/lind/repy/wrapped_lind_test_server.py", line 1370, in close_syscall
    return _close_helper(fd)
  File "/home/lind/tmp/lind/repy/wrapped_lind_test_server.py", line 1333, in _close_helper
    fdsforinode = _lookup_fds_by_inode(inode)
  File "/home/lind/tmp/lind/repy/wrapped_lind_test_server.py", line 1307, in _lookup_fds_by_inode
    if filedescriptortable[fd]['inode'] == inode:
KeyError: 'inode'


"""


from lind_fs_constants import *

from emulmisc import exitall

from time import sleep

from lind_net_constants import *

import lind_test_server

SyscallError = lind_test_server.SyscallError

# Try read / write of a file and see if it works...
lind_test_server._blank_fs_init()

myfd = lind_test_server.open_syscall('/foo', O_CREAT | O_EXCL | O_RDWR, S_IRWXA)



# write should succeed
assert(lind_test_server.write_syscall(myfd, 'hello there!') == 12)

lind_test_server.close_syscall(myfd)

# Now, re open the file

myfd = lind_test_server.open_syscall('/foo', O_RDWR, S_IRWXA)

lind_test_server.close_syscall(myfd)


# let's do a few basic things with connect.   This will be UDP only for now...

sockfd = lind_test_server.socket_syscall(AF_INET, SOCK_STREAM, 0)


# bind will not be interesting...
assert lind_test_server.bind_syscall(sockfd, '10.0.0.1', 50102) == 0
try:
    lind_test_server.setshutdown_syscall(sockfd, SHUT_RD)
except:
    pass

myfd = lind_test_server.open_syscall('/foo', O_RDWR, S_IRWXA)
lind_test_server.close_syscall(myfd)

myfd = lind_test_server.open_syscall('/foo', O_RDWR, S_IRWXA)

lind_test_server.close_syscall(myfd)
