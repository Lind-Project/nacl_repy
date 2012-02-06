"""

cmatthew, Feb, 2012

Test that a file system can be saved then re-opened.  This program
re-opens the filesystem and checks the file is there.

See ut_lind_fs_persistance_setup.py for filesystem init

"""

import wrapped_lind_fs_calls as lind_fs_calls
import os
from lind_fs_constants import *
from ut_lind_fs_persistance_setup import TEST_FILENAME

print "Found Metadata? ", os.access(DEFAULT_METADATA_FILENAME, os.W_OK)

lind_fs_calls.restore_metadata(DEFAULT_METADATA_FILENAME)

# Everything is okay, so now make a file

myfd = lind_fs_calls.open_syscall(TEST_FILENAME, \
                                  O_CREAT | O_EXCL | O_RDWR, S_IRWXA)


assert(lind_fs_calls.read_syscall(myfd, 100) == 'hello world!')

lind_fs_calls.close_syscall(myfd)

lind_fs_calls.persist_metadata(DEFAULT_METADATA_FILENAME)
