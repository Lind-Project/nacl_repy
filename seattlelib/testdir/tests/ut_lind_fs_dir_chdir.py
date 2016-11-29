from lind_fs_constants import *
import lind_test_server

# Let's add a few directories to the system and see if it works...
lind_test_server._blank_fs_init()

lind_test_server.mkdir_syscall('/bar',S_IRWXA)

lind_test_server.mkdir_syscall('/bar/baz',S_IRWXA)

lind_test_server.mkdir_syscall('/bar/baz/yaargh',0)

lind_test_server.access_syscall('bar',F_OK)

# go to bar and look for baz...
lind_test_server.chdir_syscall('bar')

lind_test_server.access_syscall('baz',F_OK)

# go to back up and look bar...
lind_test_server.chdir_syscall('..')

lind_test_server.access_syscall('bar',F_OK)

# go to the yaargh dir
lind_test_server.chdir_syscall('/bar/baz/yaargh')

lind_test_server.access_syscall('../../baz',F_OK)

