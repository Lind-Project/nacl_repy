
###### shared section ########

# Module that ensures application code runs only once...
import os

# allow me to specify error names instead of numbers
import errno

# need to know the os type...
import platform

# printing to sys.stderr
import sys

# returns a process lock (True) or if the lock is held returns the PID of the 
# process holding the lock
# NOTE: one must call stillhaveprocesslock periodically to guard against a user
# deleting the tmp file
def stillhaveprocesslock(lockname):
  #print >> sys.stderr, 'Verifying we still have lock for '+lockname
  val =  getprocesslock(lockname) 
  return val == os.getpid() or val == True

def getprocesslock(lockname):

  # NOTE: This intentionally doesn't use the superior checking mechanism in
  # nonportable because we don't want to import potentially broken modules...
  ostype = platform.system()
  if ostype == 'Windows' or ostype == 'Microsoft':
    #print >> sys.stderr, 'Getting some Windows lockmutex'
    return getprocesslockmutex(lockname)
  elif ostype == 'Linux' or ostype == 'Darwin' or 'BSD' in ostype:
    # Previously I also checked for O_EXLOCK and used that if available.
    # This didn't work well when I had to add the umask / perm hack to properly
    # support multiple users.   As a result, that code is removed.
    return getprocesslockflock(lockname)   
  else:
    raise Exception, 'Unknown operating system:'+ostype


def releaseprocesslock(lockname):

  # NOTE: This intentionally doesn't use the superior checking mechanism in
  # nonportable because we don't want to import potentially broken modules...
  ostype = platform.system()
  if ostype == 'Windows' or ostype == 'Microsoft':
    return releaseprocesslockmutex(lockname)
  elif ostype == 'Linux' or ostype == 'Darwin' or 'BSD' in ostype:
    # unfortunately, it seems *NIXes differ on whether O_EXLOCK is supported
    return releaseprocesslockflock(lockname)   
  else:
    raise Exception, 'Unknown operating system:'+ostype



###### MAC / LINUX section ########

# NOTE: In order to avoid leaking file descriptors, if I've tried to get the
# process lock before I'll close the old one on success or the new one on 
# failure
oldfiledesc = {}

# BUG FIX:   sometimes the PID is shorter than others.   Notice, I don't
# truncate the file, so I need to ensure I overwrite the digits of a  pid 
# that could be more digits than mine...
pidendpadding = "      "



def getprocesslockflock(lockname):
  global oldfiledesc
  # the file we'll use
  lockfn = "/tmp/runoncelock."+lockname
    
  try:
    # Use 0666 in octal (rw-rw-rw-).   This is needed because if a different
    # user tries to access an old file, they need to be able to overwrite it.

    # Unfortunately I need to unset the umask to do this!   I'll reset it and
    # hope this doesn't break anything in the mean time.   
    try:
      oldumask = os.umask(000)
      fd = os.open(lockfn,os.O_CREAT | os.O_RDWR | os.O_NONBLOCK, int('0666',8))
    finally:
      # restore the umask
      os.umask(oldumask)

  except (OSError, IOError), e:
    if e[0] == errno.EACCES or e[0] == errno.EAGAIN:
      # okay, they must have started already.
      pass   
      #print >> sys.stderr, 'Getting flock open failed, must have already started'
    else:
      #print >> sys.stderr, 'badness going down in opening for flock'
      raise
  else:
    try:
      import fcntl
      fcntl.flock(fd,fcntl.LOCK_EX | fcntl.LOCK_NB)
      # See above (under definition of pidendpadding) about why this is here...
      os.write(fd,str(os.getpid())+pidendpadding)
      #print >> sys.stderr, 'wrote pid ('+str(os.getpid())+') to flocked file'
      if lockname in oldfiledesc:
        os.close(oldfiledesc[lockname])
      oldfiledesc[lockname] = fd
      return True
    except (OSError, IOError), e:
      os.close(fd)
      if e[0] == errno.EACCES or e[0] == errno.EAGAIN:
        # okay, they must have started already.
        pass
        #print >> sys.stderr, 'Getting flock fcntl.flock failed, must have already started'
      else:
        # we weren't expecting this...
        #print >> sys.stderr, 'badness going down in fcntl.flock for flock'
        raise

  # Let's return the PID
  fo = open(lockfn)
  pidstring = fo.read()
  fo.close()
  #print >> sys.stderr, 'pid '+pidstring+' has the flock for '+lockname
  return int(pidstring)


