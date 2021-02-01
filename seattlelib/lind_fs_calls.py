"""
  Author: Justin Cappos
  Module: File system calls for Lind.   This is essentially POSIX written in
          Repy V2.

  Start Date: December 17th, 2011

  My goal is to write a simple and relatively accurate implementation of POSIX
  in Repy V2.   This module contains most of the file system calls.   A lind
  client can execute those calls and they will be mapped into my Repy V2
  code where I will more or less faithfully execute them.   Since Repy V2
  does not support permissions, directories, etc., I will fake these.   To
  do this I will create a metadata file / dictionary which contains
  metadata of this sort.   I will persist this metadata and re-read it upon
  initialization.

  Rather than do all of the struct packing, etc. here, I will do it in another
  routine.   The reason is that I want to be able to test this in Python / Repy
  without unpacking / repacking.

"""

import lindpipe

# At a conceptual level, the system works like this:
#   1) Files are written and managed by my program.   The actual name on disk
#      will not correspond in any way with the filename.   The name on disk
#      is chosen by my code and the filename only appears in the metadata.
#   2) A dictionary exists which stores file data.   Since there may be
#      multiple hard links to a file, the dictionary is keyed by "inode"
#      instead of filename.   The value of each entry is a dictionary that
#      contains the file mode data, size, link count, owner, group, and other
#      information.
#   3) The metadata for every directory contains a list of filenames in that
#      directory and their associated "inodes".
#   4) "Inodes" are simply unique ids per file and have no other meaning.
#      They are generated sequentially.
#   5) Every open file has an entry in the filedescriptortable.   This
#      is a dictionary that is keyed by fd, with the values consisting of
#      a dictionary with the position, flags, a lock, and inode keys.
#      The inode values are used to update / check the file size after writeat
#      calls and for calls like fstat.
#   6) A file's data is mapped the filename FILEDATAPREFIX+str(inode)
#   7) Open file objects are kept in a separate table, the fileobjecttable that
#      is keyed by inode.  This makes it easier to support multiple open file
#      descriptors that point to the same file.
#
# BUG: I created a table which allows one to look up an "inode"
#      given a filename.   It will break certain things in certain weird corner
#      cases with dir symlinks, permissions, etc.   However, it will make the
#      code simpler and faster
#   I called it: fastinodelookuptable = {}
#
#   As with Linux, etc. there is a 'current directory' that calls which take a
#      filename use as the first part of their path.   All other filenames that
#      do not begin with '/' start from here.
#
# Here is how some example calls work at a high level:
#   unlink: removes filename -> inode map / decrements the link count.  If
#           the link count is zero, deletes the file.
#   link: increments the link count and adds a new filename -> inode map.
#   rename: updates the directory's filename -> inode map.
#   getdents: returns data from the directory's filename -> inode map.
#   mkdir / rmdir: creates a directory / removes a directory
#   chdir: sets the current directory for other calls
#   stat / access: provides metadata about a file / directory / etc.
#   open: makes an entry in the file descriptor table for a file
#   read / write: use the file descriptor to perform the action
#   lseek: update the file descriptor table entry for position.


# I'm not overly concerned about efficiency right now.   I'm more worried
# about correctness.   As a result, I'm not going to optimize anything yet.
#


# To describe the metadata format, I'll start at the lowest levels and build
# up.   At a conceptual level, files, directories, symlinks, etc. are at the
# bottom level.   Directories contain references to files, symlinks, and other
# directories.   These are all entries in a table keyed by inode.
#
# A file's metadata looks like this:
#
# {'size':1033, 'uid':1000, 'gid':1000, 'mode':33261, 'linkcount':2,
#  'atime':1323630836, 'ctime':1323630836, 'mtime':1323630836}
# See the stat command for more information about what these mean...
#
#
# A directory's metadata looks very similar:
# {'size':1033, 'uid':1000, 'gid':1000, 'mode':16877,
#  'atime':1323630836, 'ctime':1323630836, 'mtime':1323630836,
#  'linkcount':4,    # the number of dir entries...
#  'filename_to_inode_dict': {'foo':1234, '.':102, '..':10, 'bar':2245}
# See the stat command for more information about what these mean...
#
#
# Symbolic links, devices, etc. will be done later (if needed)
#
#
# These are all entries in the inode table.   It is keyed by inode and maps
# to these entries.   The root directory is always at position
# ROOTDIRECTORYINODE.
#
#
# At the highest level, the metadata is in a dictionary like this:
#
# filesystemmetadata = {'nextinode':1201,   # the next unused inode number
#                       'dev_id':20,        # the device ID returned to stat
#                       'inodetable': {...} # described above
#

# Store all of the information about the file system in a dict...
# This should not be 0 because this is considered to be deleted



import time
import thread

class AtomicCounter:
    def __init__(self, initial=0):
        """Initialize a new atomic counter to given initial value (default 0)."""
        self.value = initial
        self.lock = createlock()

    def increment(self, num=1):
        """Atomically increment the counter by num (default 1) and return the
        new value.
        """
        self.lock.acquire(True)
        self.value += num
        self.lock.release()
        return self.value


global_call_counter = AtomicCounter()

call_log = {}

thread_callcounter = {}




def init_log_entry(call_num):
  global call_log
  global global_call_counter

  threadid = thread.get_ident()
  curr_count = (global_call_counter.increment(1)) - 1

  thread_callcounter[threadid] = curr_count
  call_log[curr_count] = {}




  callstring = str(call_num)
  if (call_num == 10): callstring = "open"
  if (call_num == 14): callstring = "seek"
  if (call_num == 12): callstring = "read"
  if (call_num == 13): callstring = "write"
  if (call_num == 11): callstring = "close"
  if (call_num == 17): callstring = "fstat"
  if (call_num == 9): callstring = "stat"
  if (call_num == 21): callstring = "mmap"
  if (call_num == 30): callstring = "exit"
  if (call_num == 2): callstring = "access"
  if (call_num == 3): callstring = "trace"
  if (call_num == 23): callstring = "getdents"
  if (call_num == 69): callstring = "exec"
  if (call_num == 68): callstring = "fork"
  if (call_num == 66): callstring = "pipe"
  if (call_num == 25): callstring = "dup2"
  if (call_num == 50): callstring = "getuid"
  if (call_num == 51): callstring = "geteuid"
  if (call_num == 52): callstring = "getgid"
  if (call_num == 53): callstring = "getegid"
  if (call_num == 24): callstring = "dup"
  if (call_num == 32): callstring = "socket"
  if (call_num == 31): callstring = "getpid"



  call_log[curr_count]["call"] = callstring



def add_cageid_log(cagenum):
  global call_log
  call_counter = thread_callcounter[thread.get_ident()]
  call_log[call_counter]["cageid"] = cagenum


def add_to_log(handle, time):
  global call_log
  call_counter = thread_callcounter[thread.get_ident()]
  call_log[call_counter][handle] = time


def print_log():
  global call_log
  global global_call_counter


  total_syscall_time = 0
  total_fs_time = 0

  print call_log
#   for i in range(0, global_call_counter.value):
#     curr = call_log[i]
#     logstring = "Syscall " + curr["call"]
#     if "cageid" in curr: logstring += " Cage " + str(curr["cageid"]) 
#     logstring += " syscall time " + str(curr["syscall"] * 1000000) + " us"
#     if "stub" in curr: logstring += " stub time " + str(curr["stub"] * 1000000) + " us"
#     if "fs_call" in curr: logstring += " fs call time " + str(curr["fs_call"] * 1000000) + " us"
#     total_syscall_time += curr["syscall"]
#     if "fs_call" in curr: total_fs_time += curr["fs_call"]
# #    print logstring

  print "Total system call time " + str(total_syscall_time * 1000000) + " us"
  print "Total pure implementation time " + str(total_fs_time * 1000000) + " us"

ROOTDIRECTORYINODE = 1
STREAMINODE = 2

METADATAFILENAME = 'lind.metadata'

FILEDATAPREFIX = 'linddata.'

filesystemmetadata = {}

# A lock that prevents inconsistencies in metadata
filesystemmetadatalock = createlock()


# fast lookup table...   (Should I deprecate this?)
#this is a dictionary of lookup tables
fastinodelookuptable = {}

# contains file objects... (keyed by inode)
#this is a dictionary of dictionaries of file objects
fileobjecttable = {}

# contains pipe implementaion
#this is a dictionary of pipes which contains data and appropriate locks
pipetable = {}

#this is a dictionary of cage objects
master_cage_context = {}

SILENT=True

def warning(*msg):
  if not SILENT:
    for part in msg:
      print part,
    print


# This is raised to return an error...
class SyscallError(Exception):
  """A system call had an error"""


# This is raised if part of a call is not implemented
class UnimplementedError(Exception):
  """A call was called with arguments that are not fully implemented"""

# A deepcopy implementation without importing the copy library
# Clones and calls itself recursively on allowed mutable data types
def repy_deepcopy(obj):
  o = type(obj)
  if o is dict: # Keys in dicts must be immutable
    newdict = {}
    for key, value in obj.iteritems():
      newdict[key] = repy_deepcopy(value)
    return newdict
  elif o is list:
    newlist = []
    for item in obj:
      newlist.append(repy_deepcopy(obj))
    return newlist
  elif o is set: # Sets may only contain immutable members
    return obj.copy()
  else:
    return obj #If obj is not one of the above three data types, it's immutable
  # or a user defined class which we don't know how to deal with (and may want to not clone)
  # Other mutable types (namely arrays) are banned by repy
    


def _load_lower_handle_stubs(table):
  """The lower file hadles need stubs in the descriptor talbe."""

  # we're going to give all streams an inode of 2 since lind is emulating a single "terminal"

  table[0] = {'position':0, 'inode':STREAMINODE, 'lock':createlock(), 'flags':O_RDONLY, 'stream':0, 'note':'this is a stdin'}
  table[1] = {'position':0, 'inode':STREAMINODE, 'lock':createlock(), 'flags':O_WRONLY, 'stream':1, 'note':'this is a stdout'}
  table[2] = {'position':0, 'inode':STREAMINODE, 'lock':createlock(), 'flags':O_WRONLY, 'stream':2, 'note':'this is a stderr'}


def load_fs(cageid, name=METADATAFILENAME):
  """ Help to correcly load a filesystem, if one exists, otherwise
  make a new empty one.  To do this, check if metadata exists.
  If it doesnt, call _blank_fs_init, if it DOES exist call restore_metadata

  This is the best entry point for programs loading the file subsystem.
  """
  master_cage_context[cageid] = cageobj(cageid, '/')
  try:
    # lets see if the metadata file is already here?
    f = openfile(name, False)
  except FileNotFoundError, e:
    warning("Note: No filesystem found, building a fresh one.")
    _blank_fs_init()
  else:
    f.close()
  try:
    restore_metadata(name)
    load_fs_special_files(cageid)
  except (IndexError, KeyError), e:
    print "Error: Cannot reload filesystem.  Run lind_fsck for details."
    exitall(1)


