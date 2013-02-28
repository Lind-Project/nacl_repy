"""
  Author: Justin Cappos
  Module: File system utilities.   Copies files into the Lind FS from a POSIX
          file system, creates a blank fs, removes files and directories,
          lists files in the fs, etc.

  Start Date: Feb 28th, 2012

  I want to make a few basic utilities for manipulating a lind fs.   My 
  goal here isn't to make a perfect, production-ready tool, but instead to
  make something that is good enough for us to use in normal cases.   Thus,
  my focus is on baseline functionality.   Very trivial things, like creating
  directories or changing file permissions, can be handled with the 
  appropriate system call directly and thus will not be used here.  More 
  complex things can be handled via fuse and / or added later.

  This module may be used directly from the command line or imported.

  Note: I will rely on the real POSIX API and the lind POSIX API to behave
  as advertised.

"""

import lind_test_server

from lind_fs_constants import *


import os

import sys



def _mirror_stat_data(posixfn, lindfn):
  # internal function to take a lind filename (or dirname, etc.) and change
  # it to have similar metadata to a posixfn.   This includes perms, uid, gid

  statdata = os.stat(posixfn)
  
  # I only want the file perms, not things like 'IS_DIR'.  
  # BUG (?): I think this ignores SETUID, SETGID, sticky bit, etc.
  lind_test_server.chmod_syscall(lindfn, S_IRWXA & statdata[0])

  # Note: chown / chgrp aren't implemented!!!   We would call them here.
  #lind_test_server.chown_syscall(lindfn, statdata[4])
  #lind_test_server.chgrp_syscall(lindfn, statdata[5])




def cp_into_lind(fullfilename, rootpath='.', createmissingdirs=True):
  """
   <Purpose>
      Copies a file from POSIX into the Lind FS.   It takes the abs path to 
      the file ('/etc/passwd') and looks for it in the POSIX FS off of the 
      root path.   For example, rootpath = '/foo' -> '/foo/etc/passwd'.
      If the file exists, it is overwritten...

   <Arguments>
      fullfilename: The location the file should live in the Lind FS.  
          This must be an absolute path (from the root).

      rootpath: The directory in the POSIX fs to start looking for that file.
          Note: it must be in the directory structure specified by fullfilename
   
      createmissingdirs:  Should missing dirs in the path be created?

   <Exceptions>
      IOError: If the file does not exist, the directory can't be created
          (for example, if there is a file of the same name), or 
          createmissingdirs is False, but the path is invalid.

   <Side Effects>
      The obvious file IO operations

   <Returns>
      None
  """
  
  # check for the file.
  posixfn = os.path.join(rootpath,fullfilename)

  if not os.path.exists(posixfn):
    raise IOError("Cannot locate file on POSIX FS: '"+posixfilename+"'")

  if not os.path.isfile(posixfn):
    raise IOError("POSIX FS path is not a file: '"+posixfilename+"'")
  

  # now, we should check / make intermediate dirs if needed...
  # we will walk through the components of the dir and look for them...

  # this removes '.', '///', and similar.   
  # BUG: On Windows, this converts '/' -> '\'.   I don't think lind FS handles
  # '\'...

  normalizedlindfn = os.path.normpath(fullfilename)
  normalizedlinddirname = os.path.dirname(normalizedlindfn)

  # go through the directories and check if they are there, possibly creating
  # needed ones...
  currentdir = ''
  # NOT os.path.split!   I want each dir!!!
  for thisdir in normalizedlinddirname.split('/'):
    currentdir +=thisdir + '/'

    try:
      # check if this is a directory that exists
      if IS_DIR(lind_test_server.stat_syscall(currentdir)[2]):
        # all is well
        continue
      # otherwise, it exists, but isn't a dir...   
      raise IOError("LIND FS path exists and isn't a dir: '"+currentdir+"'")

    except lind_test_server.SyscallError, e:
      # must be missing dir or else let the caller see this!
      if e[1] != "ENOENT":   
        raise

      # okay, do I create it?
      if not createmissingdirs:
        raise IOError("LIND FS path does not exist but should not be created: '"+currentdir+"'")

      # otherwise, make it ...  
      lind_test_server.mkdir_syscall(currentdir,S_IRWXA)
      # and copy over the perms, etc.
      _mirror_stat_data(os.path.join(rootpath,currentdir),currentdir)


  # Okay, I have made the path now.   Only one thing remains, adding the file
  posixfo = open(posixfn)
  filecontents = posixfo.read()
  posixfo.close()

  # make the new file, truncating any existing contents...
  lindfd = lind_test_server.open_syscall(normalizedlindfn, O_CREAT|O_EXCL|O_TRUNC|O_WRONLY, S_IRWXA)

  # should write all at once...
  datalen = lind_test_server.write_syscall(lindfd, filecontents)
  assert(datalen == len(filecontents))

  lind_test_server.close_syscall(lindfd)

   # fix stat, etc.
  _mirror_stat_data(posixfn,normalizedlindfn)