def releaseprocesslockflock(lockname):
  if lockname in oldfiledesc:
    import fcntl
    fcntl.flock(oldfiledesc[lockname],fcntl.LOCK_UN)
    os.close(oldfiledesc[lockname])
    del oldfiledesc[lockname]
    #print >> sys.stderr, 'removed flock for '+lockname





##### WINDOWS SECTION ##########

try:
  import windows_api as windowsAPI
except:
  windowsAPI = None
  pass

# NOTE: in Windows, only the current user can get the PID for their process.
# This makes sense because only the current user should uninstall their code.

# I need to ensure I don't close the handle to the mutex.   I'll make it a
# global so it isn't cleaned up.
mutexhandle = {}


# this is a helper function that opens the right location in the registry
# if write is set to true, it creates any missing items.
def openkey(basekey, keylist, write=False):
  import _winreg
  if keylist == []:
    return basekey
  else:
    if write:
      try:
        thisKey = _winreg.OpenKey(basekey, keylist[0], 0, _winreg.KEY_SET_VALUE | _winreg.KEY_WRITE) 
      except WindowsError:
        # need to create the key
        thisKey = _winreg.CreateKey(basekey, keylist[0])
      # return the remaining keys
      return openkey(thisKey, keylist[1:], write)

    else:
      # opening a key for reading...
      # I allow this call to raise an WindowsError for a non-existent key
      thisKey = _winreg.OpenKey(basekey, keylist[0], 0, _winreg.KEY_READ)
      return openkey(thisKey, keylist[1:], write)
        

# How many milliseconds to wait to acquire mutex?
WAIT_TIME = 200

# return True on success, and either the pid of the locking process or False 
# on failure.
def getprocesslockmutex(lockname):
  import _winreg
  regkeyname = r"runonce."+lockname

  # traverse registry path
  registrypath = ["SOFTWARE","UW","Seattle","1.0"]

  # locked, do we own the mutex?
  locked = False

  # Does a handle already exist?
  if lockname in mutexhandle:
    # Lets try to get ownership of it
    locked = windowsAPI.acquire_mutex(mutexhandle[lockname], WAIT_TIME)
  else:
    # Lets create the mutex, then get ownership
    try:
      mutexhandle[lockname] = windowsAPI.create_mutex('Global\\runonce.'+lockname)
      locked = windowsAPI.acquire_mutex(mutexhandle[lockname], WAIT_TIME)
    except windowsAPI.FailedMutex:
      # By default, we don't have the lock, so its okay
      pass

  # We own it!
  if locked:
    # get the place to write
    thekey = openkey(_winreg.HKEY_CURRENT_USER, registrypath, write=True) 

    try:
      _winreg.SetValueEx(thekey,regkeyname,0, _winreg.REG_SZ, str(os.getpid()))
    except EnvironmentError,e:                                          
      print thekey, regkeyname, 0, _winreg.REG_SZ, os.getpid()
      print "Encountered problems writing into the Registry..."+str(e)
      raise

    _winreg.CloseKey(thekey)

    return True      

  try:
    thekey = openkey(_winreg.HKEY_CURRENT_USER, registrypath, write=False)
  except WindowsError:
    # the key didn't exist.  Must be stored under another user...
    return False

  # I'll return once there are no more values or I've found the key...
  try:
    val, datatype = _winreg.QueryValueEx(thekey, regkeyname)
    return int(val)
  except EnvironmentError, e:                                          
    # not found...   This is odd.   The registry path is there, but no key...
    return False

  finally:
    _winreg.CloseKey(thekey)

# Release a windows mutex
def releaseprocesslockmutex(lockname):
  # Does the handle exist?
  if lockname in mutexhandle:
    try:
      # Release the mutex
      windowsAPI.release_mutex(mutexhandle[lockname])
    except windowsAPI.NonOwnedMutex, e:
      # Its fine to release when we don't own, handle is not release on failure
      pass
