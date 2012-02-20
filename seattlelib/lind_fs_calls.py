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
ROOTDIRECTORYINODE = 1

METADATAFILENAME = 'lind.metadata'

FILEDATAPREFIX = 'linddata.'

filesystemmetadata = {}

# A lock that prevents inconsistencies in metadata
filesystemmetadatalock = createlock()


# fast lookup table...   (Should I deprecate this?)
fastinodelookuptable = {}

# contains open file descriptor information... (keyed by fd)
filedescriptortable = {}

# contains file objects... (keyed by inode)
fileobjecttable = {}

# I use this so that I can assign to a global string (currentworkingdirectory)
# without using global, which is blocked by RepyV2
fs_calls_context = {}

# Where we currently are at...
fs_calls_context['currentworkingdirectory'] = '/'


# This is raised to return an error...
class SyscallError(Exception):
  """A system call had an error"""


# This is raised if part of a call is not implemented
class UnimplementedError(Exception):
  """A call was called with arguments that are not fully implemented"""


def load_fs(name=METADATAFILENAME):
  """ Help to correcly load a filesystem, if one exists, otherwise
  make a new empty one.  To do this, check if metadata exists.
  If it doesnt, call _blank_fs_init, if it DOES exist call restore_metadata

  This is the best entry point for programs loading the file subsystem.
  """
  try:
    # lets see if the metadata file is already here?
    f = openfile(name, False)
  except FileNotFoundError, e:
    print "Note: No filesystem found, building a fresh one."
    _blank_fs_init()
  else:
    f.close()
    try:
      restore_metadata(name)
    except (IndexError, KeyError), e:
      print "Error: Cannot reload filesystem.  Run lind_fsck for details."
      exitall(1)



# To have a simple, blank file system, simply run this block of code.
# 

def _blank_fs_init():

  # kill all left over data files...
  # metadata will be killed on persist.
  for filename in listfiles():
    if filename.startswith(FILEDATAPREFIX):
      removefile(filename)

  # Now setup blank data structures
  filesystemmetadata['nextinode'] = 2
  filesystemmetadata['dev_id'] = 20
  filesystemmetadata['inodetable'] = {}
  filesystemmetadata['inodetable'][ROOTDIRECTORYINODE] = {'size':0, 
            'uid':1000, 'gid':1000, 
            'mode':16877,  # DIR+rwxr-xr-x
            'atime':1323630836, 'ctime':1323630836, 'mtime':1323630836,
            'linkcount':2,    # the number of dir entries...
            'filename_to_inode_dict': {'.':ROOTDIRECTORYINODE, 
            '..':ROOTDIRECTORYINODE}}
    
  fastinodelookuptable['/'] = ROOTDIRECTORYINODE




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
    entrypurepathname = _get_absolute_path(path+'/'+entryname)
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



# private helper function that converts a relative path or a path with things
# like foo/../bar to a normal path.
def _get_absolute_path(path):

  # If it's a relative path, prepend the CWD...
  if path[0] != '/':
    path = fs_calls_context['currentworkingdirectory'] + '/' + path


  # now I'll split on '/'.   This gives a list like: ['','foo','bar'] for 
  # '/foo/bar'
  pathlist = path.split('/')

  # let's remove the leading ''
  assert(pathlist[0] == '')
  pathlist = pathlist[1:]

  # Now, let's remove any '.' entries...
  while True:
    try:
      pathlist.remove('.')
    except ValueError:
      break

  # Also remove any '' entries...
  while True:
    try:
      pathlist.remove('')
    except ValueError:
      break

  # NOTE: This makes '/foo/bar/' -> '/foo/bar'.   I think this is okay.
  
  # for a '..' entry, remove the previous entry (if one exists).   This will
  # only work if we go left to right.
  position = 0
  while position < len(pathlist):
    if pathlist[position] == '..':
      # if there is a parent, remove it and this entry.  
      if position > 0:
        del pathlist[position]
        del pathlist[position-1]

        # go back one position and continue...
        position = position -1
        continue

      else:
        # I'm at the beginning.   Remove this, but no need to adjust position
        del pathlist[position]
        continue

    else:
      # it's a normal entry...   move along...
      position = position + 1


  # now let's join the pathlist!
  return '/'+'/'.join(pathlist)


