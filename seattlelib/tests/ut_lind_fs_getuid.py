"""
File : ut_lind_fs_getuid.py

Unit test for getuid, geteuid, getgid, getegid.
"""

import lind_test_server

SyscallError = lind_test_server.SyscallError

assert lind_test_server.get_fscall_obj(-1).getuid_syscall() == 1000, "getuid failed to return."
assert lind_test_server.get_fscall_obj(-1).geteuid_syscall() == 1000, "geteuid failed to return."
assert lind_test_server.get_fscall_obj(-1).getgid_syscall() == 1000, "getgid failed to return."
assert lind_test_server.get_fscall_obj(-1).getegid_syscall() == 1000, "getegid failed to return."
