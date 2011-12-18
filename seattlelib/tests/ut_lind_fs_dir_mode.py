import lind_fs_calls

from lind_fs_constants import *

# Let's add a few directories to the system and see if it works...
lind_fs_calls._blank_fs_init()

lind_fs_calls.mkdir_syscall('/bar',S_IRWXA)


stat_result = lind_fs_calls.stat_syscall('/bar')

# ensure the mode is a dir with all bits on.
assert(stat_result[2] == S_IRWXA | S_IFDIR)

             
# create a dir with no perms...
lind_fs_calls.mkdir_syscall('/bar2',0)


stat_result = lind_fs_calls.stat_syscall('/bar2')

# ensure the mode is a dir with all bits on.
assert(stat_result[2] == S_IFDIR)