# private helper function
def _get_absolute_parent_path(path):
  return _get_absolute_path(path+'/..')
  



#################### The actual system calls...   #############################




##### FSTATFS  #####


# return statfs data for fstatfs and statfs
def _istatfs_helper(inode):
  """
  """

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
  myfsdata['f_files'] = 1024*1024*512

  myfsdata['f_fsid'] = filesystemmetadata['dev_id']

  # we don't really have a limit, but let's say 254
  myfsdata['f_namelen'] = 254

  # same as blocksize...
  myfsdata['f_frsize'] = 4096 
  
  # it's supposed to be 5 bytes...   Let's try null characters...
  #CM: should be 8 bytes by my calc
  myfsdata['f_spare'] = '\x00'*8


  return myfsdata


def fstatfs_syscall(fd):
  """ 
    http://linux.die.net/man/2/fstatfs
  """

  # is the file descriptor valid?
  if fd not in filedescriptortable:
    raise SyscallError("fstatfs_syscall","EBADF","The file descriptor is invalid.")

  
  # if so, return the information...
  return _istatfs_helper(filedescriptortable[fd]['inode'])












##### STATFS  #####


def statfs_syscall(path):
  """ 
    http://linux.die.net/man/2/statfs
  """
  # in an abundance of caution, I'll grab a lock...
  filesystemmetadatalock.acquire(True)

  # ... but always release it...
  try:
    truepath = _get_absolute_path(path)

    # is the path there?
    if truepath not in fastinodelookuptable:
      raise SyscallError("statfs_syscall","ENOENT","The path does not exist.")

    thisinode = fastinodelookuptable[truepath]
      
    return _istatfs_helper(thisinode)

  finally:
    filesystemmetadatalock.release()







    




##### ACCESS  #####

def access_syscall(path, amode):
  """
    See: http://linux.die.net/man/2/access
  """

  
  # lock to prevent things from changing while we look this up...
  filesystemmetadatalock.acquire(True)

  # ... but always release the lock
  try:

    # get the actual name.   Remove things like '../foo'
    truepath = _get_absolute_path(path)

    if truepath not in fastinodelookuptable:
      raise SyscallError("access_syscall","ENOENT","A directory in the path does not exist or file not found.")

    # BUG: This code should really walk the directories instead of using this 
    # table...   This will have to be fixed for symlinks to work.
    thisinode = fastinodelookuptable[truepath]


    # BUG: This should take the UID / GID of the requestor in mind

    # if all of the bits for this file are set as requested, then indicate
    # success (return 0)
    if filesystemmetadata['inodetable'][thisinode]['mode'] & amode == amode:
      return 0

    raise SyscallError("access_syscall","EACESS","The requested access is denied.")

  finally:
    persist_metadata(METADATAFILENAME)
    # release the lock
    filesystemmetadatalock.release()






##### CHDIR  #####





def chdir_syscall(path):
  """ 
    http://linux.die.net/man/2/chdir
  """

  # Note: I don't think I need locking here.   I don't modify any state and 
  # only check the fs state once...

  # get the actual name.   Remove things like '../foo'
  truepath = _get_absolute_path(path)

  # If it doesn't exist...
  if truepath not in fastinodelookuptable:
    raise SyscallError("chdir_syscall","ENOENT","A directory in the path does not exist.")

  # let's update and return success (0)
  fs_calls_context['currentworkingdirectory'] = truepath
  

  return 0




##### MKDIR  #####

