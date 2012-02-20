"""

cmatthew, Feb, 2012

Test that a file system can be saved then re-opened.  This program
re-opens the filesystem and checks the file is there.

See ut_lind_fs_persistance_setup.py for filesystem init

"""

import wrapped_lind_fs_calls as lind_fs_calls
import os
import sys
from lind_fs_constants import *
from ut_lind_fs_persistance_setup import TEST_FILENAME

SyscallError = lind_fs_calls.SyscallError

if not os.access(DEFAULT_METADATA_FILENAME, os.W_OK):
  print "Must run ut_lind_fs_persistance_setup.py first!!!"
  sys.exit(1)

lind_fs_calls.restore_metadata(DEFAULT_METADATA_FILENAME)

# Everything is okay, so now make a file

try:
    myfd = lind_fs_calls.open_syscall(TEST_FILENAME, \
                                     O_CREAT | O_EXCL | O_RDWR, S_IRWXA)
except SyscallError:
    pass
else:
    assert False, "This file should exist!"
