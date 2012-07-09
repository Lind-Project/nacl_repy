import lind_test_server

from lind_fs_constants import *

# Let's add a few files, etc. to the system and see if it works...
lind_test_server._blank_fs_init()

filefd = lind_test_server.open_syscall('/foo',O_CREAT | O_EXCL | O_WRONLY,\
  S_IRWXA)

assert lind_test_server.stat_syscall('/foo')[2] == S_IRWXA | S_IFREG, \
  "Failed to have full access to all users."

lind_test_server.chmod_syscall('/foo', S_IRUSR | S_IRGRP)

assert lind_test_server.stat_syscall('/foo')[2] == S_IRUSR | S_IRGRP | S_IFREG\
  , "Failed to set Read access to user and group."

lind_test_server.chmod_syscall('/foo', S_IRWXA)

assert lind_test_server.stat_syscall('/foo')[2] == S_IRWXA | S_IFREG, \
  "Failed to set back full access to all users."

lind_test_server.close_syscall(filefd)
