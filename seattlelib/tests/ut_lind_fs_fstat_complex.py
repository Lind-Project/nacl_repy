import lind_test_server
from lind_fs_constants import *

# this is very similar to the stat complex test, I had to remove the links
# though

# Let's add a few files, etc. to the system and see if it works...
lind_test_server.load_fs(-1)

myfd = lind_test_server.get_fscall_obj(-1).open_syscall('/foo',O_CREAT | O_WRONLY,S_IRWXA)

# write should succeed
assert(lind_test_server.get_fscall_obj(-1).write_syscall(myfd,'hi') == 2)

stat_result = lind_test_server.get_fscall_obj(-1).fstat_syscall(myfd)

# ensure the file has size 2
assert(stat_result[7] == 2)

# ensure the link count is 1
assert(stat_result[3] == 1)

