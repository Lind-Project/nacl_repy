import sys

# File Holds Constant values for Repy
#
#

# Holds the path to a python installation
#PATH_PYTHON_INSTALL = "\\Storage Card\\Program Files\\Python25\\python.exe"
#PATH_PYTHON_INSTALL = "\\Program Files\\Python25\\python.exe"
PATH_PYTHON_INSTALL = "C:\\Python26\\python.exe"

# Default Python Flags
# e.g. The "/new" flag is necessary for PythonCE to allow multiple instances
# The /nopcceshell disables the PythonCE window from opening and annoying the user
#PYTHON_DEFAULT_FLAGS = "/new /nopcceshell "
PYTHON_DEFAULT_FLAGS = ""

# Repy Installation path
#PATH_SEATTLE_INSTALL = "\\Storage Card\\Program Files\\Python25\\Lib\\SEATTLE\\"
#PATH_SEATTLE_INSTALL = "\\seattle\\"
PATH_SEATTLE_INSTALL = "Z:\\Projects\\seattle\\trunk\\repy\\"

# Current Working directory
REPY_CURRENT_DIR = "."

# Stores the directory repy started in
REPY_START_DIR = "."

# Polling Frequency for different Platforms, This is for non-CPU resources
# Poll non-cpu resources less often to reduce overhead
# Memory may need to be tighted, since it is possible to debilitate a system in less time than this.
RESOURCE_POLLING_FREQ_LINUX = .5 # Linux
RESOURCE_POLLING_FREQ_WIN = .5 # Windows
RESOURCE_POLLING_FREQ_WINCE = 4 # Mobile devices are pretty slow

# CPU Polling Frequency for different Platforms
CPU_POLLING_FREQ_LINUX = .1 # Linux
CPU_POLLING_FREQ_WIN = .1 # Windows
CPU_POLLING_FREQ_WINCE = .5 # Mobile devices are pretty slow


# These IP addresses are used to resolve our external IP address
# We attempt to connect to these IP addresses, and then check our local IP
# These addresses were choosen since they have been historically very stable
# They are from public universities
STABLE_PUBLIC_IPS = ["18.7.22.69",      # M.I.T
                    "171.67.216.8",     # Stanford
                    "169.229.131.81",   # Berkley
                    "140.142.12.202"]   # Univ. of Washington


#NACL Related Constats
# Descriptor for a bound socket that the NaCl browser plugin sets up
NACL_PLUGIN_BOUND_SOCK = 3

# Descriptors for connected sockets that the NaCl browser plugin sets up
NACL_PLUGIN_ASYNC_FROM_CHILD_FD = 6
NACL_PLUGIN_ASYNC_TO_CHILD_FD = 7

import os

repy_loc = os.getenv("REPY_PATH")
if repy_loc == None:
    print "[Lind] $REPY_PATH not set. Exiting."
    sys.exit(1)

NACL_PATH = repy_loc
NACL_ENV = None
