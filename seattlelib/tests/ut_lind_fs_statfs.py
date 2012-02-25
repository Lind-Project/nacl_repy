import lind_test_server

from lind_fs_constants import *

lind_test_server._blank_fs_init()

# / should exist.
statfsdict = lind_test_server.statfs_syscall('/')

assert(statfsdict['f_type']==0xBEEFC0DE)
assert(statfsdict['f_bsize']==4096)


