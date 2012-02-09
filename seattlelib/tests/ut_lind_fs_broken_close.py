"""

This test irritates a bug which causes the inode table to get
mucked up.  After a socket operations, a regular file close
will through an unexpected exception:

Traceback (most recent call last):
  File "ut_lind_fs_broken_close.py", line 52, in <module>
    lind_fs_calls.close_syscall(myfd)
  File "/home/lind/tmp/lind/repy/wrapped_lind_fs_calls.py", line 1370, in close_syscall
    return _close_helper(fd)
  File "/home/lind/tmp/lind/repy/wrapped_lind_fs_calls.py", line 1333, in _close_helper
    fdsforinode = _lookup_fds_by_inode(inode)
  File "/home/lind/tmp/lind/repy/wrapped_lind_fs_calls.py", line 1307, in _lookup_fds_by_inode
    if filedescriptortable[fd]['inode'] == inode:
KeyError: 'inode'


"""

import wrapped_lind_fs_calls as lind_fs_calls

from lind_fs_constants import *

import lind_net_calls as lind_net_calls

from emultimer import createthread as createthread

from emulmisc import exitall

from time import sleep

from lind_net_constants import *

SyscallError = lind_net_calls.SyscallError

# Try read / write of a file and see if it works...
lind_fs_calls._blank_fs_init()

myfd = lind_fs_calls.open_syscall('/foo', O_CREAT | O_EXCL | O_RDWR, S_IRWXA)

print myfd


# write should succeed
assert(lind_fs_calls.write_syscall(myfd, 'hello there!') == 12)

lind_fs_calls.close_syscall(myfd)

# Now, re open the file

myfd = lind_fs_calls.open_syscall('/foo', O_RDWR, S_IRWXA)

lind_fs_calls.close_syscall(myfd)


# let's do a few basic things with connect.   This will be UDP only for now...

sockfd = lind_net_calls.socket_syscall(AF_INET, SOCK_STREAM, 0)

print sockfd

# bind will not be interesting...
assert lind_net_calls.bind_syscall(sockfd, '10.0.0.1', 50102) == 0
try:
    lind_net_calls.setshutdown_syscall(sockfd, SHUT_RD)
except:
    pass

myfd = lind_fs_calls.open_syscall('/foo', O_RDWR, S_IRWXA)
print myfd
lind_fs_calls.close_syscall(myfd)

myfd = lind_fs_calls.open_syscall('/foo', O_RDWR, S_IRWXA)

lind_fs_calls.close_syscall(myfd)
