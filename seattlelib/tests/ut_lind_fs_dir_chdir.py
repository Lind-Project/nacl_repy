import wrapped_lind_fs_calls as lind_fs_calls
from lind_fs_constants import *

# Let's add a few directories to the system and see if it works...
lind_fs_calls._blank_fs_init()

lind_fs_calls.mkdir_syscall('/bar',S_IRWXA)

lind_fs_calls.mkdir_syscall('/bar/baz',S_IRWXA)

lind_fs_calls.mkdir_syscall('/bar/baz/yaargh',0)

lind_fs_calls.access_syscall('bar',F_OK)

# go to bar and look for baz...
lind_fs_calls.chdir_syscall('bar')

lind_fs_calls.access_syscall('baz',F_OK)

# go to back up and look bar...
lind_fs_calls.chdir_syscall('..')

lind_fs_calls.access_syscall('bar',F_OK)

# go to the yaargh dir
lind_fs_calls.chdir_syscall('/bar/baz/yaargh')

lind_fs_calls.access_syscall('../../baz',F_OK)

