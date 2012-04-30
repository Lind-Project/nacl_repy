"""
Setup the Native Client Enviroment
 Chris Matthews cmatthew@cs.uvic.ca
 Fri May 27 13:30:25 PDT 2011

"""
import os
import sys

def setup_nacl_path(nacl_base):
  """Prepare a dict with the paths to all the components on the native client
  glibc runtime"""
  nacl_enviroment = {}
  
  #check nacl base is a dir we have access to
  if not os.path.exists(nacl_base):
    raise IOError("NaCl base directory does not exist.")
  nacl_enviroment["NACL_BASE"] = nacl_base
  

  bin_str = "bin"
  nacl_bin = os.path.join(nacl_base, bin_str)
  if not os.path.exists(nacl_bin):
    raise IOError("NaCl Linux Debug bin directory does not exist: %s"
                    %(nacl_bin))
  nacl_enviroment["NACL_BIN"] = nacl_bin

  selldr = os.path.join(nacl_bin, "sel_ldr")
  if  not os.path.exists(selldr):
    raise IOError("NaCl Linux Debug bin directory does not have sel_ldr: %s"
                    %(selldr))
  nacl_enviroment["NACL_SEL_LDR"] = selldr

  imcso = os.path.join(nacl_bin, "naclimc.so")
  if not os.path.exists(imcso):
    raise IOError("NaCl Linux Debug bin directory does not have naclimc.so: %s"
                    %(imcso))
  nacl_enviroment["NACL_IMCDOTSO"] = imcso
  
  #add this naclimc.so to the pythonpath and make sure it works
  sys.path.append(nacl_bin)
  try:
    import naclimc
  except ImportError, importerror:
    print "Unable to load the naclimc.so library."
    raise importerror

  # Where should nacl get its runtime libs from
  runnableld_str = "lib/glibc/runnable-ld.so"
  runnableld = os.path.join(nacl_base, runnableld_str)
  if not os.path.exists(runnableld):
    raise IOError("NaCl glibc runnable-ld.so is missing?: %s"%(runnableld))
 
  nacl_enviroment["NACL_DYN_LOADER"] = runnableld

  libs_str = "lib/libs/"
  libs = os.path.join(nacl_base, libs_str)
  if not os.path.exists(libs):
     raise IOError("NaCl gcc libs is missing?: %s"%(libs))
  
  nacl_enviroment["NACL_LIBRARY_DIR"] = libs
                

  return nacl_enviroment

