import lind_test_server as server
from lind_fs_constants import *

# This will load the filesystem and the special character files
# It checks if the metadata is already present, if so it will
# load up the metadata.
server.load_fs()

server.stat_syscall("/dev")

# Check If the special files have been created...
assert(server.stat_syscall("/dev/null")[6] == (1, 3))
assert(server.stat_syscall("/dev/random")[6] == (1, 8))
assert(server.stat_syscall("/dev/urandom")[6] == (1, 9))
