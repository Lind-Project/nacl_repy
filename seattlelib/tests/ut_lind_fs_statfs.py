import lind_test_server

from lind_fs_constants import *

lind_test_server._blank_fs_init(-1)

# / should exist.
statfsdict = lind_test_server.get_fs_call(-1,"statfs_syscall")('/')

assert(statfsdict['f_type']==0xBEEFC0DE)
assert(statfsdict['f_bsize']==4096)


