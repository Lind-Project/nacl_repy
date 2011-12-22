import wrapped_lind_fs_calls as lind_fs_calls

from lind_fs_constants import *

lind_fs_calls._blank_fs_init()

# / should exist.
statfsdict = lind_fs_calls.statfs_syscall('/')

assert(statfsdict['f_type']==0xBEEFC0DE)
assert(statfsdict['f_bsize']==4096)


