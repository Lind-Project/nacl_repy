import wrapped_lind_fs_calls as lind_fs_calls

from lind_fs_constants import *

# Let's add a few directories to the system and see if it works...
lind_fs_calls._blank_fs_init()

lind_fs_calls.mkdir_syscall('/bar',S_IRWXA)

lind_fs_calls.mkdir_syscall('/bar/baz',S_IRWXA)

lind_fs_calls.mkdir_syscall('/bar/baz/yaargh',0)

stat_result = lind_fs_calls.stat_syscall('/bar/baz')

# ensure the mode is a dir with all bits on.
assert(stat_result[2] == S_IRWXA | S_IFDIR)


stat_result = lind_fs_calls.stat_syscall('/bar/baz/yaargh')

# ensure the mode is a dir with all bits on.
assert(stat_result[2] == S_IFDIR)

