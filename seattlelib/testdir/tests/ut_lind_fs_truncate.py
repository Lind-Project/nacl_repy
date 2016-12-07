# Check the ftruncate systemcall

import lind_test_server

from lind_fs_constants import *

lind_test_server._blank_fs_init()

fd = lind_test_server.open_syscall('/foo', O_CREAT | O_EXCL | O_RDWR, S_IRWXA)

# Make a big file
msg = "Hello" * 100
size = len(msg)

# how small will we make the file
TRUNCATE_SIZE = 10
NEW_TRUNCATE_SIZE = 200
lind_test_server.write_syscall(fd, msg)

lind_test_server.ftruncate_syscall(fd, TRUNCATE_SIZE)

# seek to the beginning...
assert(lind_test_server.lseek_syscall(fd, 0, SEEK_SET) == 0)


data = lind_test_server.read_syscall(fd, 100)

assert len(data) == TRUNCATE_SIZE, "File must be smaller after truncate"

assert data == msg[:TRUNCATE_SIZE], "New files contents must match: \n%s\n%s" \
       % (data, msg[:TRUNCATE_SIZE])

lind_test_server.ftruncate_syscall(fd, NEW_TRUNCATE_SIZE)

# seek to the beginning...
assert(lind_test_server.lseek_syscall(fd, 0, SEEK_SET) == 0)


data2 = lind_test_server.read_syscall(fd, NEW_TRUNCATE_SIZE)

assert data2 == (msg[:TRUNCATE_SIZE] + '\x00' * \
                 (NEW_TRUNCATE_SIZE - TRUNCATE_SIZE)), \
       "Expecting zero padding when truncating to a bigger size"

lind_test_server.close_syscall(fd)