def mkdir_syscall(path, mode):
  """ 
    http://linux.die.net/man/2/mkdir
  """

  # lock to prevent things from changing while we look this up...
  filesystemmetadatalock.acquire(True)

  # ... but always release it...
  try:
    truepath = _get_absolute_path(path)

    # is the path there?
    if truepath in fastinodelookuptable:
      raise SyscallError("mkdir_syscall","EEXIST","The path exists.")

      
    # okay, it doesn't exist (great!).   Does it's parent exist and is it a 
    # dir?
    trueparentpath = _get_absolute_parent_path(path)

    if trueparentpath not in fastinodelookuptable:
      raise SyscallError("mkdir_syscall","ENOENT","Path does not exist.")

    parentinode = fastinodelookuptable[trueparentpath]
    if not IS_DIR(filesystemmetadata['inodetable'][parentinode]['mode']):
      raise SyscallError("mkdir_syscall","ENOTDIR","Path's parent is not a directory.")


    # TODO: I should check permissions...


    assert(mode & S_IRWXA == mode)

    # okay, great!!!   We're ready to go!   Let's make the new directory...
    dirname = truepath.split('/')[-1]

    # first, make the new directory...
    newinode = filesystemmetadata['nextinode']
    filesystemmetadata['nextinode'] += 1

    newinodeentry = {'size':0, 'uid':1000, 'gid':1000, 
            'mode':mode | S_IFDIR,  # DIR+rwxr-xr-x
            # BUG: I'm listing some arbitrary time values.  I could keep a time
            # counter too.
            'atime':1323630836, 'ctime':1323630836, 'mtime':1323630836,
            'linkcount':2,    # the number of dir entries...
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

def rmdir_syscall(path):
  """ 
    http://linux.die.net/man/2/rmdir
  """

  # lock to prevent things from changing while we look this up...
  filesystemmetadatalock.acquire(True)

  # ... but always release it...
  try:
    truepath = _get_absolute_path(path)

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


    trueparentpath = _get_absolute_parent_path(path)
    parentinode = fastinodelookuptable[trueparentpath]


    # remove the entry from the inode table...
    del filesystemmetadata['inodetable'][thisinode]


    # We're ready to go!   Let's clean up the file entry
    dirname = truepath.split('/')[-1]
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


def link_syscall(oldpath, newpath):
  """ 
    http://linux.die.net/man/2/link
  """

  # lock to prevent things from changing while we look this up...
  filesystemmetadatalock.acquire(True)

  # ... but always release it...
  try:
    trueoldpath = _get_absolute_path(oldpath)

    # is the old path there?
    if trueoldpath not in fastinodelookuptable:
      raise SyscallError("link_syscall","ENOENT","Old path does not exist.")

    oldinode = fastinodelookuptable[trueoldpath]
    # is oldpath a directory?
    if IS_DIR(filesystemmetadata['inodetable'][oldinode]['mode']):
      raise SyscallError("link_syscall","EPERM","Old path is a directory.")
  
    # TODO: I should check permissions...

    # okay, the old path info seems fine...
      
    truenewpath = _get_absolute_path(newpath)

    # does the newpath exist?   It shouldn't
    if truenewpath in fastinodelookuptable:
      raise SyscallError("link_syscall","EEXIST","newpath already exists.")
      
    # okay, it doesn't exist (great!).   Does it's parent exist and is it a 
    # dir?
    truenewparentpath = _get_absolute_parent_path(newpath)

    if truenewparentpath not in fastinodelookuptable:
      raise SyscallError("link_syscall","ENOENT","New path does not exist.")

    newparentinode = fastinodelookuptable[truenewparentpath]
    if not IS_DIR(filesystemmetadata['inodetable'][newparentinode]['mode']):
      raise SyscallError("link_syscall","ENOTDIR","New path's parent is not a directory.")


    # TODO: I should check permissions...



    # okay, great!!!   We're ready to go!   Let's make the file...
    newfilename = truenewpath.split('/')[-1]
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



def unlink_syscall(path):
  """ 
    http://linux.die.net/man/2/unlink
  """

  # lock to prevent things from changing while we do this...
  filesystemmetadatalock.acquire(True)

  # ... but always release it...
  try:
    truepath = _get_absolute_path(path)

    # is the path there?
    if truepath not in fastinodelookuptable:
      raise SyscallError("unlink_syscall","ENOENT","The path does not exist.")

    thisinode = fastinodelookuptable[truepath]
      
    # okay, is it a directory?
    if IS_DIR(filesystemmetadata['inodetable'][thisinode]['mode']):
      raise SyscallError("unlink_syscall","EISDIR","Path is a directory.")

    # TODO: I should check permissions...


    trueparentpath = _get_absolute_parent_path(path)
    parentinode = fastinodelookuptable[trueparentpath]




    # We're ready to go!   Let's clean up the file entry
    dirname = truepath.split('/')[-1]
    # remove the entry from the parent...

    del filesystemmetadata['inodetable'][parentinode]['filename_to_inode_dict'][dirname]
    # decrement the link count on the dir...
    filesystemmetadata['inodetable'][parentinode]['linkcount'] -= 1

    # clean up the fastinodelookuptable
    del fastinodelookuptable[truepath]


    # decrement the link count...
    filesystemmetadata['inodetable'][thisinode]['linkcount'] -= 1

    # If zero, remove the entry from the inode table
    if filesystemmetadata['inodetable'][thisinode]['linkcount'] == 0:
      del filesystemmetadata['inodetable'][thisinode]

      # TODO: I also would remove the file.   However, I need to do special
      # things if it's open, like wait until it is closed to remove it.
    
    return 0

  finally:
    persist_metadata(METADATAFILENAME)
    filesystemmetadatalock.release()






##### STAT  #####



def stat_syscall(path):
  """ 
    http://linux.die.net/man/2/stat
  """
  # in an abundance of caution, I'll grab a lock...
  filesystemmetadatalock.acquire(True)

  # ... but always release it...
  try:
    truepath = _get_absolute_path(path)

    # is the path there?
    if truepath not in fastinodelookuptable:
      raise SyscallError("stat_syscall","ENOENT","The path does not exist.")

    thisinode = fastinodelookuptable[truepath]
      
    return _istat_helper(thisinode)

  finally:
    persist_metadata(METADATAFILENAME)
    filesystemmetadatalock.release()







    


##### FSTAT  #####

def fstat_syscall(fd):
  """ 
    http://linux.die.net/man/2/fstat
  """

  # TODO: I don't handle socket objects.   I should return something like: 
  # st_mode=49590, st_ino=0, st_dev=0L, st_nlink=0, st_uid=501, st_gid=20, 
  # st_size=0, st_atime=0, st_mtime=0, st_ctime=0

  # is the file descriptor valid?
  if fd not in filedescriptortable:
    raise SyscallError("fstat_syscall","EBADF","The file descriptor is invalid.")

  
  # if so, return the information...
  return _istat_helper(filedescriptortable[fd]['inode'])



# private helper routine that returns stat data given an inode
def _istat_helper(inode):

  return (filesystemmetadata['dev_id'],          # st_dev
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






##### OPEN  #####


STARTINGFD = 10
MAXFD = 1024

# get the next free file descriptor
def get_next_fd():
  # let's get the next available fd number.   The standard says we need to 
  # return the lowest open fd number.
  for fd in range(STARTINGFD, MAXFD):
    if not fd in filedescriptortable:
      return fd

  raise SyscallError("open_syscall","EMFILE","The maximum number of files are open.")
  

def open_syscall(path, flags, mode):
  """ 
    http://linux.die.net/man/2/open
  """

  # in an abundance of caution, lock...   I think this should only be needed
  # with O_CREAT flags...
  filesystemmetadatalock.acquire(True)

  # ... but always release it...
  try:
    truepath = _get_absolute_path(path)

    # is the file missing?
    if truepath not in fastinodelookuptable:

      # did they use O_CREAT?
      if not O_CREAT & flags:
        raise SyscallError("open_syscall","ENOENT","The file does not exist.")
      
      # okay, it doesn't exist (great!).   Does it's parent exist and is it a 
      # dir?
      trueparentpath = _get_absolute_parent_path(path)

      if trueparentpath not in fastinodelookuptable:
        raise SyscallError("open_syscall","ENOENT","Path does not exist.")

      parentinode = fastinodelookuptable[trueparentpath]
      if not IS_DIR(filesystemmetadata['inodetable'][parentinode]['mode']):
        raise SyscallError("open_syscall","ENOTDIR","Path's parent is not a directory.")



      # okay, great!!!   We're ready to go!   Let's make the new file...
      filename = truepath.split('/')[-1]

      # first, make the new file's entry...
      newinode = filesystemmetadata['nextinode']
      filesystemmetadata['nextinode'] += 1

      # be sure there aren't extra mode bits...   No errno seems to exist for 
      # this.
      assert(mode & S_IRWXA == mode)

      newinodeentry = {'size':0, 'uid':1000, 'gid':1000, 
            'mode':S_IFREG + mode,  # FILE + their entries
            # BUG: I'm listing some arbitrary time values.  I could keep a time
            # counter too.
            'atime':1323630836, 'ctime':1323630836, 'mtime':1323630836,
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


    # TODO: I should check permissions...

    # At this point, the file will exist... 

    # Let's find the inode
    inode = fastinodelookuptable[truepath]

    
    # get the next fd so we can use it...
    thisfd = get_next_fd()
  

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

    filedescriptortable[thisfd] = {'position':position, 'inode':inode, 'lock':createlock(), 'flags':flags&O_RDWRFLAGS}

    # Done!   Let's return the file descriptor.
    return thisfd

  finally:
    persist_metadata(METADATAFILENAME)
    filesystemmetadatalock.release()







##### CREAT  #####

def creat_syscall(pathname, mode):
  """ 
    http://linux.die.net/man/2/creat
  """

  try:

    return open_syscall(pathname, O_CREAT | O_TRUNC | O_WRONLY, mode)
  
  except SyscallError, e:
    # If it's a system call error, return our call name instead.
    assert(e[0]=='open_syscall')
    
    raise SyscallError('creat_syscall',e[1],e[2])
  






##### LSEEK  #####

def lseek_syscall(fd, offset, whence):
  """ 
    http://linux.die.net/man/2/lseek
  """

  # check the fd
  if fd not in filedescriptortable:
    raise SyscallError("lseek_syscall","EBADF","Invalid file descriptor.")

  # Acquire the fd lock...
  filedescriptortable[fd]['lock'].acquire(True)


  # ... but always release it...
  try:
    # we will need the file size in a moment, but also need to check the type
    inode = filedescriptortable[fd]['inode']

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
      eventualpos = filedescriptortable[fd]['position']+offset
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
    filedescriptortable[fd]['position'] = eventualpos

    return eventualpos

  finally:
    # ... release the lock
    filedescriptortable[fd]['lock'].release()







##### READ  #####

def read_syscall(fd, count):
  """ 
    http://linux.die.net/man/2/read
  """

  # BUG: I probably need a filedescriptortable lock to prevent an untimely
  # close call or similar from messing everything up...

  # check the fd
  if fd not in filedescriptortable:
    raise SyscallError("read_syscall","EBADF","Invalid file descriptor.")

  # Is it open for reading?
  if IS_WRONLY(filedescriptortable[fd]['flags']): 
    raise SyscallError("read_syscall","EBADF","File descriptor is not open for reading.")

  # Acquire the fd lock...
  filedescriptortable[fd]['lock'].acquire(True)

  # ... but always release it...
  try:

    # get the inode so I can and check the mode (type)
    inode = filedescriptortable[fd]['inode']

    # Is it anything other than a regular file?
    if not IS_REG(filesystemmetadata['inodetable'][inode]['mode']):
      raise SyscallError("read_syscall","EINVAL","File descriptor does not refer to a regular file.")
      

    # let's do a readat!
    position = filedescriptortable[fd]['position']

    data = fileobjecttable[inode].readat(count,position)

    # and update the position
    filedescriptortable[fd]['position'] += len(data)

    return data

  finally:
    # ... release the lock
    filedescriptortable[fd]['lock'].release()









##### WRITE  #####



def write_syscall(fd, data):
  """ 
    http://linux.die.net/man/2/write
  """

  # BUG: I probably need a filedescriptortable lock to prevent an untimely
  # close call or similar from messing everything up...

  # check the fd
  if fd not in filedescriptortable:
    raise SyscallError("write_syscall","EBADF","Invalid file descriptor.")

  # Is it open for writing?
  if IS_RDONLY(filedescriptortable[fd]['flags']): 
    raise SyscallError("write_syscall","EBADF","File descriptor is not open for writing.")


  # Acquire the fd lock...
  filedescriptortable[fd]['lock'].acquire(True)

  # ... but always release it...
  try:

    # get the inode so I can update the size (if needed) and check the type
    inode = filedescriptortable[fd]['inode']

    # Is it anything other than a regular file?
    if not IS_REG(filesystemmetadata['inodetable'][inode]['mode']):
      raise SyscallError("write_syscall","EINVAL","File descriptor does not refer to a regular file.")
      

    # let's get the position...
    position = filedescriptortable[fd]['position']
    
    # and the file size...
    filesize = filesystemmetadata['inodetable'][inode]['size']

    # if the position is past the end of the file, write '\0' bytes to fill
    # up the gap...
    blankbytecount = position - filesize

    if blankbytecount > 0:
      # let's write the blank part at the end of the file...
      fileobjecttable[inode].writeat('\0'*blankbytecount,filesize)
      

    # writeat never writes less than desired in Repy V2.
    fileobjecttable[inode].writeat(data,position)

    # and update the position
    filedescriptortable[fd]['position'] += len(data)

    # update the file size if we've extended it
    if filedescriptortable[fd]['position'] > filesize:
      filesystemmetadata['inodetable'][inode]['size'] = filedescriptortable[fd]['position']
      
    # we always write it all, so just return the length of what we were passed.
    # We do not mention whether we write blank data (if position is after the 
    # end)
    return len(data)

  finally:
    # ... release the lock
    filedescriptortable[fd]['lock'].release()







##### CLOSE  #####

# private helper.   Get the fds for an inode (or [] if none)
def _lookup_fds_by_inode(inode):
  returnedfdlist = []
  for fd in filedescriptortable:
    if not IS_SOCK_DESC(fd) and filedescriptortable[fd]['inode'] == inode:
      returnedfdlist.append(fd)
  return returnedfdlist


# is this file descriptor a socket? 
def IS_SOCK_DESC(fd):
  if 'domain' in filedescriptortable[fd]:
    return True
  else:
    return False


# private helper that allows this to be called in other places (like dup2)
# without changing to re-entrant locks
def _close_helper(fd):
  # if we are a socket, we dont change disk metadata
  if IS_SOCK_DESC(fd):
    #TODO maybe something here? Like shutdown
    return 0

  # get the inode for the filedescriptor
  inode = filedescriptortable[fd]['inode']

  # If it's not a regular file, we have nothing to close...
  if not IS_REG(filesystemmetadata['inodetable'][inode]['mode']):

    # double check that this isn't in the fileobjecttable
    if inode in fileobjecttable:
      raise Exception("Internal Error: non-regular file in fileobjecttable")
   
    # and return success
    return 0

  # so it's a regular file.

  # get the list of file descriptors for the inode
  fdsforinode = _lookup_fds_by_inode(inode)

  # I should be in there!
  assert(fd in fdsforinode)

  # I should only close here if it's the last use of the file.   This can
  # happen due to dup, multiple opens, etc.
  if len(fdsforinode) > 1:
    # Is there more than one descriptor open?   If so, return success
    return 0

  # now let's close it and remove it from the table
  fileobjecttable[inode].close()

  del fileobjecttable[inode]

  # success!
  return 0



def close_syscall(fd):
  """ 
    http://linux.die.net/man/2/close
  """

  # BUG: I probably need a filedescriptortable lock to prevent race conditions

  # check the fd
  if fd not in filedescriptortable:
    raise SyscallError("close_syscall","EBADF","Invalid file descriptor.")

  # Acquire the fd lock, if there is one.
  if 'lock' in filedescriptortable[fd]:
    filedescriptortable[fd]['lock'].acquire(True)

  # ... but always release it...
  try:
    return _close_helper(fd)

  finally:
    # ... release the lock, if there is one
    if 'lock' in filedescriptortable[fd]:
      filedescriptortable[fd]['lock'].release()
    del filedescriptortable[fd]







##### DUP2  #####


# private helper that allows this to be used by dup
def _dup2_helper(oldfd,newfd):

  # if the new file descriptor is too low or too high
  # NOTE: I want to support dup2 being used to replace STDERR, STDOUT, etc.
  #      The Lind code may pass me descriptors less than STARTINGFD
  if newfd >= MAXFD or newfd < 0:
    # BUG: the STARTINGFD isn't really too low.   It's just lower than we
    # support
    raise SyscallError("dup2_syscall","EBADF","Invalid new file descriptor.")

  # if they are equal, return them
  if newfd == oldfd:
    return newfd

  # okay, they are different.   If the new fd exists, close it.
  if newfd in filedescriptortable:
    # should not result in an error.   This only occurs on a bad fd 
    _close_helper(newfd)


  # Okay, we need the new and old to point to the same thing.
  # NOTE: I am not making a copy here!!!   They intentionally both
  # refer to the same instance because manipulating the position, etc.
  # impacts both.
  filedescriptortable[newfd] = filedescriptortable[oldfd]

  return newfd




def dup2_syscall(oldfd,newfd):
  """ 
    http://linux.die.net/man/2/dup2
  """

  # check the fd
  if oldfd not in filedescriptortable:
    raise SyscallError("dup2_syscall","EBADF","Invalid old file descriptor.")

  # Acquire the fd lock...
  filedescriptortable[oldfd]['lock'].acquire(True)


  # ... but always release it...
  try:
    return _dup2_helper(oldfd, newfd)

  finally:
    # ... release the lock
    filedescriptortable[oldfd]['lock'].release()




##### DUP  #####

def dup_syscall(fd):
  """ 
    http://linux.die.net/man/2/dup
  """


  # check the fd
  if fd not in filedescriptortable:
    raise SyscallError("dup_syscall","EBADF","Invalid old file descriptor.")

  # Acquire the fd lock...
  filedescriptortable[fd]['lock'].acquire(True)

  try: 
    # get the next available file descriptor
    try:
      nextfd = get_next_fd()
    except SyscallError, e:
      # If it's an error getting the fd, return our call name instead.
      assert(e[0]=='open_syscall')
    
      raise SyscallError('dup_syscall',e[1],e[2])
  
    # this does the work.   It should _never_ raise an exception given the
    # checks we've made...
    return _dup2_helper(fd, nextfd)
  
  finally:
    # ... release the lock
    filedescriptortable[fd]['lock'].release()
  






##### FCNTL  #####



def fcntl_syscall(fd, cmd, *args):
  """ 
    http://linux.die.net/man/2/fcntl
  """
  # this call is totally crazy!   I'll just implement the basics and add more
  # as is needed.

  # BUG: I probably need a filedescriptortable lock to prevent race conditions

  # check the fd
  if fd not in filedescriptortable:
    raise SyscallError("fcntl_syscall","EBADF","Invalid file descriptor.")

  # Acquire the fd lock...
  filedescriptortable[fd]['lock'].acquire(True)

  # ... but always release it...
  try:

    # if we're getting the flags, return them... (but this is just CLO_EXEC, 
    # so ignore)
    if cmd == F_GETFD:
      assert(len(args) == 0)
      return 0

    # set the flags... (but this is just CLO_EXEC, so ignore...)
    elif cmd == F_SETFD:
      assert(len(args) == 1)
      assert(type(args[0]) == int or type(args[0]) == long)
      return 0

    # if we're getting the flags, return them...
    elif cmd == F_GETFL:
      assert(len(args) == 0)
      return filedescriptortable[fd]['flags']

    # set the flags...
    elif cmd == F_SETFL:
      assert(len(args) == 1)
      assert(type(args[0]) == int or type(args[0]) == long)
      filedescriptortable[fd]['flags'] = args[0]
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
    filedescriptortable[fd]['lock'].release()









##### GETDENTS  #####



def getdents_syscall(fd,quantity):
  """ 
    http://linux.die.net/man/2/getdents
  """

  # BUG: I probably need a filedescriptortable lock to prevent race conditions

  # BUG BUG BUG: Do I really understand this spec!?!?!?!

  # check the fd
  if fd not in filedescriptortable:
    raise SyscallError("getdents_syscall","EBADF","Invalid file descriptor.")

  # Acquire the fd lock...
  filedescriptortable[fd]['lock'].acquire(True)

  # ... but always release it...
  try:

    # get the inode so I can read the directory entries
    inode = filedescriptortable[fd]['inode']

    # Is it a directory?
    if not IS_DIR(filesystemmetadata['inodetable'][inode]['mode']):
      raise SyscallError("getdents_syscall","EINVAL","File descriptor does not refer to a directory.")
      
    returninodefntuplelist = []
    currentquantity = 0

    # let's move the position forward...
    startposition = filedescriptortable[fd]['position']

    # return tuple with inode, name, type tuples...
    for entryname,entryinode in list(filesystemmetadata['inodetable'][inode]['filename_to_inode_dict'].iteritems())[startposition:]:
      if currentquantity >= quantity:
        break

      # getdents returns the mode also (at least on Linux)...
      entrytype = get_direnttype_from_mode(filesystemmetadata['inodetable'][entryinode]['mode'])
      returninodefntuplelist.append((entryinode,entryname,entrytype))
      currentquantity=currentquantity + 1

    # and move the position along.   Go no further than the end...
    filedescriptortable[fd]['position'] = min(startposition+quantity, len(filesystemmetadata['inodetable'][inode]['filename_to_inode_dict']))
    
    return returninodefntuplelist

  finally:
    # ... release the lock
    filedescriptortable[fd]['lock'].release()


