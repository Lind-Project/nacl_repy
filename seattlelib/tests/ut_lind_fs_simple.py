import lind_fs_calls

from lind_fs_constants import *

lind_fs_calls._blank_fs_init()

# / should exist.
lind_fs_calls.access_syscall('/',F_OK)

# / should be read / executable by other
lind_fs_calls.access_syscall('/',X_OK|R_OK)

stat_result = lind_fs_calls.stat_syscall('/')

# ensure there are 2 hard links to the root of an empty fs
assert(stat_result[3] == 2)
             

# ensure there is no associated size
assert(stat_result[7] == 0)