def _find_all_paths_recursively(startingpath):
  # helper for list_all_lind_paths.   It recursively looks at all child dirs
  
  knownitems = []

  # I need to open the dir to use getdents...
  dirfd = lind_test_server.open_syscall(startingpath,0,0)

  # build a list of all dents.   These have an odd format:
  #  [(inode, filename, d_type (DT_DIR, DR_REG, etc.), length of entry), ...]
  # We only care about the filename and d_type.
  mydentslist = []

  # Note: the length parameter is odd, it's related to data structure space, so
  # it doesn't map to python cleanly.   So long as it's > the largest possible
  # entry size, this code should work though.
  thesedents = lind_test_server.getdents_syscall(dirfd,10000)
  while thesedents:
    mydentslist += thesedents
    thesedents = lind_test_server.getdents_syscall(dirfd,10000)

  lind_test_server.close_syscall(dirfd)

  # to make the output correct, if the dir is '/', don't print it.
  if startingpath == '/':
    startingpath = ''

  for dent in mydentslist:
    # ignore '.' and '..' because they aren't interesting and we don't want
    # to loop forever.
    if dent[1]=='.' or dent[1]=='..':
      continue
   
    thisitem = startingpath+'/'+dent[1]

    # add it...
    knownitems.append(thisitem)

    # if it's a directory, recurse...
    if dent[2]==DT_DIR:
      knownitems = knownitems + _find_all_paths_recursively(thisitem)

  return knownitems
    



def list_all_lind_paths(startingdir='/'):
  """
   <Purpose>
      Returns a list of all files / dirs in the lind fs.   Each has an absolute
      name.   This is similar to 'find startingdir'.

   <Arguments>
      startingdir: the path to start with.

   <Exceptions>
      If startingdir is not a dir, this is a SyscallError.

   <Side Effects>
      None

   <Returns>
      A list of strings that correspond to absolute names.   For example:
      ['/','/etc/','/etc/passwd']
  """
  
  # BUG: This code may need to be revisited with symlinks...

  # this will throw exceptions when given bad data...
  lind_test_server.chdir_syscall(startingdir)

  return _find_all_paths_recursively(startingdir)


  


def print_usage():
  print """
Usage: lind_fs_utils.py [commandname] [options...]

Where commandname is one of the following:

help                       : print this message
usage                      : print this message
mkdir dir1 [dir2...]       : create a directory
cp root file1 [file2...]   : copies files from the root into the lindfs.   For
                             example, cp bar /etc/passwd /bin/ls will copy
                             bar/etc/passwd, bar/bin/ls as /etc/passwd, /bin/ls
find [startingpath]        : print the names of all files / paths in the fs
                             This is much like 'find startingpath'
format                     : make a new blank fs, removing the current one.
deltree dirname            : delete a directory and all it contains
rm file1 [file2...]        : delete a file
rmdir dir1 [dir2...]       : delete a directory
"""




def main():
  # I can be imported as a module too!!!
  if len(sys.argv)==1:
    print_usage()
    return

  command = sys.argv[1]
  args = sys.argv[2:]



#help                       : print this message
#usage                      : print this message
  if command == 'help' or command == 'usage':
    print_usage()



#cp root file1 [file2...]   : copies files from the root into the lindfs.   For
#                             example, cp bar /etc/passwd /bin/ls will copy
#                             bar/etc/passwd, bar/bin/ls as /etc/passwd, /bin/ls
  elif command == 'cp':
    lind_test_server.load_fs()

    if len(args)<2:
      print 'Too few arguments to cp.   Must specify root and at least one file'
      return

    root = args[0]
    for filetocp in args[1:]:
      cp_into_lind(filetocp, rootpath=root)



#find [startingpath]        : print the names of all files / paths in the fs
#                             This is much like 'find /'
  elif command == 'find':
    lind_test_server.load_fs()

    if len(args)>1:
      print 'Too many arguments to find.   Takes an optional path'
      return
    elif len(args) == 0:
      startingpath = '/'
    elif len(args)==1:
      startingpath = args[0]
      
    allpathlist = list_all_lind_paths(startingdir=startingpath)
    # want to print this more cleanly than as a list
    for thispath in allpathlist:
      print thispath


#format                     : make a new blank fs, removing the current one.
  elif command == 'format':
    lind_test_server._blank_fs_init()


#deltree dirname            : delete a directory and all it contains
  elif command == 'deltree':
    lind_test_server.load_fs()

    if len(args)!= 1:
      print 'deltree takes exactly one argument, the dir to remove'
      return

    print 'Unimplemented...'

#rm file1 [file2...]        : delete a file
  elif command == 'rm':
    lind_test_server.load_fs()

    if len(args) == 0:
      print 'rm takes one or more arguments'
      return

    for filename in args:
      lind_test_server.unlink_syscall(filename)



#mkdir dir1 [dir2...]       : create a directory
  elif command == 'mkdir':
    lind_test_server.load_fs()

    if len(args) == 0:
      print 'mkdir takes one or more arguments'
      return

    for dirname in args:
      lind_test_server.mkdir_syscall(dirname,S_IRWXA)



#rmdir dir1 [dir2...]       : delete a directory
  elif command == 'rmdir':
    lind_test_server.load_fs()

    if len(args) == 0:
      print 'rmdir takes one or more arguments'
      return

    for dirname in args:
      lind_test_server.rmdir_syscall(dirname)


# OTHERWISE?
  else:
    print "ERROR: command unknown"
    print
    print_usage()
    return



if __name__ == '__main__':
  main()
