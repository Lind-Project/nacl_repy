import repy_constants
import lind_launcher

class NaClRuntime:
  """An wrapper for a running NaCl instance"""

  def __init__(self, proc, fd, recv, send):
    self._proc = proc
    self._fd = fd
    self._recv = recv
    self._send = send

    
  def isalive(self):
    """
    <Purpose>
    
      Is the process which is running this Native Client instance still running?
    
    <Returns>

      True when the process is still running, false otherwise.

    """  
    return self.proc.poll() == None

  def send(self, message):
    """Send a message string to the Native Client instance.

    TODO: test this... 
    """
    
    self._send.imc_sendmsg(message)
  
  def recv(self, size):
    """
    <Purpose> 

      Ask for SIZE bytes of message from the Native Client instance. 
    
    <Arguments>
    
      size: the number of bytes to pull.

    <Returns>
      a messsage string, or a string containing "EOT" if channel closed.
    """
    try:
      (message, crap) = self._recv.imc_recvmsg(size)
    except Exception, e:
      message = "EOT"
    return message
  
  def __str__(self):
    return "Binray running in PID: " + str(self._proc)



def safelyexecutenativecode(binary_file_name, arglist):
  """
  <Purpose>

    Experimental! Executes code in an arbitrary programming language that was compiled 
    using the toolchain.

  <Arguments>

    binary: The file name of the binary to launch.

    arglist: A list of strings that should be used as the command line arguments.

  <Exceptions>

    TODO

    A CodeUnsafeError? is raised if the binary does not pass verification. 

    RepyArgumentError? is raised if the binary is not a string or the arglist 
    does not contain only strings
    
    LaunchFailedError? is raised if the launch fails

  <Side Effects>

    Another process will be launched to execute the program. This has memory 
    and CPU ramifications, that will be accounted for in the current vessel.

  <Resource Consumption>

    TODO (we may change the resource model to account for processes 
    separately from threads)

  <Returns>

    A NaclRuntime object which can be used to check if the process is alive,
    and send and receive data to the process. 

  """
  if safebinary == True:
    #Perhaps it is better to do the launch directly in here?
    return lind_launcher.launch_nacl(repy_constants.NACL_ENV, binary_file_name, arglist)
  else:
    return None