def load_fs_special_files(cageid):
  """ If called adds special files in standard locations.
  Specifically /dev/null, /dev/zero, /dev/urandom and /dev/random
  """
  try:
     get_fscall_obj(cageid).mkdir_syscall("/dev", S_IRWXA)
  except SyscallError as e:
    warning( "making /dev failed. Skipping",str(e))

  # load /dev/null
  try:
    get_fscall_obj(cageid).mknod_syscall("/dev/null", S_IFCHR, (1,3))
  except SyscallError as e:
    warning("making /dev/null failed. Skipping", str(e))

  # load /dev/zero
  try:
    get_fscall_obj(cageid).mknod_syscall("/dev/zero", S_IFCHR, (1,5))
  except SyscallError as e:
    warning("making /dev/zero failed. Skipping", str(e))

  # load /dev/urandom
  try:
    get_fscall_obj(cageid).mknod_syscall("/dev/urandom", S_IFCHR, (1,9))
  except SyscallError as e:
    warning("making /dev/urandom failed. Skipping",str(e))

  # load /dev/random
  try:
    get_fscall_obj(cageid).mknod_syscall("/dev/random", S_IFCHR, (1,8))
  except SyscallError as e:
    warning("making /dev/random failed. Skipping", str(e))


# To have a simple, blank file system, simply run this block of code.
#
def _blank_fs_init():

  # kill all left over data files...
  # metadata will be killed on persist.
  for filename in listfiles():
    if filename.startswith(FILEDATAPREFIX):
      removefile(filename)

  # Now setup blank data structures
  # next inode starts after root and streams
  filesystemmetadata['nextinode'] = STREAMINODE + 1
  filesystemmetadata['dev_id'] = 20
  filesystemmetadata['inodetable'] = {}
  filesystemmetadata['inodetable'][ROOTDIRECTORYINODE] = {'size':0,
            'uid':DEFAULT_UID, 'gid':DEFAULT_GID,
            'mode':S_IFDIR | S_IRWXA, # directory + all permissions
            'atime':1323630836, 'ctime':1323630836, 'mtime':1323630836,
            'linkcount':2,    # the number of dir entries...
            'refcount': 0, # no open handles to the file
            'filename_to_inode_dict': {'.':ROOTDIRECTORYINODE,
            '..':ROOTDIRECTORYINODE}}

  fastinodelookuptable['/'] = ROOTDIRECTORYINODE

  # it makes no sense this wasn't done before...
  persist_metadata(METADATAFILENAME)



# These are used to initialize and stop the system
def persist_metadata(metadatafilename):

  metadatastring = serializedata(filesystemmetadata)


  # open the file (clobber) and write out the information...
  try:
    removefile(metadatafilename)
  except FileNotFoundError:
    pass
  metadatafo = openfile(metadatafilename,True)
  metadatafo.writeat(metadatastring,0)
  metadatafo.close()



def restore_metadata(metadatafilename):
  # should only be called with a fresh system...
  assert(filesystemmetadata == {})

  # open the file and write out the information...
  metadatafo = openfile(metadatafilename,True)
  metadatastring = metadatafo.readat(None, 0)
  metadatafo.close()

  # get the dict we want
  desiredmetadata = deserializedata(metadatastring)

  # I need to put things in the dict, but it's not a global...   so instead
  # add them one at a time.   It should be empty to start with
  for item in desiredmetadata:
    filesystemmetadata[item] = desiredmetadata[item]

  # I need to rebuild the fastinodelookuptable. let's do this!
  _rebuild_fastinodelookuptable()



# I'm already added.
def _recursive_rebuild_fastinodelookuptable_helper(path, inode):

  # for each entry in my table...
  for entryname,entryinode in filesystemmetadata['inodetable'][inode]['filename_to_inode_dict'].iteritems():

    # if it's . or .. skip it.
    if entryname == '.' or entryname == '..':
      continue

    # always add it...
    entrypurepathname = normpath2(path+'/'+entryname)
    fastinodelookuptable[entrypurepathname] = entryinode

    # and recurse if a directory...
    if 'filename_to_inode_dict' in filesystemmetadata['inodetable'][entryinode]:
      _recursive_rebuild_fastinodelookuptable_helper(entrypurepathname,entryinode)


def _rebuild_fastinodelookuptable():
  # first, empty it...
  for item in fastinodelookuptable:
    del fastinodelookuptable[item]

  # now let's go through and add items...


  # I need to add the root.
  fastinodelookuptable['/'] = ROOTDIRECTORYINODE
  # let's recursively do the rest...

  _recursive_rebuild_fastinodelookuptable_helper('/', ROOTDIRECTORYINODE)










######################   Generic Helper functions   #########################

def normpath2(path):

  # now I'll split on '/'.   This gives a list like: ['','foo','bar'] for
  # '/foo/bar'
  pathlist = path.split('/')

  # let's remove the leading ''
  assert(pathlist[0] == '')

  # NOTE: This makes '/foo/bar/' -> '/foo/bar'.   I think this is okay.

  # for a '..' entry, remove the previous entry (if one exists).   This will
  # only work if we go left to right.
  newpathlist = []
  position = 0
  for node in pathlist:
    if node == '.':
      continue
    elif node == '':
      continue
    elif node == '..':
      # if there is a parent, remove it and this entry.
      if len(newpathlist) > 0:
        newpathlist.pop()
      # If not, this is a no-op
    else:
      newpathlist.append(node)


  # now let's join the pathlist!
  return '/'+'/'.join(newpathlist)

# private helper function that converts a relative path or a path with things
# like foo/../bar to a normal path.
def normpath(path, cageid):

  # should raise an ENOENT error...
  if path == '':
    return path

  # If it's a relative path, prepend the CWD...
  if path[0] != '/':
    path = master_cage_context[cageid].currentworkingdirectory + '/' + path

  return normpath2(path)


# private helper function
def normpath_parent(path, cageid):
  return normpath(path+'/..', cageid)


def IS_EPOLL_FD(fd, fdtable):
  return (fd in fdtable) and ('registered_fds' in fdtable[fd])

# does this file descriptor have an inode?
def IS_INODE_DESC(fd, fdtable):
  return 'inode' in fdtable[fd]

# is this file descriptor a socket?
def IS_SOCK_DESC(fd, fdtable):
  return 'domain' in fdtable[fd]

# is this file descriptor a pipe?
def IS_PIPE_DESC(fd, fdtable):
  return 'pipe' in fdtable[fd]

def enosys_syscall(*args):
  raise SyscallError("unavailable_syscall","ENOSYS","No such syscall available")



#################### The actual system calls...   #############################

# JS: The following class provides an enclosing scope for all of the file
# system system calls. This structure allows the system calls enclosed by 
# the class to access the cageid without having a signature that contradicts
# the POSIX specification (by having a cageid parameter on each one). Although
# such a change would not adversely affect the functioning of the program, it
# would be ugly and also confusing.
#
# The syscalls should be called using the following syntax:
# get_fscall_obj(<cageid>).<syscall name>(arg1,arg2...)
#
# The networking system calls are in lind_net_calls.py and put into this class
#
# The inclusion of the cageid within system calls is necessary to handle a
# posix compliant fork, which involves a duplication of the file table.

def get_fscall_obj(cageid):
  if cageid not in master_cage_context:
    master_cage_context[cageid] = cageobj(cageid, '/')
  return master_cage_context[cageid]


