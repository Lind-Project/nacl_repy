"""
File: ut_lind_fs_mknod.py

Unit test for mknod_syscall(), which is used to create special files.
"""

import lind_test_server
from lind_fs_constants import *

lind_test_server._blank_fs_init()
lind_test_server._load_lower_handle_stubs()

# let's create /dev/null...
lind_test_server.mknod_syscall('/null', S_IFCHR, (1, 3))
fd = lind_test_server.open_syscall('/null', O_CREAT | O_RDWR, S_IRWXA)

assert lind_test_server.fstat_syscall(fd)[2] & S_FILETYPEFLAGS == S_IFCHR,\
  "File should be a Character file."
assert lind_test_server.fstat_syscall(fd)[6] == (1, 3),\
  "File is not /dev/null."
assert lind_test_server.write_syscall(fd, "test") == 4,\
  "Write failed to /dev/null file."
assert lind_test_server.read_syscall(fd, 10) == '',\
  "Read failed from /dev/null file."

lind_test_server.close_syscall(fd)


# let's create /dev/random...
lind_test_server.mknod_syscall('/random', S_IFCHR, (1, 8))
fd = lind_test_server.open_syscall('/random', O_CREAT | O_RDWR, S_IRWXA)

assert lind_test_server.fstat_syscall(fd)[2] & S_FILETYPEFLAGS == S_IFCHR,\
  "File should be a Character file."
assert lind_test_server.fstat_syscall(fd)[6] == (1, 8),\
  "File is not /dev/random."
assert lind_test_server.write_syscall(fd, "test") == 4,\
  "Write failed to /dev/random file."
assert lind_test_server.read_syscall(fd, 10) != '',\
  "Read failed from /dev/random file."

lind_test_server.close_syscall(fd)
