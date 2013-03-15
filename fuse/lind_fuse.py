#!/usr/bin/env python

#    Chris Matthews - University of Victoria - July 2012

import sys
import os
import stat
import runonce

# We need lind_test_server.py, lind_fs_calls.py and lind_fs_constants.py.
# They should be in the REPY_PATH OR copy them in to this folder so python
# can import the lind_test_server

# add repy install path to script
repy_path = os.getenv("REPY_PATH")

if repy_path == None:
    # if not set, use the location of this file.
    (lind_fuse_path, name) = os.path.split(os.path.abspath(__file__))
    os.environ['REPY_PATH'] = lind_fuse_path
    code_path = lind_fuse_path
else:
    # If it is set, use the standard lind path
    code_path = os.path.join(repy_path, "repy/")

sys.path.append(code_path)


# change dir so the execfile in test server works
pwd = os.getcwd()
os.chdir(code_path)
import lind_test_server as lind
# and now back to where we started.
os.chdir(pwd)


# pull in some spaghetti to make this stuff work without
# fuse-py being installed
try:
    import _find_fuse_parts
except ImportError:
    pass

import fuse
from fuse import Fuse

LOGGING = False


def log(*messages):
    if LOGGING:
        print ' '.join(map(str, messages))


# Convert a string errno value to the numeric value
# see the POSIX errno.h for the real thing
errno = {
    'EPERM': 1,	# Operation not permitted
    'ENOENT': 2, # No such file or directory
    'ESRCH': 3,	# No such process
    'EINTR': 4,	# Interrupted system call
    'EIO': 5,	# I/O error
    'ENXIO': 6,	# No such device or address
    'E2BIG': 7,	# Argument list too long
    'ENOEXEC': 8,	# Exec format error
    'EBADF': 9,	# Bad file number
    'ECHILD': 10,	# No child processes
    'EAGAIN': 11,	# Try again
    'ENOMEM': 12,	# Out of memory
    'EACCES': 13,	# Permission denied
    'EACESS': 13,	# Permission denied
    'EFAULT': 14,	# Bad address
    'ENOTBLK': 15,	# Block device required
    'EBUSY': 16,	# Device or resource busy
    'EEXIST': 17,	# File exists
    'EXDEV': 18,	# Cross-device link
    'ENODEV': 19,	# No such device
    'ENOTDIR': 20,	# Not a directory
    'EISDIR': 21,	# Is a directory
    'EINVAL': 22,	# Invalid argument
    'ENFILE': 23,	# File table overflow
    'EMFILE': 24,	# Too many open files
    'ENOTTY': 25,	# Not a typewriter
    'ETXTBSY': 26,	# Text file busy
    'EFBIG': 27,	# File too large
    'ENOSPC': 28,	# No space left on device
    'ESPIPE': 29,	# Illegal seek
    'EROFS': 30,	# Read-only file system
    'EMLINK': 31,	# Too many links
    'EPIPE': 32,	# Broken pipe
    'EDOM': 33,	# Math argument out of domain of func
    'ERANGE': 34,	# Math result not representable

    'EDEADLK': 35,	# Resource deadlock would occur
    'ENAMETOOLONG': 36,	# File name too long
    'ENOLCK': 37,  # No record locks available
    'ENOSYS': 38,	# Function not implemented
    'ENOTEMPTY': 39,	# Directory not empty
    'ELOOP': 40,	# Too many symbolic links encountered
#    'EWOULDBLOCK': EAGAIN,	# Operation would block
    'ENOMSG': 42,	# No message of desired type
    'EIDRM': 43,	# Identifier removed
    'ECHRNG': 44,	# Channel number out of range
    'EL2NSYNC': 45,	# Level 2 not synchronized
    'EL3HLT': 46,	# Level 3 halted
    'EL3RST': 47,	# Level 3 reset
    'ELNRNG': 48,	# Link number out of range
    'EUNATCH': 49,	# Protocol driver not attached
    'ENOCSI': 50,	# No CSI structure available
    'EL2HLT': 51,	# Level 2 halted
    'EBADE': 52,	# Invalid exchange
    'EBADR': 53,	# Invalid request descriptor
    'EXFULL': 54,	# Exchange full
    'ENOANO': 55,	# No anode
    'EBADRQC': 56,	# Invalid request code
    'EBADSLT': 57,	# Invalid slot
    'EBFONT': 59,	# Bad font file format
    'ENOSTR': 60,	# Device not a stream
    'ENODATA': 61,	# No data available
    'ETIME': 62,	# Timer expired
    'ENOSR': 63,	# Out of streams resources
    'ENONET': 64,	# Machine is not on the network
    'ENOPKG': 65,	# Package not installed
    'EREMOTE': 66,	# Object is remote
    'ENOLINK': 67,	# Link has been severed
    'EADV': 68,	# Advertise error
    'ESRMNT': 69,	# Srmount error
    'ECOMM': 70,	# Communication error on send
    'EPROTO': 71,	# Protocol error
    'EMULTIHOP': 72,	# Multihop attempted
    'EDOTDOT': 73,	# RFS specific error
    'EBADMSG': 74,	# Not a data message
    'EOVERFLOW': 75,	# Value too large for defined data type
    'ENOTUNIQ': 76,	# Name not unique on network
    'EBADFD': 77,	# File descriptor in bad state
    'EREMCHG': 78,	# Remote address changed
    'ELIBACC': 79,	# Can not access a needed shared library
    'ELIBBAD': 80,	# Accessing a corrupted shared library
    'ELIBSCN': 81,	# .lib section in a.out corrupted
    'ELIBMAX': 82,	# Attempting to link in too many shared libraries
    'ELIBEXEC': 83,	# Cannot exec a shared library directly
    'EILSEQ': 84,	# Illegal byte sequence
    'ERESTART': 85,	# Interrupted system call should be restarted
    'ESTRPIPE': 86,	# Streams pipe error
    'EUSERS': 87,	# Too many users
    'ENOTSOCK': 88,	# Socket operation on non-socket
    'EDESTADDRREQ': 89,	# Destination address required
    'EMSGSIZE': 90,	# Message too long
    'EPROTOTYPE': 91,	# Protocol wrong type for socket
    'ENOPROTOOPT': 92,	# Protocol not available
    'EPROTONOSUPPORT': 93,	# Protocol not supported
    'ESOCKTNOSUPPORT': 94,	# Socket type not supported
    'EOPNOTSUPP': 95,	# Operation not supported on transport endpoint
    'EPFNOSUPPORT': 96,	# Protocol family not supported
    'EAFNOSUPPORT': 97,	# Address family not supported by protocol
    'EADDRINUSE': 98,	# Address already in use
    'EADDRNOTAVAIL': 99,	# Cannot assign requested address
    'ENETDOWN': 100,	# Network is down
    'ENETUNREACH': 101,	# Network is unreachable
    'ENETRESET': 102,	# Network dropped connection because of reset
    'ECONNABORTED': 103,	# Software caused connection abort
    'ECONNRESET': 104,	# Connection reset by peer
    'ENOBUFS': 105,	# No buffer space available
    'EISCONN': 106,	# Transport endpoint is already connected
    'ENOTCONN': 107,	# Transport endpoint is not connected
    'ESHUTDOWN': 108,	# Cannot send after transport endpoint shutdown
    'ETOOMANYREFS': 109,	# Too many references: cannot splice
    'ETIMEDOUT': 110,	# Connection timed out
    'ECONNREFUSED': 111,	# Connection refused
    'EHOSTDOWN': 112,	# Host is down
    'EHOSTUNREACH': 113,	# No route to host
    'EALREADY': 114,	# Operation already in progress
    'EINPROGRESS': 115,	# Operation now in progress
    'ESTALE': 116,	# Stale NFS file handle
    'EUCLEAN': 117,	# Structure needs cleaning
    'ENOTNAM': 118,	# Not a XENIX named type file
    'ENAVAIL': 119,	# No XENIX semaphores available
    'EISNAM': 120,	# Is a named type file
    'EREMOTEIO': 121,	# Remote I/O error
    'EDQUOT': 122,	# Quota exceeded
    'ENOMEDIUM': 123,	# No medium found
    'EMEDIUMTYPE': 124,	# Wrong medium type
    'ECANCELED': 125,	# Operation Canceled
    'ENOKEY': 126,	# Required key not available
    'EKEYEXPIRED': 127,	# Key has expired
    'EKEYREVOKED': 128,	# Key has been revoked
    'EKEYREJECTED': 129,	# Key was rejected by service
    # for robust mutexes
    'EOWNERDEAD': 130,	# Owner died
    'ENOTRECOVERABLE': 131} # State not recoverable


