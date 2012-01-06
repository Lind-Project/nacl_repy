# this file gets appended on our tests to make them work

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

from lind_fs_constants import *








