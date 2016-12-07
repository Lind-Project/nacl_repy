
# I'm importing these so I can neuter the calls so that they aren't 
# restricted...
import safe
import emulfile
import emulmisc
import nonportable
import namespace
import nanny
import virtual_namespace


# JAC: Save the calls in case I want to restore them.   This is useful if 
# repy ends up wanting to use either repyportability or repyhelper...
# This is also useful if a user wants to enforce restrictions on the repy
# code they import via repyhelper (they must use 
# restrictions.init_restriction_tables(filename) as well)...
oldrestrictioncalls = {}
oldrestrictioncalls['nanny.tattle_quantity'] = nanny.tattle_quantity
oldrestrictioncalls['nanny.tattle_add_item'] = nanny.tattle_add_item
oldrestrictioncalls['nanny.tattle_remove_item'] = nanny.tattle_remove_item
oldrestrictioncalls['nanny.is_item_allowed'] = nanny.is_item_allowed
oldrestrictioncalls['nanny.get_resource_limit'] = nanny.get_resource_limit
oldrestrictioncalls['nanny._resources_allowed_dict'] = nanny._resources_allowed_dict
oldrestrictioncalls['nanny._resources_consumed_dict'] = nanny._resources_consumed_dict
oldrestrictioncalls['emulfile.assert_is_allowed_filename'] = emulfile._assert_is_allowed_filename


port_list = [x for x in range(60000, 65000)]

default_restrictions = {'loopsend': 100000000.0, 'netrecv': 1000000.0, 'random': 10000.0, 'insockets': 500.0, 'fileread': 10000000.0, 'netsend': 1000000.0, 'connport': set(port_list), 'messport': set(port_list), 'diskused': 10000000000.0, 'filewrite': 10000000.0, 'lograte': 3000000.0, 'filesopened': 500.0, 'looprecv': 100000000.0, 'events': 1000.0, 'memory': 150000000000.0, 'outsockets': 500.0, 'cpu': 1.0}


resource_used = {'diskused': 0.0, 'renewable_update_time': {'fileread': 0.0, 'loopsend': 0.0, 'lograte': 0.0, 'netrecv': 0.0, 'random': 0.0, 'filewrite': 0.0, 'looprecv': 0.0, 'netsend': 0.0, 'cpu': 0.0}, 'fileread': 0.0, 'loopsend': 0.0, 'filesopened': set([]), 'lograte': 0.0, 'netrecv': 0.0, 'random': 0.0, 'insockets': set([]), 'filewrite': 0.0, 'looprecv': 0.0, 'events': set([]), 'messport': set([]), 'memory': 0.0, 'netsend': 0.0, 'connport': set([]), 'outsockets': set([]), 'cpu': 0.0}

def _do_nothing(*args):
  pass

def _always_true(*args):
  return True


# Overwrite the calls so that I don't have restrictions (the default)
def override_restrictions():
  """
   <Purpose>
      Turns off restrictions.   Resource use will be unmetered after making
      this call.   (note that CPU / memory / disk space will never be metered
      by repyhelper or repyportability)

   <Arguments>
      None.
         
   <Exceptions>
      None.

   <Side Effects>
      Resource use is unmetered / calls are unrestricted.

   <Returns>
      None
  """
  nonportable.get_resources = _do_nothing

  nanny.tattle_quantity = _do_nothing
  nanny.tattle_add_item = _do_nothing
  nanny.tattle_remove_item = _do_nothing
  nanny.is_item_allowed = _always_true
  nanny.get_resource_limit = _do_nothing
  nanny._resources_allowed_dict = default_restrictions
  nanny._resources_consumed_dict = resource_used
  emulfile.assert_is_allowed_filename = _do_nothing
  


# Sets up restrictions for the program
# THIS IS ONLY METERED FOR REPY CALLS AND DOES NOT INCLUDE CPU / MEM / DISK 
# SPACE
def initialize_restrictions(restrictionsfn):
  """
   <Purpose>
      Sets up restrictions.   This allows some resources to be metered 
      despite the use of repyportability / repyhelper.   CPU / memory / disk 
      space will not be metered.   Call restrictions will also be enabled.

   <Arguments>
      restrictionsfn:
        The file name of the restrictions file.
         
   <Exceptions>
      None.

   <Side Effects>
      Enables restrictions.

   <Returns>
      None
  """
  nanny.start_resource_nanny(restrictionsfn)

def enable_restrictions():
  """
   <Purpose>
      Turns on restrictions.   There must have previously been a call to
      initialize_restrictions().  CPU / memory / disk space will not be 
      metered.   Call restrictions will also be enabled.

   <Arguments>
      None.
         
   <Exceptions>
      None.

   <Side Effects>
      Enables call restrictions / resource metering.

   <Returns>
      None
  """
  # JAC: THIS WILL NOT ENABLE CPU / MEMORY / DISK SPACE
  nanny.tattle_quantity = oldrestrictioncalls['nanny.tattle_quantity']
  nanny.tattle_add_item = oldrestrictioncalls['nanny.tattle_add_item'] 
  nanny.tattle_remove_item = oldrestrictioncalls['nanny.tattle_remove_item'] 
  nanny.is_item_allowed = oldrestrictioncalls['nanny.is_item_allowed'] 
  nanny.get_resource_limit = oldrestrictioncalls['nanny.get_resource_limit']
  nanny._resources_allowed_dict = oldrestrictioncalls['nanny._resources_allowed_dict']
  nanny._resources_consumed_dict = oldrestrictioncalls['_resources_consumed_dict']
  emulfile.assert_is_allowed_filename = oldrestrictioncalls['emulfile.assert_is_allowed_filename']
  
# from virtual_namespace import VirtualNamespace
# We need more of the module then just the VirtualNamespace
from virtual_namespace import *
from safe import *
from emulmisc import *
from emulcomm import *
from emulfile import *
from emultimer import *

# Buld the _context and usercontext dicts.
# These will be the functions and variables in the user's namespace (along
# with the builtins allowed by the safe module).
usercontext = {'mycontext':{}}

# Add to the user's namespace wrapped versions of the API functions we make
# available to the untrusted user code.
namespace.wrap_and_insert_api_functions(usercontext)

# Convert the usercontext from a dict to a SafeDict
usercontext = safe.SafeDict(usercontext)

# Allow some introspection by providing a reference to the context
usercontext["_context"] = usercontext
usercontext["getresources"] = nonportable.get_resources
usercontext["createvirtualnamespace"] = virtual_namespace.createvirtualnamespace
usercontext["getlasterror"] = emulmisc.getlasterror
_context = usercontext.copy()

# This is needed because otherwise we're using the old versions of file and
# open.   We should change the names of these functions when we design
# repy 0.2
originalopen = open
originalfile = file
openfile = emulated_open

# file command discontinued in repy V2
#file = emulated_open

# Override by default!
override_restrictions()

