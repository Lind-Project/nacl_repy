# this file gets appended on our tests to make them work

from exception_hierarchy import *

from emulmisc import createlock as createlock

from emulfile import emulated_open as openfile 
from emulfile import removefile
from emulfile import listfiles

from  nonportable import get_resources as getresources

from serialize import serializedata as serializedata

import nanny

def do_nothing(*args):
  pass

nanny.tattle_quantity = do_nothing

nanny.tattle_add_item = do_nothing
nanny.tattle_remove_item = do_nothing

nanny._resources_allowed_dict = {'cpu':0, 'messport':set(range(50000,60000)),
      'connport': set(range(50000,60000)), 'memory':0, 'diskused':0,
      'filewrite': 0, 'fileread':0, 'netsend':0, 'netrecv':0,
      'loopsend': 0, 'looprecv':0, 'lograte':0, 'random':0,
      'events':set(), 'filesopened':set(), 'insockets':set(), 'outsockets':set()
      }
nanny._resources_consumed_dict = {'messport':set(), 'connport':set(), 'cpu':0, 
      'memory':0, 'diskused':0,
      'filewrite': 0, 'fileread':0, 'netsend':0, 'netrecv':0,
      'loopsend': 0, 'looprecv':0, 'lograte':0, 'random':0,
      'events':set(), 'filesopened':set(), 'insockets':set(), 'outsockets':set()
      }

from lind_fs_constants import *