if not hasattr(fuse, '__version__'):
    raise RuntimeError("your fuse-py doesn't know of fuse.__version__,"
                       " probably it's too old.")


fuse.fuse_python_api = (0, 2)


fuse.feature_assert('stateful_files', 'has_init')


class LindFileStat(fuse.Stat):
    """ File attributes.

    See stat and fstat.

    http://linux.die.net/man/2/stat

    """

    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0


class LindFileStatFS(fuse.Stat):
    """File system attributes.

    See man statfs and fstatfs.

    http://linux.die.net/man/2/fstatfs

    """

    def __init__(self):
        self.f_bsize = 0  # preferred size of file  blocks, in bytes
        self.f_frsize = 0  # fundamental size of file blcoks, in bytes
        self.f_blocks = 0  # total number of blocks in the filesystem
        self.f_bfree = 0  # number of free blocks
        self.f_files = 0  # total number of file inodes
        self.f_ffree = 0  # number of free file inodes


class LindFuseFS(Fuse):

    def __init__(self, *args, **kw):

        Fuse.__init__(self, *args, **kw)

        # You can enable multithreading here
        #import thread
        #thread.start_new_thread(self.mythread, ())
        self.root = '/'

    def getattr(self, path):
        log("getattr", path)
        try:
            stats = lind.stat_syscall(path)
        except lind.SyscallError, e:
            return -errno[e[1]]
        devid, inode, mode, linkcount, uid, gid, rdev, size, blocksize,\
               blocks, atime, atimens, mtime, mtimens, ctime, \
               ctimens = stats
        st = LindFileStat()

        # treat root specially
        if path == '/':
            st.st_mode = stat.S_IFDIR | 0755
            st.st_nlink = 2
        else:
            st.st_mode = mode # stat.S_IFREG | 0444
            st.st_nlink = linkcount
            st.st_size = size
            st.st_dev = devid
            st.st_uid = uid
            st.st_gid = gid
            st.st_ino = inode
            st.st_atime = atime
            st.st_ctime = ctime
            st.st_mtime = mtime

        return st

    def readlink(self, path):
        log("readlink (unimplemented)", path)
        return - errno["ENOSYS"]

    def readdir(self, path, offset):
        log("readdir", path, offset)
        lindfd = lind.open_syscall(path, lind.O_RDONLY, lind.S_IRWXU)
        dents = map(lambda x: x[1], lind.getdents_syscall(lindfd, 999))

        assert len(dents) < 998, "Readdir max was hit..."
        for e in dents:
            yield fuse.Direntry(e)

    def unlink(self, path):
        log("unlink", path)
        try:
            ret = lind.unlink_syscall(path)
        except lind.SyscallError, e:
            ret = -errno[e[1]]
        return ret

    def rmdir(self, path):
        log("rmdir", path)
        try:
            ret = lind.rmdir_syscall(path)
        except lind.SyscallError, e:
            ret = -errno[e[1]]
        return ret

    def symlink(self, path, path1):
        log("symlink", path, path1)
        try:
            ret = lind.link_syscall(path, path1)
        except lind.SyscallError, e:
            ret = -errno[e[1]]
        return ret

    def rename(self, path, path1):
        log("rename", path, path1)
        try:
            ret = lind.rename_syscall(path, path1)
        except lind.SyscallError, e:
            ret = -errno[e[1]]
        return ret

    def link(self, path, path1):
        log("link", path, path1)
        try:
            ret = lind.link_syscall(path, path1)
        except lind.SyscallError, e:
            ret = -errno[e[1]]
        return ret

    def chmod(self, path, mode):
        log("chmod", path, hex(mode))
        try:
            ret = lind.chmod_syscall(path, mode)
        except lind.SyscallError, e:
            ret = -errno[e[1]]
        return ret
        

    def chown(self, path, user, group):
        log("chown (unimplemented)", path, user, group)
        return -errno["ENOSYS"]

    def truncate(self, path, length):
	log("truncate", path, length)
        try:
            ret = lind.truncate_syscall(path, length)
        except lind.SyscallError, e:
            ret = -errno[e[1]]
        return ret

    def mknod(self, path, mode, dev):
        log("mknod (unimplemented)", path, mode, dev)
        return -errno["ENOSYS"]

    def mkdir(self, path, mode):
        log("mkdir", path, mode)
        try:
            ret = lind.mkdir_syscall(path, mode)
        except lind.SyscallError, e:
            ret = -errno[e[1]]
        return ret

    def utime(self, path, times):
        log("utime (unimplemented)", path, times)

    def access(self, path, mode):
        log("access", path, hex(mode))
        try:
            ret = lind.access_syscall(path, mode)
        except lind.SyscallError, e:
            ret = -errno[e[1]]
        return ret

    def statfs(self):
        log("statfs")
        try:
            stats = lind.statfs_syscall("/")
        except lind.SyscallError, e:
            return -errno[e[1]]

        st = LindFileStatFS()
        st.f_bsize = stats['f_bsize']
        st.f_frsize = stats['f_frsize']
        st.f_blocks = stats['f_blocks']
        st.f_bfree = stats['f_bfree']
        st.f_files = stats['f_files']
        st.f_ffree = stats['f_ffree']

        return st

    def fsinit(self):
        print "Starting Lindfs"

    class LindFuseFSFile(object):
        """For each open file in the FS, there will be one of these."""

        def __init__(self, path, flags, *mode):
            log("open", path, hex(flags))
            self.direct_io = False
            self.keep_cache = False
            lindfd = lind.open_syscall(path, flags, lind.S_IRWXA)

            self.fd = lindfd

        def read(self, length, offset):
            log("read", self.fd, length, offset)
            try:
                lind.lseek_syscall(self.fd, offset, 0)
                ret = lind.read_syscall(self.fd, length)
            except lind.SyscallError, e:
                ret = -errno[e[1]]

            return ret

        def write(self, buf, offset):
            log("write", self.fd, buf, offset)
            try:
                lind.lseek_syscall(self.fd, offset, 0)
                ret = lind.write_syscall(self.fd, buf)
            except lind.SyscallError, e:
                ret = -errno[e[1]]
            return ret

        def release(self, flags):
            log("close", self.fd, flags)
            return lind.close_syscall(self.fd)

        def _fflush(self):
            log("flush", self.fd)
            return 0

        def fsync(self, isfsyncfile):
            log("fsync", self.fd, isfsyncfile)
            lind.persist_metadata("lind.metadata")
            return 0

        def flush(self):
            return self._fflush()

        def fgetattr(self):
            log("fstat", self.fd)
            try:
                stats = lind.fstat_syscall(self.fd)
            except lind.SyscallError, e:
                return -errno[e[1]]
            devid, inode, mode, linkcount, uid, gid, rdev, size, blocksize,\
                   blocks, atime, atimens, mtime, mtimens, ctime,\
                   ctimens = stats
            st = LindFileStat()
            st.st_mode = mode # stat.S_IFREG | 0444
            st.st_nlink = linkcount
            st.st_size = size
            st.st_dev = devid
            st.st_uid = uid
            st.st_gid = gid
            st.st_ino = inode
            st.st_atime = atime
            st.st_ctime = ctime
            st.st_mtime = mtime

            return st

        def ftruncate(self, len):
            try:
                trunc = lind.ftruncate_syscall(self.fd, len)
            except lind.SyscallError, e:
                return -errno[e[1]]
            return trunc

        def lock(self, cmd, owner, **kw):
            return -errno["ENOSYS"]

    def main(self, *a, **kw):

        self.file_class = self.LindFuseFSFile

        return Fuse.main(self, *a, **kw)


def main():
    global LOGGING

    if "-v" in sys.argv or "--verbose" in sys.argv:
        LOGGING = True

    usage = """
Lind Fuse File System.

""" + Fuse.fusage

    lind.load_fs()
    
    gotlock = runonce.getprocesslock('lind_fuse')
    if gotlock == True:
      pass
    else:
      if gotlock:
        print "\n\n#########################################################"
        print "[Warning] Another Process (pid: " + str(gotlock) + ") already in use."
        print "#########################################################\n\n"
      else:
        print "[Warning] Another Process is running"

    server = LindFuseFS(version="%prog " + fuse.__version__,
                 usage=usage,
                 dash_s_do='setsingle')

    server.multithreaded = False  # if this is true, better add some locks!

    server.parser.add_option("-v", "--verbose",
                             action="store_true",
                             dest="verbose",
                             default=False,
                             help="print extra information about which system"
                             " calls are being called.")

    server.parser.add_option(mountopt="root", metavar="PATH", default='/',
                             help="mirror filesystem from under PATH "
                             "[default: %default]")
    server.parse(values=server, errex=1)

    server.main()
    lind.persist_metadata("lind.metadata")


if __name__ == '__main__':
    main()