class cageobj:
  def __init__(self, CONST_CAGEID, workingdir, fdtable = None, parent = 0):
    self.cageid = CONST_CAGEID
    self.currentworkingdirectory = workingdir
    self.parent = parent
    if fdtable is None:
      self.filedescriptortable = {}
      _load_lower_handle_stubs(self.filedescriptortable)
    else:
      self.filedescriptortable = {}
      filesystemmetadatalock.acquire(True)
      for key, value in fdtable.iteritems():
        self.filedescriptortable[key] = value
        try:
         filesystemmetadata['inodetable'][value['inode']]['refcount'] += 1
        except KeyError:
          pass
      filesystemmetadatalock.release()
    self.fdtablelock = createlock()

  _socket_initializer = _socket_initializer
  socket_syscall = socket_syscall
  bind_syscall = bind_syscall
  connect_syscall = connect_syscall
  sendto_syscall = sendto_syscall
  send_syscall = send_syscall
  recvfrom_syscall = recvfrom_syscall
  recv_syscall = recv_syscall
  getsockname_syscall = getsockname_syscall
  getpeername_syscall = getpeername_syscall
  listen_syscall = listen_syscall
  accept_syscall = accept_syscall
  getsockopt_syscall = getsockopt_syscall
  setsockopt_syscall = setsockopt_syscall
  _cleanup_socket = _cleanup_socket
  netshutdown_syscall = netshutdown_syscall
  _nonblock_peek_read = _nonblock_peek_read
  select_syscall = select_syscall
  getifaddrs_syscall = getifaddrs_syscall
  poll_syscall = poll_syscall
  _helper_sockpair = _helper_sockpair
  socketpair_syscall = socketpair_syscall
  _epoll_object_allocator = _epoll_object_allocator
  _epoll_object_deallocator = _epoll_object_deallocator
  epoll_create_syscall = epoll_create_syscall
  epoll_ctl_syscall = epoll_ctl_syscall
  epoll_wait_syscall = epoll_wait_syscall
  gethostname_syscall = gethostname_syscall
  
  ##### EXIT  #####

  def exit_syscall(self, status):
    """
    http://linux.die.net/man/2/exit
    """

    self.fdtablelock.acquire(True)
    
    try:
      # close all the fds in the fd-table
      for fd in self.filedescriptortable:
        self._close_helper(fd) # call _close_helper to do the work
      # remove/reparent children
     
    finally:
      self.fdtablelock.release()
      self.filedescriptortable.clear() # clean up the fd-table

    return 0
  
  
  ##### FSTATFS  #####


  # return statfs data for fstatfs and statfs
  def _istatfs_helper(self, inode):

    # I need to compute the amount of disk available / used
    limits, usage, stoptimes = getresources()

    # I'm going to fake large parts of this.
    myfsdata = {}

    myfsdata['f_type'] = 0xBEEFC0DE   # unassigned.   New to us...

    myfsdata['f_bsize'] = 4096        # Match the repy V2 block size

    myfsdata['f_blocks'] = int(limits['diskused']) / 4096

    myfsdata['f_bfree'] = (int(limits['diskused']-usage['diskused'])) / 4096
    # same as above...
    myfsdata['f_bavail'] = (int(limits['diskused']-usage['diskused'])) / 4096

    # file nodes...   I think this is infinite...
    myfsdata['f_files'] = 1024*1024*1024

    # free file nodes...   I think this is also infinite...
    myfsdata['f_ffree'] = 1024*1024*512

    myfsdata['f_fsid'] = filesystemmetadata['dev_id']

    # we don't really have a limit, but let's say 254
    myfsdata['f_namelen'] = 254

    # same as blocksize...
    myfsdata['f_frsize'] = 4096

    # it's supposed to be 5 bytes...   Let's try null characters...
    #CM: should be 8 bytes by my calc
    myfsdata['f_spare'] = '\x00'*8


    return myfsdata


  def fstatfs_syscall(self, fd):
    """
      http://linux.die.net/man/2/fstatfs
    """


    # is the file descriptor valid?
    if fd not in self.filedescriptortable:
      raise SyscallError("fstatfs_syscall","EBADF","The file descriptor is invalid.")

    # We can't fstat  Pipe or Socket
    if IS_SOCK_DESC(fd, self.filedescriptortable) or IS_PIPE_DESC(fd, self.filedescriptortable):
      raise SyscallError("fstatfs_syscall","EBADF","The file descriptor is invalid.")

    # grab the lock
    filesystemmetadatalock.acquire(True)

    try:
      # if so, return the information...
      return self_istatfs_helper(self.filedescriptortable[fd]['inode'])

    finally:
      filesystemmetadatalock.release()


  ##### STATFS  #####


  def statfs_syscall(self, path):
    """
      http://linux.die.net/man/2/statfs
    """
    # in an abundance of caution, I'll grab a lock...
    filesystemmetadatalock.acquire(True)

    # ... but always release it...
    try:
      truepath = normpath(path, self.cageid)

      # is the path there?
      if truepath not in fastinodelookuptable:
        raise SyscallError("statfs_syscall","ENOENT","The path does not exist.")

      thisinode = fastinodelookuptable[truepath]

      return self._istatfs_helper(thisinode)

    finally:
      filesystemmetadatalock.release()


  ##### ACCESS  #####

  def access_syscall(self, path, amode):
    """
      See: http://linux.die.net/man/2/access
    """


    # lock to prevent things from changing while we look this up...
    filesystemmetadatalock.acquire(True)

    # ... but always release the lock
    try:

      # get the actual name.   Remove things like '../foo'
      truepath = normpath(path, self.cageid)

      if truepath not in fastinodelookuptable:
        raise SyscallError("access_syscall","ENOENT","A directory in the path does not exist or file not found.")

      newmode = 0
      # assume current user owns the file
      if amode & X_OK:
        newmode |= S_IXUSR
      if amode & W_OK:
        newmode |= S_IWUSR
      if amode & R_OK:
        newmode |= S_IRUSR

      # BUG: This code should really walk the directories instead of using this
      # table...   This will have to be fixed for symlinks to work.
      thisinode = fastinodelookuptable[truepath]

      # BUG: This should take the UID / GID of the requestor in mind

      # if all of the bits for this file are set as requested, then indicate
      # success (return 0)
      if filesystemmetadata['inodetable'][thisinode]['mode'] & newmode == newmode:
        return 0

      raise SyscallError("access_syscall","EACCES","The requested access is denied.")

    finally:
      # release the lock
      filesystemmetadatalock.release()



  ##### CHDIR  #####

  def chdir_syscall(self, path):
    """
      http://linux.die.net/man/2/chdir
    """

    # Note: I don't think I need locking here.   I don't modify any state and
    # only check the fs state once...

    # get the actual name.   Remove things like '../foo'
    truepath = normpath(path, self.cageid)

    # If it doesn't exist...
    if truepath not in fastinodelookuptable:
      raise SyscallError("chdir_syscall","ENOENT","A directory in the path does not exist.")

    # let's update and return success (0)
    master_cage_context[self.cageid].currentworkingdirectory = truepath


    return 0


  ##### MKDIR  #####

  def mkdir_syscall(self, path, mode):
    """
      http://linux.die.net/man/2/mkdir
    """

    # lock to prevent things from changing while we look this up...
    filesystemmetadatalock.acquire(True)

    # ... but always release it...
    try:
      if path == '':
        raise SyscallError("mkdir_syscall","ENOENT","Path does not exist.")

      truepath = normpath(path, self.cageid)

      # is the path there?
      if truepath in fastinodelookuptable:
        raise SyscallError("mkdir_syscall","EEXIST","The path exists.")


      # okay, it doesn't exist (great!).   Does it's parent exist and is it a
      # dir?
      trueparentpath = normpath_parent(path, self.cageid)

      if trueparentpath not in fastinodelookuptable:
        raise SyscallError("mkdir_syscall","ENOENT","Path does not exist.")

      parentinode = fastinodelookuptable[trueparentpath]
      if not IS_DIR(filesystemmetadata['inodetable'][parentinode]['mode']):
        raise SyscallError("mkdir_syscall","ENOTDIR","Path's parent is not a directory.")


      # TODO: I should check permissions...


      assert(mode & S_IRWXA == mode)

      # okay, great!!!   We're ready to go!   Let's make the new directory...
      dirname = truepath.rsplit('/', 1)[-1]

      # first, make the new directory...
      newinode = filesystemmetadata['nextinode']
      filesystemmetadata['nextinode'] += 1

      newinodeentry = {'size':0, 'uid':DEFAULT_UID, 'gid':DEFAULT_GID,
              'mode':mode | S_IFDIR,  # DIR+rwxr-xr-x
              # BUG: I'm listing some arbitrary time values.  I could keep a time
              # counter too.
              'atime':1323630836, 'ctime':1323630836, 'mtime':1323630836,
              'linkcount':2,    # the number of dir entries...
              'refcount': 0, # no open handles to the file
              'filename_to_inode_dict': {'.':newinode, '..':parentinode}}

      # ... and put it in the table..
      filesystemmetadata['inodetable'][newinode] = newinodeentry


      filesystemmetadata['inodetable'][parentinode]['filename_to_inode_dict'][dirname] = newinode
      # increment the link count on the dir...
      filesystemmetadata['inodetable'][parentinode]['linkcount'] += 1

      # finally, update the fastinodelookuptable and return success!!!
      fastinodelookuptable[truepath] = newinode

      return 0

    finally:
      persist_metadata(METADATAFILENAME)
      filesystemmetadatalock.release()


  ##### RMDIR  #####

  def rmdir_syscall(self, path):
    """
      http://linux.die.net/man/2/rmdir
    """

    # lock to prevent things from changing while we look this up...
    filesystemmetadatalock.acquire(True)

    # ... but always release it...
    try:
      truepath = normpath(path, self.cageid)

      # Is it the root?
      if truepath == '/':
        raise SyscallError("rmdir_syscall","EINVAL","Cannot remove the root directory.")

      # is the path there?
      if truepath not in fastinodelookuptable:
        raise SyscallError("rmdir_syscall","EEXIST","The path does not exist.")

      thisinode = fastinodelookuptable[truepath]

      # okay, is it a directory?
      if not IS_DIR(filesystemmetadata['inodetable'][thisinode]['mode']):
        raise SyscallError("rmdir_syscall","ENOTDIR","Path is not a directory.")

      # Is it empty?
      if filesystemmetadata['inodetable'][thisinode]['linkcount'] > 2:
        raise SyscallError("rmdir_syscall","ENOTEMPTY","Path is not empty.")

      # TODO: I should check permissions...


      trueparentpath = normpath_parent(path, self.cageid)
      parentinode = fastinodelookuptable[trueparentpath]


      # remove the entry from the inode table...
      del filesystemmetadata['inodetable'][thisinode]


      # We're ready to go!   Let's clean up the file entry
      dirname = truepath.rsplit('/', 1)[-1]
      # remove the entry from the parent...

      del filesystemmetadata['inodetable'][parentinode]['filename_to_inode_dict'][dirname]
      # decrement the link count on the dir...
      filesystemmetadata['inodetable'][parentinode]['linkcount'] -= 1

      # finally, clean up the fastinodelookuptable and return success!!!
      del fastinodelookuptable[truepath]

      return 0

    finally:
      persist_metadata(METADATAFILENAME)
      filesystemmetadatalock.release()


  ##### LINK  #####

  def link_syscall(self, oldpath, newpath):
    """
      http://linux.die.net/man/2/link
    """

    # lock to prevent things from changing while we look this up...
    filesystemmetadatalock.acquire(True)

    # ... but always release it...
    try:
      trueoldpath = normpath(oldpath, self.cageid)

      # is the old path there?
      if trueoldpath not in fastinodelookuptable:
        raise SyscallError("link_syscall","ENOENT","Old path does not exist.")

      oldinode = fastinodelookuptable[trueoldpath]
      # is oldpath a directory?
      if IS_DIR(filesystemmetadata['inodetable'][oldinode]['mode']):
        raise SyscallError("link_syscall","EPERM","Old path is a directory.")

      # TODO: I should check permissions...

      # okay, the old path info seems fine...

      if newpath == '':
        raise SyscallError("link_syscall","ENOENT","New path does not exist.")

      truenewpath = normpath(newpath, self.cageid)

      # does the newpath exist?   It shouldn't
      if truenewpath in fastinodelookuptable:
        raise SyscallError("link_syscall","EEXIST","newpath already exists.")

      # okay, it doesn't exist (great!).   Does it's parent exist and is it a
      # dir?
      truenewparentpath = normpath_parent(newpath, self.cageid)

      if truenewparentpath not in fastinodelookuptable:
        raise SyscallError("link_syscall","ENOENT","New path does not exist.")

      newparentinode = fastinodelookuptable[truenewparentpath]
      if not IS_DIR(filesystemmetadata['inodetable'][newparentinode]['mode']):
        raise SyscallError("link_syscall","ENOTDIR","New path's parent is not a directory.")


      # TODO: I should check permissions...



      # okay, great!!!   We're ready to go!   Let's make the file...
      newfilename = truenewpath.rsplit('/', 1)[-1]
      # first, make the directory entry...
      filesystemmetadata['inodetable'][newparentinode]['filename_to_inode_dict'][newfilename] = oldinode
      # increment the link count on the dir...
      filesystemmetadata['inodetable'][newparentinode]['linkcount'] += 1

      # ... and the file itself
      filesystemmetadata['inodetable'][oldinode]['linkcount'] += 1

      # finally, update the fastinodelookuptable and return success!!!
      fastinodelookuptable[truenewpath] = oldinode

      return 0

    finally:
      persist_metadata(METADATAFILENAME)
      filesystemmetadatalock.release()


  ##### UNLINK  #####

  def unlink_syscall(self, path):
    """
      http://linux.die.net/man/2/unlink
    """

    # lock to prevent things from changing while we do this...
    filesystemmetadatalock.acquire(True)

    # ... but always release it...
    try:
      truepath = normpath(path, self.cageid)

      # is the path there?
      if truepath not in fastinodelookuptable:
        raise SyscallError("unlink_syscall","ENOENT","The path does not exist.")

      thisinode = fastinodelookuptable[truepath]

      # okay, is it a directory?
      if IS_DIR(filesystemmetadata['inodetable'][thisinode]['mode']):
        raise SyscallError("unlink_syscall","EISDIR","Path is a directory.")

      # TODO: I should check permissions...


      trueparentpath = normpath_parent(path, self.cageid)
      parentinode = fastinodelookuptable[trueparentpath]




      # We're ready to go!   Let's clean up the file entry
      dirname = truepath.rsplit('/', 1)[-1]
      # remove the entry from the parent...

      del filesystemmetadata['inodetable'][parentinode]['filename_to_inode_dict'][dirname]
      # decrement the link count on the dir...
      filesystemmetadata['inodetable'][parentinode]['linkcount'] -= 1

      # clean up the fastinodelookuptable
      del fastinodelookuptable[truepath]


      # decrement the link count...
      filesystemmetadata['inodetable'][thisinode]['linkcount'] -= 1

      # If 0, remove the entry from the inode table if there are no open handles
      # If open handles exist, flag it to unlink when the last handle is closed
      if filesystemmetadata['inodetable'][thisinode]['linkcount'] == 0:
        if filesystemmetadata['inodetable'][thisinode]['refcount'] == 0:
          del filesystemmetadata['inodetable'][thisinode]
          removefile(FILEDATAPREFIX+str(thisinode))
        else:
          filesystemmetadata['inodetable'][thisinode]['unlinked'] = True

      return 0

    finally:
      persist_metadata(METADATAFILENAME)
      filesystemmetadatalock.release()


  ##### STAT  #####

  def stat_syscall(self, path):
    """
      http://linux.die.net/man/2/stat

    """

    # in an abundance of caution, I'll grab a lock...
    filesystemmetadatalock.acquire(True)

    # ... but always release it...
    try:
      truepath = normpath(path, self.cageid)

      # is the path there?
      if truepath not in fastinodelookuptable:
        raise SyscallError("stat_syscall","ENOENT","The path does not exist.")

      thisinode = fastinodelookuptable[truepath]

      # If its a character file, call the helper function.
      if IS_CHR(filesystemmetadata['inodetable'][thisinode]['mode']):
        return self._istat_helper_chr_file(thisinode)

      return self._istat_helper(thisinode)

    finally:
      filesystemmetadatalock.release()


  ##### FSTAT  #####

  def fstat_syscall(self, fd):
    """
      http://linux.die.net/man/2/fstat
    """
    # TODO: I don't handle socket objects.   I should return something like:
    # st_mode=49590, st_ino=0, st_dev=0L, st_nlink=0, st_uid=501, st_gid=20,
    # st_size=0, st_atime=0, st_mtime=0, st_ctime=0


    # is the file descriptor valid?
    if fd not in self.filedescriptortable:
      raise SyscallError("fstat_syscall","EBADF","The file descriptor is invalid.")
    
    # grab the locks
    filesystemmetadatalock.acquire(True)
    self.filedescriptortable[fd]['lock'].acquire(True)

    try:
      # if so, return the information...
      if IS_PIPE_DESC(fd, self.filedescriptortable):
        # mocking pipe inode number to 0xfeef0000
        return self._stat_alt_helper(PIPE_INODE)
      
      inode = self.filedescriptortable[fd]['inode']

      # this is a stream, lets mock it
      if inode == STREAMINODE:
        return self._stat_alt_helper(inode)


      if IS_CHR(filesystemmetadata['inodetable'][inode]['mode']):
        return self._istat_helper_chr_file(inode)
      return self._istat_helper(inode)

    finally:
      self.filedescriptortable[fd]['lock'].release()
      filesystemmetadatalock.release()


  # private helper routine that returns stat data given an inode
  def _istat_helper(self, inode):
    ret =  (filesystemmetadata['dev_id'],          # st_dev
            inode,                                 # inode
            filesystemmetadata['inodetable'][inode]['mode'],
            filesystemmetadata['inodetable'][inode]['linkcount'],
            filesystemmetadata['inodetable'][inode]['uid'],
            filesystemmetadata['inodetable'][inode]['gid'],
            0,                                     # st_rdev     ignored(?)
            filesystemmetadata['inodetable'][inode]['size'],
            0,                                     # st_blksize  ignored(?)
            0,                                     # st_blocks   ignored(?)
            filesystemmetadata['inodetable'][inode]['atime'],
            0,                                     # atime ns
            filesystemmetadata['inodetable'][inode]['mtime'],
            0,                                     # mtime ns
            filesystemmetadata['inodetable'][inode]['ctime'],
            0,                                     # ctime ns
          )
    return ret

  # this is used to configure non-std stats such as pipes or std streams
  def _stat_alt_helper(self, inode):
    ret =  (filesystemmetadata['dev_id'],          # st_dev
            inode,                                 # inode
            49590,                                 # mode (these are all the R + W permissions)
            1,                                     # links
            DEFAULT_UID,                           # uid
            DEFAULT_GID,                           #  gid
            0,                                     # st_rdev     ignored(?)
            0,                                     # size
            0,                                     # st_blksize  ignored(?)
            0,                                     # st_blocks   ignored(?)
            0,
            0,                                     # atime ns
            0,
            0,                                     # mtime ns
            0,
            0,                                     # ctime ns
          )
    return ret






  ##### OPEN  #####


  # get the next free file descriptor
  def get_next_fd(self, startfd=STARTINGFD):
    # let's get the next available fd number.   The standard says we need to
    # return the lowest open fd number.
    for fd in range(startfd, MAX_FD):
      if not fd in self.filedescriptortable:
        return fd

    raise SyscallError("open_syscall","EMFILE","The maximum number of files are open.")

  def open_syscall(self, path, flags, mode):
    """
      http://linux.die.net/man/2/open
    """

    # in an abundance of caution, lock...   I think this should only be needed
    # with O_CREAT flags...
    filesystemmetadatalock.acquire(True)
    self.fdtablelock.acquire(True)

    # ... but always release it...
    try:
      if path == '':
        raise SyscallError("open_syscall","ENOENT","The file does not exist.")

      truepath = normpath(path, self.cageid)

      # is the file missing?
      if truepath not in fastinodelookuptable:

        # did they use O_CREAT?
        if not O_CREAT & flags:
          raise SyscallError("open_syscall","ENOENT","The file does not exist.")

        # okay, it doesn't exist (great!).   Does it's parent exist and is it a
        # dir?
        trueparentpath = normpath_parent(path, self.cageid)

        if trueparentpath not in fastinodelookuptable:
          raise SyscallError("open_syscall","ENOENT","Path does not exist.")

        parentinode = fastinodelookuptable[trueparentpath]
        if not IS_DIR(filesystemmetadata['inodetable'][parentinode]['mode']):
          raise SyscallError("open_syscall","ENOTDIR","Path's parent is not a directory.")



        # okay, great!!!   We're ready to go!   Let's make the new file...
        filename = truepath.rsplit('/', 1)[-1]

        # first, make the new file's entry...
        newinode = filesystemmetadata['nextinode']
        filesystemmetadata['nextinode'] += 1

        # be sure there aren't extra mode bits...   No errno seems to exist for
        # this.
        assert(mode & (S_IRWXA|S_FILETYPEFLAGS) == mode)

        effective_mode = (S_IFCHR | mode) if (S_IFCHR & flags) != 0 else (S_IFREG | mode)

        newinodeentry = {'size':0, 'uid':DEFAULT_UID, 'gid':DEFAULT_GID,
              'mode':effective_mode,
              # BUG: I'm listing some arbitrary time values.  I could keep a time
              # counter too.
              'atime':1323630836, 'ctime':1323630836, 'mtime':1323630836,
              'refcount': 0, # no open handles to the file
              'linkcount':1}

        # ... and put it in the table..
        filesystemmetadata['inodetable'][newinode] = newinodeentry


        # let's make the parent point to it...
        filesystemmetadata['inodetable'][parentinode]['filename_to_inode_dict'][filename] = newinode
        # ... and increment the link count on the dir...
        filesystemmetadata['inodetable'][parentinode]['linkcount'] += 1

        # finally, update the fastinodelookuptable
        fastinodelookuptable[truepath] = newinode

        # this file must not exist or it's an internal error!!!
        openfile(FILEDATAPREFIX+str(newinode),True).close()

        persist_metadata(METADATAFILENAME)

      # if the file did exist, were we told to create with exclusion?
      else:
        # did they use O_CREAT and O_EXCL?
        if O_CREAT & flags and O_EXCL & flags:
          raise SyscallError("open_syscall","EEXIST","The file exists.")

        # This file should be removed.   If O_RDONLY is set, the behavior
        # is undefined, so this is okay, I guess...
        if O_TRUNC & flags:
          inode = fastinodelookuptable[truepath]

          # if it exists, close the existing file object so I can remove it...
          if inode in fileobjecttable:
            fileobjecttable[inode].close()
            
          # reset the size to 0
          filesystemmetadata['inodetable'][inode]['size'] = 0

          # remove the file...
          removefile(FILEDATAPREFIX+str(inode))

          # always open the file.
          fileobjecttable[inode] = openfile(FILEDATAPREFIX+str(inode),True)

          persist_metadata(METADATAFILENAME)


      # TODO: I should check permissions...

      # At this point, the file will exist...

      # Let's find the inode
      inode = fastinodelookuptable[truepath]

      filesystemmetadata['inodetable'][inode]['refcount'] += 1 #add a reference to the file


      # get the next fd so we can use it...
      thisfd = self.get_next_fd()


      # Note, directories can be opened (to do getdents, etc.).   We shouldn't
      # actually open something in this case...
      # Is it a regular file?
      if IS_REG(filesystemmetadata['inodetable'][inode]['mode']):
        # this is a regular file.  If it's not open, let's open it!
        if inode not in fileobjecttable:
          thisfo = openfile(FILEDATAPREFIX+str(inode),False)
          fileobjecttable[inode] = thisfo

      # I'm going to assume that if you use O_APPEND I only need to
      # start the pointer in the right place.
      if O_APPEND & flags:
        position = filesystemmetadata['inodetable'][inode]['size']
      else:
        # else, let's start at the beginning
        position = 0


      # TODO handle read / write locking, etc.

      # Add the entry to the table!
      self.filedescriptortable[thisfd] = {'position':position, 'inode':inode, 'lock':createlock(), 'flags':flags&O_RDWRFLAGS}
      # Done!   Let's return the file descriptor.
      return thisfd

    finally:
      self.fdtablelock.release()
      filesystemmetadatalock.release()


  ##### CREAT  #####

  def creat_syscall(self, pathname, mode):
    """
      http://linux.die.net/man/2/creat
    """

    try:

      return self.open_syscall(pathname, O_CREAT | O_TRUNC | O_WRONLY, mode)

    except SyscallError, e:
      # If it's a system call error, return our call name instead.
      assert(e[0]=='open_syscall')

      raise SyscallError('creat_syscall',e[1],e[2])


  ##### LSEEK  #####

  def lseek_syscall(self, fd, offset, whence):
    """
      http://linux.die.net/man/2/lseek
    """


    # check the fd
    if fd not in self.filedescriptortable:
      raise SyscallError("lseek_syscall","EBADF","Invalid file descriptor.")

    # Acquire the fd and filesystemmetadata locks...
    filesystemmetadatalock.acquire(True)
    self.filedescriptortable[fd]['lock'].acquire(True)


    # We can't seek on Pipe or Socket
    if IS_SOCK_DESC(fd, self.filedescriptortable) or IS_PIPE_DESC(fd, self.filedescriptortable):
      self.filedescriptortable[fd]['lock'].release()
      filesystemmetadatalock.release()
      raise SyscallError("lseek_syscall","ESPIPE","Invalid seek.")

    # if we are any of the odd handles(stdin, stdout, stderr), we cant seek, so just report we are at 0
    if self.filedescriptortable[fd]['inode'] == STREAMINODE:
      self.filedescriptortable[fd]['lock'].release()
      filesystemmetadatalock.release()
      return 0



    # ... but always release the locks...
    try:

      # we will need the file size in a moment, but also need to check the type
      try:
        inode = self.filedescriptortable[fd]['inode']
      except KeyError:
        raise SyscallError("lseek_syscall","ESPIPE","This is a socket, not a file.")

      # Let's figure out if this has a length / pointer...
      if IS_REG(filesystemmetadata['inodetable'][inode]['mode']):
        # straightforward if it is a file...
        filesize = filesystemmetadata['inodetable'][inode]['size']

      elif IS_DIR(filesystemmetadata['inodetable'][inode]['mode']):
        # if a directory, let's use the number of entries
        filesize = len(filesystemmetadata['inodetable'][inode]['filename_to_inode_dict'])

      else:
        # otherwise we don't know
        raise SyscallError("lseek_syscall","EINVAL","File descriptor does not refer to a regular file or directory.")


      # Figure out where we will seek to and check it...
      if whence == SEEK_SET:
        eventualpos = offset
      elif whence == SEEK_CUR:
        eventualpos = self.filedescriptortable[fd]['position']+offset
      elif whence == SEEK_END:
        eventualpos = filesize+offset
      else:
        raise SyscallError("lseek_syscall","EINVAL","Invalid whence.")

      # did we fall off the front?
      if eventualpos < 0:
        raise SyscallError("lseek_syscall","EINVAL","Seek before position 0 in file.")

      # did we fall off the back?
      # if so, we'll handle this when we do a write.   The correct behavior is
      # to write '\0' bytes between here and that pos.

      # do the seek and return success (the position)!
      self.filedescriptortable[fd]['position'] = eventualpos

      return eventualpos

    finally:
      # ... release the lock
      self.filedescriptortable[fd]['lock'].release()
      filesystemmetadatalock.release()


  # helper function for pipe reads
  def _read_from_pipe(self, fd, count, buf_addr):

    # lets find the pipe number and acquire the readlock
    pipenumber = self.filedescriptortable[fd]['pipe']

    return pipetable[pipenumber].piperead(buf_addr, count)
 


  #helper funtion for read/pread
  def read_from_file(self, syscall_name, fd, count, offset):
    try:
      # Acquire the metadata lock... but always release it
      filesystemmetadatalock.acquire(True)

      # get the inode so I can and check the mode (type)
      inode = self.filedescriptortable[fd]['inode']

      # If its a character file, call the helper function.
      if IS_CHR(filesystemmetadata['inodetable'][inode]['mode']):
        return self._read_chr_file(inode, count)

      # Is it anything other than a regular file?
      if not IS_REG(filesystemmetadata['inodetable'][inode]['mode']):
        raise SyscallError(syscall_name,"EINVAL","File descriptor does not refer to a regular file.")

      # let's do a readat!
      
      if syscall_name == "read_syscall": #read
        position = self.filedescriptortable[fd]['position']
        data = fileobjecttable[inode].readat(count,position)
        # and update the position
        self.filedescriptortable[fd]['position'] += len(data)
        
      else: #pread
        data = fileobjecttable[inode].readat(count,offset)
        
      return data
    
    finally:
      filesystemmetadatalock.release()
        
        
        
  ##### READ  #####

  def read_syscall(self, fd, count, buf_addr):
    """
      http://linux.die.net/man/2/read
    """

    try:
      if self.filedescriptortable[fd]["stream"] == 0:
        return ""
    except KeyError:
      pass

    # check the fd
    if fd not in self.filedescriptortable:
      raise SyscallError("read_syscall","EBADF","Invalid file descriptor.")

    # Is it open for reading?
    if IS_WRONLY(self.filedescriptortable[fd]['flags']):
      raise SyscallError("read_syscall","EBADF","File descriptor is not open for reading.")

    # Acquire the fd lock...
    self.filedescriptortable[fd]['lock'].acquire(True)

    # ... but always release it...
    try:

      # lets check if it's a pipe first, and if so read from that
      if IS_PIPE_DESC(fd, self.filedescriptortable):
        return self._read_from_pipe(fd, count, buf_addr)

      if IS_SOCK_DESC(fd, self.filedescriptortable):
        try:
          if count == 0:
            data = self.recv_syscall(fd, TX_BUF_MAX, 0)
          data = self.recv_syscall(fd, count, 0) #recv doesn't lock for some reason
        except SocketWouldBlockError as e:
          return ErrorResponseBuilder("fs_read", "EAGAIN", "Socket would block")

      data = self.read_from_file("read_syscall", fd, count, 0)
      
      # transfer read data back to read buffer and return size
      size_read = len(data)
      repy_move_to_readbuf(buf_addr, data, size_read)
      return size_read

    finally:
      # ... release the lock
      self.filedescriptortable[fd]['lock'].release()
  
 
  
  ##### PREAD  #####
  
  def pread_syscall(self, fd, count, offset):
    """
      https://linux.die.net/man/2/pread
    """

    try:
      if self.filedescriptortable[fd]["stream"] == 0:
        return ""
    except KeyError:
      pass

    # check the fd
    if fd not in self.filedescriptortable:
      raise SyscallError("pread_syscall","EBADF","Invalid file descriptor.")

    # Is it open for reading?
    if IS_WRONLY(self.filedescriptortable[fd]['flags']):
      raise SyscallError("pread_syscall","EBADF","File descriptor is not open for reading.")

    # Acquire the fd lock...
    self.filedescriptortable[fd]['lock'].acquire(True)

    # ... but always release it...
    try:
      if IS_PIPE_DESC(fd, self.filedescriptortable) or IS_SOCK_DESC(fd, self.filedescriptortable):
        raise SyscallError("pread_syscall","ESPIPE","File descriptor is associated with a pipe or FIFO or socket.")
      
      return self.read_from_file("pread_syscall", fd, count, offset)

    finally:
      # ... release the lock
      self.filedescriptortable[fd]['lock'].release()


  # helper function for pipe writes
  def _write_to_pipe(self, fd, count, buf_addr):

    pipenumber = self.filedescriptortable[fd]['pipe']

    return pipetable[pipenumber].pipewrite(buf_addr, count)

  
  #helper funtion for read/pread
  def write_to_file(self, syscall_name, fd, data, offset):
    
    try:
      # Acquire the metadata lock... but always release it
      filesystemmetadatalock.acquire(True)

      # get the inode so I can update the size (if needed) and check the type
      inode = self.filedescriptortable[fd]['inode']

      # If its a character file, call the helper function.
      if IS_CHR(filesystemmetadata['inodetable'][inode]['mode']):
        return self._write_chr_file(inode, data)

      # Is it anything other than a regular file?
      if not IS_REG(filesystemmetadata['inodetable'][inode]['mode']):
        raise SyscallError(syscall_name,"EINVAL","File descriptor does not refer to a regular file.")
        
      # let's get the position...
      if syscall_name == "write_syscall": #write
        position = self.filedescriptortable[fd]['position']        
      else: #pwrite
        position = offset
      
      # and the file size...
      filesize = filesystemmetadata['inodetable'][inode]['size']

      # if the position is past the end of the file, write '\0' bytes to fill
      # up the gap...
      blankbytecount = position - filesize
      
      if blankbytecount > 0:
        # let's write the blank part at the end of the file...
        fileobjecttable[inode].writeat('\0'*blankbytecount,filesize)
        filesystemmetadata['inodetable'][inode]['size'] = position
        filesize = position

      # writeat never writes less than desired in Repy V2.
      fileobjecttable[inode].writeat(data,position)


      if syscall_name == "write_syscall": #write
        #update the position
        self.filedescriptortable[fd]['position'] += len(data)

        # update the file size if we've extended it
        if self.filedescriptortable[fd]['position'] > filesize:
          filesystemmetadata['inodetable'][inode]['size'] = self.filedescriptortable[fd]['position']
          persist_metadata(METADATAFILENAME)
      
      else: #pwrite
        # update the file size if we've extended it
        if (position + len(data)) > filesize:
          filesystemmetadata['inodetable'][inode]['size'] = position + len(data)
          persist_metadata(METADATAFILENAME)

      # we always write it all, so just return the length of what we were passed.
      # We do not mention whether we write blank data (if position is after the
      # end)
      return len(data)
      
    finally:
      filesystemmetadatalock.release()


  ##### WRITE  #####

  def write_syscall(self, fd, count, buf_addr):
    """
      http://linux.die.net/man/2/write
    """
    # check the fd
    if fd not in self.filedescriptortable:
      raise SyscallError("write_syscall","EBADF","Invalid file descriptor.")
  
    # if we're going to stdout/err, lets get it over with and print    
    try:
      if self.filedescriptortable[fd]['stream'] in [1,2]:
        log_stdout(repy_addr2string(buf_addr, count))
        return count
    except KeyError:
      pass

    # Is it open for writing?
    if IS_RDONLY(self.filedescriptortable[fd]['flags']):
      raise SyscallError("write_syscall","EBADF","File descriptor is not open for writing.")
    
    # Acquire the fd lock...
    self.filedescriptortable[fd]['lock'].acquire(True)

    # ... but always release it...
    try:

      # lets check if it's a pipe first, and if so write to that
      if IS_PIPE_DESC(fd, self.filedescriptortable):
        return self._write_to_pipe(fd, count, buf_addr)

      # turn buffer into PyString
      data = repy_addr2string(buf_addr, count)

      if IS_SOCK_DESC(fd, self.filedescriptortable):
        return self.send_syscall(fd, data, 0)

      return self.write_to_file("write_syscall", fd, data, 0)

    finally:
      # ... release the lock
      self.filedescriptortable[fd]['lock'].release()

  
  ##### PWRITE  #####

  def pwrite_syscall(self, fd, data, offset):
    """
      https://linux.die.net/man/2/pwrite
    """
    
    # check the fd
    if fd not in self.filedescriptortable:
      raise SyscallError("pwrite_syscall","EBADF","Invalid file descriptor.")
  
    # if we're going to stdout/err, lets get it over with and print    
    try:
      if self.filedescriptortable[fd]['stream'] in [1,2]:
        log_stdout(data)
        return len(data)
    except KeyError:
      pass

    # Is it open for writing?
    if IS_RDONLY(self.filedescriptortable[fd]['flags']):
      raise SyscallError("pwrite_syscall","EBADF","File descriptor is not open for writing.")
    
    # Acquire the fd lock...
    self.filedescriptortable[fd]['lock'].acquire(True)

    # ... but always release it...
    try:
      if IS_PIPE_DESC(fd,CONST_CAGEID) or IS_SOCK_DESC(fd,CONST_CAGEID):
        raise SyscallError("pwrite_syscall","ESPIPE","File descriptor is associated with a pipe or FIFO or socket.")
        
      return self.write_to_file("pwrite_syscall", fd, data, offset)

    finally:
      # ... release the lock
      self.filedescriptortable[fd]['lock'].release()

  
  
  

  ##### CLOSE  #####

  # private helper.   Get the fds for an inode (or [] if none)
  def _lookup_fds_by_inode(self, inode):
    returnedfddict = {}
    for cageid, ctx in master_cage_context.items():
      table = ctx.filedescriptortable
      try:
        for fd in table.keys():
          if IS_SOCK_DESC(fd, table) or IS_EPOLL_FD(fd, table) or IS_PIPE_DESC(fd, table):
            continue

          if table[fd]['inode'] == inode:
            if cageid in returnedfddict:
              returnedfddict[cageid].append(fd)
            else:
              returnedfddict[cageid] = [fd]
      except KeyError as e:
        print e


    return returnedfddict

  # private helper.   Get the references to and end of a pipe 
  def _lookup_refs_by_pipe_end(self, pipenumber, flags):
    pipe_references = 0
    for cageid, ctx in master_cage_context.items():
      table = ctx.filedescriptortable
      try:
        for fd in table.keys(): 
          if IS_PIPE_DESC(fd, table):
            if table[fd]['pipe'] == pipenumber and table[fd]['flags'] == flags:
              pipe_references += 1
      except KeyError as e:
        print e


    return pipe_references


  # private helper, handle pipe as each end closes.
  def _cleanup_pipe(self, fd):
    # let's find the pipenumber
    pipenumber = self.filedescriptortable[fd]['pipe']

    # and look up how many read ends and write ends are open
    read_references = self._lookup_refs_by_pipe_end(pipenumber, O_RDONLY)
    write_references = read_references = self._lookup_refs_by_pipe_end(pipenumber, O_WRONLY)

    # if there's only one write end left open, and we're closing that end, no write ends will be open so we can send an EOF
    if write_references == 1 and self.filedescriptortable[fd]['flags'] == O_WRONLY:
      pipetable[pipenumber].seteof()

    # if we're closing the last end, we can delete the pipe
    if (read_references + write_references) == 1:
      del pipetable[pipenumber]


      return 0


  # private helper that allows this to be called in other places (like dup2)
  # without changing to re-entrant locks
  def _close_helper(self, fd, filelock = True):

    # don't close streams, which have an inode of 1
    try:
      if self.filedescriptortable[fd]['inode'] == STREAMINODE: return 0
    except KeyError:
      pass

    # in an abundance of caution, lock...
    filesystemmetadatalock.acquire(True)

    # Acquire the fd lock, if there is one.
    if 'lock' in self.filedescriptortable[fd] and filelock:
      self.filedescriptortable[fd]['lock'].acquire(True)

    try:
      # if we are a socket, we dont change disk metadata
      if IS_SOCK_DESC(fd, self.filedescriptortable):
        self._cleanup_socket(fd, False)
        return 0

      if IS_PIPE_DESC(fd, self.filedescriptortable):
        self._cleanup_pipe(fd)
        return 0

      if IS_EPOLL_FD(fd, self.filedescriptortable):
        _epoll_object_deallocator(fd)
        return 0


      # get the inode for the filedescriptor
      inode = self.filedescriptortable[fd]['inode']
      filesystemmetadata['inodetable'][inode]['refcount'] -= 1 # close a reference to the file

      # If it's not a regular file, we have nothing to close...
      if not IS_REG(filesystemmetadata['inodetable'][inode]['mode']):

        # double check that this isn't in the fileobjecttable
        if inode in fileobjecttable:
          raise Exception("Internal Error: non-regular file in fileobjecttable")
        # and return success
        return 0

      # I should only close here if it's the last use of the file.   This can
      # happen due to dup, multiple opens, etc.
      if filesystemmetadata['inodetable'][inode]['refcount'] != 0:
        # Is there more than one descriptor open?   If so, return success
        return 0
      # now let's close it and remove it from the table
      fileobjecttable[inode].close()
      del fileobjecttable[inode]

      # If this was the last open handle to the file, and the file has been marked
      # for unlinking, then delete the inode here.
      if 'unlinked' in filesystemmetadata['inodetable'][inode]:
          del filesystemmetadata['inodetable'][inode]
          removefile(FILEDATAPREFIX+str(inode))

      # success!
      return 0
    finally:
      # ... release the lock, if there is one
      if 'lock' in self.filedescriptortable[fd] and filelock:
        self.filedescriptortable[fd]['lock'].release()
      filesystemmetadatalock.release()


  def close_syscall(self, fd):
    """
      http://linux.die.net/man/2/close
    """

    # in an abundance of caution, lock...
    self.fdtablelock.acquire(True)

    if fd not in self.filedescriptortable:
      raise SyscallError("close_syscall","EBADF","Invalid file descriptor.")

    # ... but always release it...
    try:
      return self._close_helper(fd)

    finally:
      del self.filedescriptortable[fd]
      self.fdtablelock.release()


  ##### DUP2  #####


  # private helper that allows this to be used by dup
  def _dup2_helper(self, oldfd,newfd):

    # if the new file descriptor is too low or too high
    # NOTE: I want to support dup2 being used to replace STDERR, STDOUT, etc.
    #      The Lind code may pass me descriptors less than STARTINGFD

    if newfd >= MAX_FD or newfd < 0:
      # BUG: the STARTINGFD isn't really too low.   It's just lower than we
      # support
      raise SyscallError("dup2_syscall","EBADF","Invalid new file descriptor.")

    # if they are equal, return them
    if newfd == oldfd:
      return newfd

    # okay, they are different.   If the new fd exists, close it.
    if newfd in self.filedescriptortable:
      # should not result in an error.   This only occurs on a bad fd
      self._close_helper(newfd, filelock = False)


    # Okay, we need the new and old to point to the same thing.
    # NOTE: I am not making a copy here!!!   They intentionally both
    # refer to the same instance because manipulating the position, etc.
    # impacts both.
    self.filedescriptortable[newfd] = self.filedescriptortable[oldfd]

    return newfd




  def dup2_syscall(self, oldfd,newfd):
    """
      http://linux.die.net/man/2/dup2
    """

    # lock to prevent things from changing while we look this up...
    self.fdtablelock.acquire(True)
    # check the fd
    if oldfd not in self.filedescriptortable:
      raise SyscallError("dup2_syscall","EBADF","Invalid old file descriptor.")

    # Acquire the fd lock...
    self.filedescriptortable[oldfd]['lock'].acquire(True)


    # ... but always release it...
    try:
      return self._dup2_helper(oldfd, newfd)

    finally:
      # ... release the locks
      self.filedescriptortable[oldfd]['lock'].release()
      self.fdtablelock.release()


  ##### DUP  #####

  def dup_syscall(self, fd, startfd=STARTINGFD):
    """
      http://linux.die.net/man/2/dup
    """

    # lock to prevent things from changing while we look this up...
    self.fdtablelock.acquire(True)

    # check the fd
    if fd not in self.filedescriptortable and fd >= STARTINGFD:
      raise SyscallError("dup_syscall","EBADF","Invalid old file descriptor.")

    # Acquire the fd lock...
    self.filedescriptortable[fd]['lock'].acquire(True)

    try:
      # get the next available file descriptor
      try:
        nextfd = self.get_next_fd(startfd)
      except SyscallError, e:
        # If it's an error getting the fd, return our call name instead.
        assert(e[0]=='open_syscall')

        raise SyscallError('dup_syscall',e[1],e[2])

      # this does the work.   It should _never_ raise an exception given the
      # checks we've made...
      return self._dup2_helper(fd, nextfd)

    finally:
      # ... release the locks
      self.filedescriptortable[fd]['lock'].release()
      self.fdtablelock.release()


  ##### FCNTL  #####

  def fcntl_syscall(self, fd, cmd, *args):
    """
      http://linux.die.net/man/2/fcntl
    """
    # this call is totally crazy!   I'll just implement the basics and add more
    # as is needed.

    # BUG: I probably need a filedescriptortable lock to prevent race conditions

    # check the fd
    if fd not in self.filedescriptortable:
      raise SyscallError("fcntl_syscall","EBADF","Invalid file descriptor.")

    # Acquire the fd lock...
    self.filedescriptortable[fd]['lock'].acquire(True)

    # ... but always release it...
    try:
      # if we're getting the flags, return them... (but this is just CLO_EXEC,
      # so ignore)
      if cmd == F_GETFD:
        if len(args) > 0:
          raise SyscallError("fcntl_syscall", "EINVAL", "Argument is more than\
            maximum allowable value.")
        return int((self.filedescriptortable[fd]['flags'] & FD_CLOEXEC) != 0)

      # set the flags...
      elif cmd == F_SETFD:
        assert(len(args) == 1)
        self.filedescriptortable[fd]['flags'] |= FD_CLOEXEC #Linux only supports FD_CLOEXEC
        return 0

      # if we're getting the flags, return them...
      elif cmd == F_GETFL:
        assert(len(args) == 0)
        return self.filedescriptortable[fd]['flags']

      # set the flags...
      elif cmd == F_SETFL:
        assert(len(args) == 1)
        assert(type(args[0]) == int or type(args[0]) == long)
        self.filedescriptortable[fd]['flags'] = args[0]
        return 0

      # lets go to DUP
      elif cmd == F_DUPFD:
        assert(len(args) == 1)
        assert(type(args[0]) == int or type(args[0]) == long)
        self.dup_syscall(fd, args[0])
        return 0

      # This is saying we'll get signals for this.   Let's punt this...
      elif cmd == F_GETOWN:
        assert(len(args) == 0)
        # Saying traditional SIGIO behavior...
        return 0

      # indicate that we want to receive signals for this FD...
      elif cmd == F_SETOWN:
        assert(len(args) == 1)
        assert(type(args[0]) == int or type(args[0]) == long)
        # this would almost certainly say our PID (if positive) or our process
        # group (if negative).   Either way, we do nothing and return success.
        return 0


      else:
        # This is either unimplemented or malformed.   Let's raise
        # an exception.
        raise UnimplementedError('FCNTL with command '+str(cmd)+' is not yet implemented.')

    finally:
      # ... release the lock
      self.filedescriptortable[fd]['lock'].release()


  ##### GETDENTS  #####

  def getdents_syscall(self, fd, quantity):
    """
      http://linux.die.net/man/2/getdents
    """

    # BUG BUG BUG: Do I really understand this spec!?!?!?!

    # check the fd
    if fd not in self.filedescriptortable:
      raise SyscallError("getdents_syscall","EBADF","Invalid file descriptor.")

    # We can't getdents on a Pipe or Socket
    if IS_SOCK_DESC(fd, self.filedescriptortable) or IS_PIPE_DESC(fd, self.filedescriptortable):
      raise SyscallError("getdents_syscall","ENOENT","No such directory.")

    # Sanitizing the Input, there are people who would send other types too.
    if not isinstance(quantity, (int, long)):
      raise SyscallError("getdents_syscall","EINVAL","Invalid type for buffer size.")

    # This is the minimum number of bytes, that should be provided.
    if quantity < 24:
      raise SyscallError("getdents_syscall","EINVAL","Buffer size is too small.")

    # Acquire the fd lock...
    filesystemmetadatalock.acquire(True)
    self.filedescriptortable[fd]['lock'].acquire(True)

    # ... but always release it...
    try:

      # get the inode so I can read the directory entries
      inode = self.filedescriptortable[fd]['inode']

      # Is it a directory?
      if not IS_DIR(filesystemmetadata['inodetable'][inode]['mode']):
        raise SyscallError("getdents_syscall","EINVAL","File descriptor does not refer to a directory.")

      returninodefntuplelist = []
      bufferedquantity = 0

      # let's move the position forward...
      startposition = self.filedescriptortable[fd]['position']
      # return tuple with inode, name, type tuples...
      for entryname,entryinode in list(filesystemmetadata['inodetable'][inode]['filename_to_inode_dict'].iteritems())[startposition:]:
        # getdents returns the mode also (at least on Linux)...
        entrytype = get_direnttype_from_mode(filesystemmetadata['inodetable'][entryinode]['mode'])

        # Get the size of each entry, the size should be a multiple of 8.
        # The size of each entry is determined by sizeof(struct linux_dirent) which is 20 bytes plus the length of name of the file.
        # So, size of each entry becomes : 21 => 24, 26 => 32, 32 => 32.
        currentquantity = (((20 + len(entryname)) + 7) / 8) * 8

        # This is the overall size of entries parsed till now, if size exceeds given size, then stop parsing and return
        bufferedquantity += currentquantity
        if bufferedquantity > quantity:
          break

        returninodefntuplelist.append((entryinode, entryname, entrytype, currentquantity))

      # and move the position along.   Go no further than the end...
      self.filedescriptortable[fd]['position'] = min(startposition + len(returninodefntuplelist),\
        len(filesystemmetadata['inodetable'][inode]['filename_to_inode_dict']))

      return returninodefntuplelist

    finally:
      # ... release the lock
      self.filedescriptortable[fd]['lock'].release()
      filesystemmetadatalock.release()


  #### CHMOD ####

  def chmod_syscall(self, path, mode):
    """
      http://linux.die.net/man/2/chmod
    """
    # in an abundance of caution, I'll grab a lock...
    filesystemmetadatalock.acquire(True)

    # ... but always release it...
    try:
      truepath = normpath(path, self.cageid)

      # is the path there?
      if truepath not in fastinodelookuptable:
        raise SyscallError("chmod_syscall", "ENOENT", "The path does not exist.")

      thisinode = fastinodelookuptable[truepath]

      # be sure there aren't extra mode bits... No errno seems to exist for this
      assert(mode & (S_IRWXA|S_FILETYPEFLAGS) == mode)

      # should overwrite any previous permissions, according to POSIX.   However,
      # we want to keep the 'type' part of the mode from before
      filesystemmetadata['inodetable'][thisinode]['mode'] = (filesystemmetadata['inodetable'][thisinode]['mode'] &~S_IRWXA) | mode

    finally:
      persist_metadata(METADATAFILENAME)
      filesystemmetadatalock.release()
    return 0


  #### TRUNCATE  ####

  def truncate_syscall(self, path, length):
    """
      http://linux.die.net/man/2/truncate
    """

    fd = self.open_syscall(path, O_RDWR, S_IRWXA)

    ret = self.ftruncate_syscall(fd, length)

    self.close_syscall(fd)

    return ret


  #### FTRUNCATE ####

  def ftruncate_syscall(self, fd, new_len):
    """
      http://linux.die.net/man/2/ftruncate
    """

    # check the fd
    if fd not in self.filedescriptortable and fd >= STARTINGFD:
      raise SyscallError("ftruncate_syscall","EBADF","Invalid old file descriptor.")

    if new_len < 0:
      raise SyscallError("ftruncate_syscall", "EINVAL", "Incorrect length passed.")

    # Acquire the fd lock...
    filesystemmetadatalock.acquire(True)
    self.filedescriptortable[fd]["lock"].acquire(True)

    try:

          # we will need the file size in a moment, but also need to check the type
      try:
        inode = self.filedescriptortable[fd]['inode']
      except KeyError:
        raise SyscallError("lseek_syscall","ESPIPE","This is a socket, not a file.")


      filesize = filesystemmetadata['inodetable'][inode]['size']

      if filesize < new_len:
        # we must pad with zeros
        blankbytecount = new_len - filesize
        fileobjecttable[inode].writeat('\0'*blankbytecount,filesize)

      else:
        # we must cut
        to_save = fileobjecttable[inode].readat(new_len,0)
        fileobjecttable[inode].close()
        # remove the old file
        removefile(FILEDATAPREFIX+str(inode))
        # make a new blank one
        fileobjecttable[inode] = openfile(FILEDATAPREFIX+str(inode),True)

        fileobjecttable[inode].writeat(to_save, 0)


      filesystemmetadata['inodetable'][inode]['size'] = new_len

    finally:
      self.filedescriptortable[fd]['lock'].release()
      filesystemmetadatalock.release()

    return 0


  #### MKNOD ####

  # for now, I am considering few assumptions:
  # 1. It is only used for creating character special files.
  # 2. I am not bothering about S_IRWXA in mode. (I need to fix this).
  # 3. /dev/null    : (1, 3)
  #    /dev/zero    : (1, 5)
  #    /dev/random  : (1, 8)
  #    /dev/urandom : (1, 9)
  #    The major and minor device number's should be passed in as a 2-tuple.

  def mknod_syscall(self, path, mode, dev):
    """
      http://linux.die.net/man/2/mknod
    """
    if path == '':
      raise SyscallError("mknod_syscall","ENOENT","The file does not exist.")

    truepath = normpath(path, self.cageid)

    # check if file already exists, if so raise an error.
    if truepath in fastinodelookuptable:
      raise SyscallError("mknod_syscall", "EEXIST", "file already exists.")

    # FIXME: mode should also accept user permissions(S_IRWXA)
    if not mode & S_FILETYPEFLAGS == mode:
      raise SyscallError("mknod_syscall", "EINVAL", "mode requested creation\
        of something other than regular file, device special file, FIFO or socket")

    # FIXME: for now, lets just only create character special file
    if not IS_CHR(mode):
      raise UnimplementedError("Only Character special files are supported.")

    # this has nothing to do with syscall, so I will raise UnimplementedError.
    if type(dev) is not tuple or len(dev) != 2:
      raise UnimplementedError("Third argument should be 2-tuple.")

    # Create a file, but don't open it. openning a chr_file should be done only using
    # open_syscall. S_IFCHR flag will ensure that the file is not opened.
    fd = self.open_syscall(path, mode | O_CREAT, S_IRWXA)

    # grab the lock
    filesystemmetadatalock.acquire(True)

    try:
      # add the major and minor device no.'s, I did it here so that the code can be managed
      # properly, instead of putting everything in open_syscall.
      inode = self.filedescriptortable[fd]['inode']
      filesystemmetadata['inodetable'][inode]['rdev'] = dev

      # close the file descriptor...

      return 0

    finally:
      filesystemmetadatalock.release()
      self.close_syscall(fd)

  #### Helper Functions for Character Files.####
  # currently supported devices are:
  # 1. /dev/null
  # 2. /dev/zero
  # 3. /dev/random
  # 4. /dev/urandom

  def _read_chr_file(self, inode, count):
    """
     helper function for reading data from chr_file's.
    """

    # check if it's a /dev/null.
    if filesystemmetadata['inodetable'][inode]['rdev'] == (1, 3):
      return ''
    # /dev/zero
    elif filesystemmetadata['inodetable'][inode]['rdev'] == (1, 5):
      return '\0' * count
    # /dev/random
    elif filesystemmetadata['inodetable'][inode]['rdev'] == (1, 8):
      return randombytes()[0:count]
    # /dev/urandom
    # FIXME: urandom is supposed to be non-blocking.
    elif filesystemmetadata['inodetable'][inode]['rdev'] == (1, 9):
      return randombytes()[0:count]
    else:
      raise UnimplementedError("Given device is not supported.")


  def _write_chr_file(self, inode, data):
    """
     helper function for writing data to chr_file's.
    """

    # check if it's a /dev/null.
    if filesystemmetadata['inodetable'][inode]['rdev'] == (1, 3):
      return len(data)
    # /dev/zero
    # There's no real /dev/zero file, just vanish it into thin air.
    elif filesystemmetadata['inodetable'][inode]['rdev'] == (1, 5):
      return len(data)
    # /dev/random
    # There's no real /dev/random file, just vanish it into thin air.
    elif filesystemmetadata['inodetable'][inode]['rdev'] == (1, 8):
      return len(data)
    # /dev/urandom
    # There's no real /dev/random file, just vanish it into thin air.
    elif filesystemmetadata['inodetable'][inode]['rdev'] == (1, 9):
      return len(data)
    else:
      raise UnimplementedError("Given device is not supported.")


  def _istat_helper_chr_file(self, inode):
    ret =  (5,          # st_dev, its always 5 for chr_file's.
            inode,                                 # inode
            filesystemmetadata['inodetable'][inode]['mode'],
            filesystemmetadata['inodetable'][inode]['linkcount'],
            filesystemmetadata['inodetable'][inode]['uid'],
            filesystemmetadata['inodetable'][inode]['gid'],
            filesystemmetadata['inodetable'][inode]['rdev'],
            filesystemmetadata['inodetable'][inode]['size'],
            0,                                     # st_blksize  ignored(?)
            0,                                     # st_blocks   ignored(?)
            filesystemmetadata['inodetable'][inode]['atime'],
            0,                                     # atime ns
            filesystemmetadata['inodetable'][inode]['mtime'],
            0,                                     # mtime ns
            filesystemmetadata['inodetable'][inode]['ctime'],
            0,                                     # ctime ns
          )
    return ret

  #### USER/GROUP IDENTITIES ####


  def getuid_syscall(self):
    """
      http://linux.die.net/man/2/getuid
    """
    # I will return 1000, since this is also used in stat
    return DEFAULT_UID

  def geteuid_syscall(self):
    """
      http://linux.die.net/man/2/geteuid
    """
    # I will return 1000, since this is also used in stat
    return DEFAULT_UID

  def getgid_syscall(self):
    """
      http://linux.die.net/man/2/getgid
    """
    # I will return 1000, since this is also used in stat
    return DEFAULT_GID

  def getegid_syscall(self):
    """
      http://linux.die.net/man/2/getegid
    """
    # I will return 1000, since this is also used in stat
    return DEFAULT_GID

  #TODO: We currently don't handle prctl or subreaper at all
  def getpid_syscall(self):
    """
      http://linux.die.net/man/2/getpid
    """
    return self.cageid

  def getppid_syscall(self):
    """
      http://linux.die.net/man/2/getppid
    """
    return master_cage_context[self.cageid].parent
    #NOTE: POSIX specifies that default parent should be
    #init, with a pid of 1, however pid 1 is a different
    #process in Lind, so 0 is our pseudo-init

  def getrlimit_syscall(self, res_type):
    """
      http://linux.die.net/man/2/getrlimit

      NOTE: Second argument is deprecated.
    """
    if res_type == RLIMIT_NOFILE:
      return (NOFILE_CUR, NOFILE_MAX)
    elif res_type == RLIMIT_STACK:
      return (STACK_CUR, STACK_MAX)
    else:
      raise UnimplementedError("The resource type is unimplemented.")

  def setrlimit_syscall(self, res_type, limits):
    """
      http://linux.die.net/man/2/setrlimit
    """

    if res_type == RLIMIT_NOFILE:
      # always make sure that, current value is less than or equal to Max value.
      if NOFILE_CUR > NOFILE_MAX:
        raise SyscallException("setrlimit", "EPERM", "Should not exceed Max limit.")

      # FIXME: I should update the value which should be per program.
      # since, Lind doesn't need this right now, I will pass.
      return 0

    else:
      raise UnimplementedError("This resource type is unimplemented")

  #### FLOCK SYSCALL  ####


  def flock_syscall(self, fd, operation):
    """
      http://linux.die.net/man/2/flock
    """

    if fd not in self.filedescriptortable:
      raise SyscallError("flock_syscall", "EBADF" "Invalid file descriptor.")

    # if we are anything besides the allowed flags, fail
    if operation & ~(LOCK_SH|LOCK_EX|LOCK_NB|LOCK_UN):
      raise SyscallError("flock_syscall", "EINVAL", "operation is invalid.")

    if operation & LOCK_SH:
      raise UnimplementedError("Shared lock is not yet implemented.")

    # check whether its a blocking or non-blocking lock...
    if operation & LOCK_EX and operation & LOCK_NB:
      if self.filedescriptortable[fd]['lock'].acquire(False):
        return 0
      else: # raise an error, if there's another lock already holding this
        raise SyscallError("flock_syscall", "EWOULDBLOCK", "Operation would block.")
    elif operation & LOCK_EX:
      self.filedescriptortable[fd]['lock'].acquire(True)
      return 0

    if operation & LOCK_UN:
      self.filedescriptortable[fd]['lock'].release()
      return 0

  #### RENAME SYSCALL  ####


  def rename_syscall(self, old, new):
    """
    http://linux.die.net/man/2/rename
    TODO: this needs to be fixed up.
    """
    # grab the lock
    filesystemmetadatalock.acquire(True)

    try:
      true_old_path = normpath(old, self.cageid)
      true_new_path = normpath(new, self.cageid)

      if true_old_path not in fastinodelookuptable:
        raise SyscallError("rename_syscall", "ENOENT", "Old file does not exist")

      if true_new_path == '':
        raise SyscallError("rename_syscall", "ENOENT", "New file does not exist")

      trueparentpath_old = normpath_parent(true_old_path, self.cageid)
      parentinode = fastinodelookuptable[trueparentpath_old]

      inode = fastinodelookuptable[true_old_path]

      newname = true_new_path.rsplit('/', 1)[-1]
      filesystemmetadata['inodetable'][parentinode]['filename_to_inode_dict'][newname] = inode

      fastinodelookuptable[true_new_path] = inode

      oldname = true_old_path.rsplit('/', 1)[-1]
      del filesystemmetadata['inodetable'][parentinode]['filename_to_inode_dict'][oldname]
      del fastinodelookuptable[true_old_path]

    finally:
      filesystemmetadatalock.release()
    return 0


  #### PIPE SYSCALL  ####

  def get_next_pipe(self):
    # let's get the next available pipe number.   
    for pipenumber in range(STARTING_PIPE, MAX_PIPE):
      if not pipenumber in pipetable:
        return pipenumber

    raise SyscallError("pipe_syscall","EMFILE","The maximum number of files are open.")

  def pipe_syscall(self):
    """
    http://linux.die.net/man/2/pipe
    """
    # lock to prevent things from changing while we look this up...

    self.fdtablelock.acquire(True)

    # ... but always release it...

    try:
      # get next available pipe number, and set up pipe
      pipenumber = self.get_next_pipe()
      pipetable[pipenumber] = lindpipe.LindPipe()
      pipefds = []
     
      # get an fd for each end of the pipe and set flags to RD_ONLY and WR_ONLY
      # append each to pipefds list

      for flag in [O_RDONLY, O_WRONLY]:
        try:
          nextfd = self.get_next_fd()
        except SyscallError, e:
          assert(e[0]=='open_syscall')
          raise SyscallError('pipe_syscall',e[1],e[2])

        self.filedescriptortable[nextfd] = {'pipe':pipenumber, 'lock':createlock(), 'flags':flag}
        pipefds.append(nextfd)    

      return pipefds

    finally:
      self.fdtablelock.release()
      

  # pipe2 currently not implemented

  def pipe2_syscall(self, flags):
    """
    http://linux.die.net/man/2/pipe2
    """
    # lock to prevent things from changing while we look this up...
    self.fdtablelock.acquire(True)
    # ... but always release it...
    try:
      #stuff
      pass
    finally:
      self.fdtablelock.release()


  # NOTE: this is only the part of fork that forks the file table and adds the parentage information. Most of fork
  # is implemented in parts of NaCl

  def fork_syscall(self, child_cageid):

    self.fdtablelock.acquire(True)

    try:
      master_cage_context[child_cageid] = cageobj(child_cageid, self.currentworkingdirectory, self.filedescriptortable, self.cageid)
      return child_cageid
    
    finally:
      self.fdtablelock.release()


  # Exec will do the same copying as fork, 
  # but we want to get rid of all the information from the old cage
  
  def exec_syscall(self, child_cageid):

    self.fdtablelock.acquire(True)

    try:
      #is CLOEXEC handled?
      master_cage_context[child_cageid] = self
      del master_cage_context[self.cageid]
      self.cageid = child_cageid
      # remove/reparent children
      return 0 #dummy for SuccessResponseBuilder
    
    finally:
      self.fdtablelock.release()
  

  def mmap_syscall(self, addr, leng, prot, flags, fildes, off):
    """
    http://linux.die.net/man/2/mmap
    """

    # lock to prevent things from changing while we look this up...
    filesystemmetadatalock.acquire(True)

    # ... but always release it...
    try:
      if leng==0:
        raise SyscallError("mmap_syscall", "EINVAL", "The value of len is zero")

      if 0 == flags & (MAP_PRIVATE | MAP_SHARED):
        raise SyscallError("mmap_syscall", "EINVAL", "The value of flags is invalid (neither MAP_PRIVATE nor MAP_SHARED is set)")

      #some ENOMEM guards might be nice, maybe even EAGAIN or EPERM

      if 0 != flags & MAP_ANONYMOUS:
        return repy_mmap(addr, leng, prot, flags, -1, 0)

      if fildes not in self.filedescriptortable:
        raise SyscallError("mmap_syscall", "EBADF", "The fildes argument is not a valid open file descriptor")

      self.filedescriptortable[fildes]['lock'].acquire(True)

      try:
        thisinode = self.filedescriptortable[fildes]['inode']
        mode = filesystemmetadata['inodetable'][thisinode]['mode']
        fflags = self.filedescriptortable[fildes]['flags']

        # We cannot mmap a repy file object in the way we want, so we get the
        # system file descriptor from the file object corresponding to the inode
        fobjno = fileobjecttable[thisinode].fobj.fileno()

        # If we want to write back our changes to the file (i.e. mmap with MAP_SHARED
        # as well as PROT_WRITE), we need the file to be open with the flag O_RDWR
        if (flags & MAP_SHARED) and (flags & PROT_WRITE) and not (fflags & O_RDWR):
          raise SyscallError("mmap_syscall", "EACCES", "File descriptor is not open RDWR, but MAP_SHARED and PROT_WRITE are set")
        if not (IS_REG(mode) or IS_CHR(mode)):
          raise SyscallError("mmap_syscall", "EACCES", "The fildes argument refers to a file whose type is not supported by mmap()")

        if IS_CHR(mode):
          raise SyscallError("mmap_syscall", "ENOTSUP", "Lind currently does not support mapping character files")

        filesize = filesystemmetadata['inodetable'][thisinode]['size']

        if off < 0 or off >= filesize:
          raise SyscallError("mmap_syscall", "ENXIO", "Addresses in the range [off,off+len) are invalid for the object specified by fildes.")

        # Because of NaCl's internal workings, we must allow mappings to extend past the end of a file

        return repy_mmap(addr, leng, prot, flags, fobjno, off)
      finally:
        self.filedescriptortable[fildes]['lock'].release()

    finally:
      filesystemmetadatalock.release()

   
  def munmap_syscall(self, addr, leng):
    """
    http://linux.die.net/man/2/munmap
    """
    # lock to prevent things from changing while we look this up...
    filesystemmetadatalock.acquire(True)

    # ... but always release it...
    try:
      if leng==0:
        raise SyscallError("mmap_syscall", "EINVAL", "The value of len is zero")
      return repy_mmap(addr, 
        leng, 
        PROT_NONE,
        MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED,
        -1,
        0)
    finally:
      filesystemmetadatalock.release()
