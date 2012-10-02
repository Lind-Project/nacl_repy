"""
  Author: Justin Cappos
  Module: File system constants for Lind.   This is things like the mode bits
          and macros.

  Start Date: December 17th, 2011

"""

# Mostly used with access()
F_OK = 0
X_OK = 1
W_OK = 2
R_OK = 4


O_RDONLY = 00
O_WRONLY = 01
O_RDWR = 02

# we will use this to get the flags
O_RDWRFLAGS = O_RDONLY | O_WRONLY | O_RDWR

O_CREAT = 0100
O_EXCL = 0200
O_NOCTTY = 0400
O_TRUNC = 01000
O_APPEND = 02000
O_NONBLOCK = 04000
# O_NDELAY=O_NONBLOCK
O_SYNC = 010000
# O_FSYNC=O_SYNC
O_ASYNC = 020000
O_CLOEXEC = 02000000

S_IRWXA = 00777
S_IRWXU = 00700
S_IRUSR = 00400
S_IWUSR = 00200
S_IXUSR = 00100
S_IRWXG = 00070
S_IRGRP = 00040
S_IWGRP = 00020
S_IXGRP = 00010
S_IRWXO = 00007
S_IROTH = 00004
S_IWOTH = 00002
S_IXOTH = 00001


# file types for open / stat, etc.
S_IFBLK = 24576
S_IFCHR = 8192
S_IFDIR = 16384
S_IFIFO = 4096
S_IFLNK = 40960
S_IFREG = 32768
S_IFSOCK = 49152

# the above type mode is these 4 bits.   I want to be able to pull them out...
S_FILETYPEFLAGS = 2**12 + 2**13 + 2**14 + 2**15

S_IWRITE = 128
S_ISUID = 2048
S_IREAD = 256
S_ENFMT = 1024
S_ISGID = 1024

SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2

F_DUPFD = 0
F_GETFD = 1
F_SETFD = 2
F_GETFL = 3
F_SETFL = 4
F_GETLK = 5
F_GETLK64 = 5
F_SETLK = 6
F_SETLK64 = 6
F_SETLKW = 7
F_SETLKW64 = 7
F_SETOWN = 8
F_GETOWN = 9
F_SETSIG = 10
F_GETSIG = 11
F_SETLEASE = 1024
F_GETLEASE = 1025
F_NOTIFY = 1026

# for fcntl to manipulate file descriptor flags..
FD_CLOEXEC = 02000000

# for the lock calls
F_RDLCK = 0
F_WRLCK = 1
F_UNLCK = 2
F_EXLCK = 4
F_SHLCK = 8

# for flock syscall
LOCK_SH = 1
LOCK_EX = 2
LOCK_UN = 8
LOCK_NB = 4


# the longest path in Linux
PATH_MAX = 4096

#largest file descriptor
MAX_FD = 1024
STARTINGFD = 10


# for dirents...
DEFAULT_UID=1000
DEFAULT_GID=1000

# when saving the metadata file on disk,
# what name should we use:
DEFAULT_METADATA_FILENAME = "lind.metadata"



# convert file mode (S_) to dirent type (D_SIR_)
def get_direnttype_from_mode(mode):
  if IS_DIR(mode):
    return DT_DIR
  if IS_REG(mode):
    return DT_REG
  if IS_SOCK(mode):
    return DT_SOCK

  # otherwise, return unknown for now...
  return DT_UNKNOWN


# types for getdents d_type field

#default
DT_UNKNOWN = 0

#named pipe
DT_FIFO = 1

#character device
DT_CHR = 2

#directory
DT_DIR = 4

#block device
DT_BLK = 6

# regular file
DT_REG = 8

#link
DT_LNK = 10

# unix domain socket
DT_SOCK = 12

# dont know what this is for?!  but it is in dirent.h
DT_WHT = 14

# default name for metadata
DEFAULT_METADATA_FILENAME = "lind.metadata"


# some MACRO helpers...
def IS_DIR(mode):
  if mode & S_FILETYPEFLAGS == S_IFDIR:
    return True
  else:
    return False

def IS_REG(mode):
  if mode & S_FILETYPEFLAGS == S_IFREG:
    return True
  else:
    return False


def IS_CHR(mode):
  return (mode & S_FILETYPEFLAGS) == S_IFCHR


def IS_SOCK(mode):
  if mode & S_FILETYPEFLAGS == S_IFSOCK:
    return True
  else:
    return False


def IS_RDONLY(flags):
  if flags & O_RDWRFLAGS == O_RDONLY:
    return True
  else:
    return False


def IS_WRONLY(flags):
  if flags & O_RDWRFLAGS == O_WRONLY:
    return True
  else:
    return False


def IS_RDWR(flags):
  if flags & O_RDWRFLAGS == O_RDWR:
    return True
  else:
    return False

def IS_NONBLOCKING(fd_flags, recv_flags):
  if ((fd_flags & O_NONBLOCK) != 0) or ((recv_flags & O_NONBLOCK) != 0):
    return True
  else:
    return False
