"""

cmatthew, Feb, 2012

Test that a file system can be saved then re-opened.  This program
saves the file system.

ut_lind_fs_persistance_test.py reopens the filesystem and checks it

"""

import wrapped_lind_fs_calls as lind_fs_calls
import os
from lind_fs_constants import *

TEST_FILENAME = "/someSimpleFileName"
TEST2_FILENAME = "/otherSimpleFileName2"



if __name__ == '__main__':

    lind_fs_calls._blank_fs_init()

    # Everything is okay, so now make a file
    myfd = lind_fs_calls.open_syscall(TEST_FILENAME, \
                                      O_CREAT | O_EXCL | O_RDWR, S_IRWXA)

    # write should succeed
    assert(lind_fs_calls.write_syscall(myfd, 'hello there!') == 12)

    # seek to the beginning...
    assert(lind_fs_calls.lseek_syscall(myfd, 0, SEEK_SET) == 0)

    # read the first 5 bytes (hello)
    assert(lind_fs_calls.read_syscall(myfd, 5) == 'hello')

    # change it to hello world!
    assert(lind_fs_calls.write_syscall(myfd, ' world') == 6)

    # seek to the beginning again...
    assert(lind_fs_calls.lseek_syscall(myfd, 0, SEEK_SET) == 0)

    # and read it all...
    assert(lind_fs_calls.read_syscall(myfd, 100) == 'hello world!')

    lind_fs_calls.close_syscall(myfd)

    # Now make and remove a file:
    myfd = lind_fs_calls.open_syscall(TEST2_FILENAME, \
                                      O_CREAT | O_EXCL | O_RDWR, S_IRWXA)

    # write should succeed
    message = '================================================================================================================================'
    assert(lind_fs_calls.write_syscall(myfd, message) == len(message))

    lind_fs_calls.close_syscall(myfd)

    lind_fs_calls.unlink_syscall(TEST2_FILENAME)

    lind_fs_calls.persist_metadata(DEFAULT_METADATA_FILENAME)

    # ensure the metadata exists...
    assert(os.access(DEFAULT_METADATA_FILENAME, os.W_OK))
