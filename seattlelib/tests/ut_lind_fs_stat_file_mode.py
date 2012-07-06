import lind_test_server

from lind_fs_constants import *

# Let's add a few files, etc. to the system and see if it works...
lind_test_server._blank_fs_init()

myfd = lind_test_server.open_syscall('/foo',O_CREAT | O_EXCL | O_WRONLY,S_IRWXA)


stat_result = lind_test_server.stat_syscall('/foo')

# ensure the mode is a regular file with all bits on.
assert(stat_result[2] == S_IRWXA | S_IFREG)

             
# create a file with no perms...
myfd2 = lind_test_server.open_syscall('/foo2',O_CREAT | O_EXCL | O_WRONLY,0)

stat_result2 = lind_test_server.stat_syscall('/foo2')

# ensure the mode is a regular file with all bits off.
assert(stat_result2[2] == S_IFREG)

stat_result = lind_test_server.stat_syscall('.')

