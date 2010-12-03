import subprocess
import os
import tempfile
import pickle




def execute(args):
  """
  <Purpose>
    Given the list of arguments, this function will execute them within Python.
    
  <Arguments>
    args: Command line arguments.

  <Exceptions>
    None
    
  <Side Effects>
    None

  <Returns>
    Output after execution:
    (Standard Out, Standard Error)
  """
  process = subprocess.Popen(args,
                       stdout = subprocess.PIPE,
                       stderr = subprocess.PIPE)
      
  (stdoutdata, stderrdata) = process.communicate()
  
  return (stdoutdata, stderrdata)




def execute_repy(args):
  """
  <Purpose>
    Given the list of arguments, this function will execute them within Repy
    Execution Environment.
    
  <Arguments>
    args: Command line arguments

  <Exceptions>
    None
    
  <Side Effects>
    None

  <Returns>
    Output after execution:
    (Standard Out, Standard Error)
  """
  python = 'python'
  repy = 'repy.py'

  args = [python, repy] + args
  
  return execute(args)




def parse_directive(source_text, directive):
  """
  <Purpose>
    Given the file source, 'source-text', this function will search for the given directive.
    
  <Arguments>
    source_text: The source in which we are searching for a pragma directive.
    directive: The pragma directive we are searching for.

  <Exceptions>
    None
    
  <Side Effects>
    None

  <Returns>
    Return all relevant information for the specified directive:
    [(Directive, Type, Argument)... ]
  """
  result = []
  
  directive_string = '#' + directive
  
  for line in source_text.splitlines():
    if line.startswith(directive_string):
      stripped = line[len(directive_string):].strip()
      (pragma_type, separator, arg) = stripped.partition(' ')
      result.append((directive, pragma_type, arg))

  return result




def kill(identifier):
  """
  <Purpose>
    Given the identifier, this function will search for the corresponding file
    name, desirialize the file descriptor and kill the corresponding process.
    
  <Arguments>
    Identifier.

  <Exceptions>
    None
    
  <Side Effects>
    None

  <Returns>
    None
  """
  temp_dir = tempfile.gettempdir()
  file_path = identifier
  
  if temp_dir:
    file_path = os.path.join(temp_dir, file_path)
    
  temp_file_handle = open(file_path)
  
  temp_file_handle = open(file_path)
  process = pickle.load(temp_file_handle)
  temp_file_handle.close()

  process.kill()

  os.remove(file_path)




def spawn(args, identifier):
  """
  <Purpose>
    Given the list of arguments, this function will execute them and save the
    corresponding file descriptor using the identifier as a name.
    
  <Arguments>
    Command.
    Identifier.

  <Exceptions>
    None
    
  <Side Effects>
    None

  <Returns>
    None
  """
  
  # We have to pipe the output. Otherwise, the process's output fills up and its
  # write attempt eventually blocks, preventing it from continuing.
  proccess = subprocess.Popen(args,
                              stdout = subprocess.PIPE,
                              stderr = subprocess.PIPE)
  
  temp_dir = tempfile.gettempdir()
  file_path = identifier
  
  if temp_dir:
    file_path = os.path.join(temp_dir, file_path)
  
  temp_file_handle = open(file_path, 'w')
  pickle.dump(proccess, temp_file_handle, 2)
  temp_file_handle.close()
