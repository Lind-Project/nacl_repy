""" 
Author: Justin Cappos

Module: Node Manager resource math.   Helper routines to figure out how to add
        two vessels together and divide a vessel into two others.

Start date: September 5th 2008

The design goals of this version are to be secure, simple, and reliable (in 
that order).   

This is where we worry about the offcut resources...
"""


# need to know what resources are supported
from nanny import known_resources
# need to know what resources are supported
from nanny import individual_item_resources
# need to know what resources are required - Brent
from nanny import must_assign_resources

# NOTE: Should I move all of this into nanny and restrictions?   Should I 
# have restrictions and nanny call this instead?  
# Duplication is bad, but I'm not sure how best to refactor.
from restrictions import get_rule
from restrictions import known_calls
from restrictions import valid_actions

# What we throw when getting an invalid resource / restriction file
class ResourceParseError(Exception):
  pass



# reads a restrictions file (tossing the non-resource lines and returning a 
# dict of the resources)
def read_resources_from_file(filename):

  retdict = {}
  for individual_item_resource in individual_item_resources:
    retdict[individual_item_resource] = set()

  # much of this is adopted from restrictions.py.   If you find bugs here, 
  # check there as well
  for line in open(filename):
    # remove any comments
    noncommentline = line.split('#')[0]

    tokenlist = noncommentline.split()
   
    if len(tokenlist) == 0:
      # This was a blank or comment line
      continue

    # should be either a resource or a call line
    if tokenlist[0] != 'resource' and tokenlist[0] != 'call':
      raise ResourceParseError, "Line '"+line+"' not understood in file '"+filename+"'"

    # don't care about calls for this.
    if tokenlist[0] == 'call':
      continue

    ####### Okay, it's a resource.  It must have two other tokens!
    if len(tokenlist) != 3:
      raise ResourceParseError, "Line '"+line+"' has wrong number of items in '"+filename+"'"
    # and the second token must be a known resource
    if tokenlist[1] not in known_resources:
      raise ResourceParseError, "Line '"+line+"' has an unknown resource '"+tokenlist[1]+"' in '"+filename+"'"


    # and the last item should be a valid float
    try:
      float(tokenlist[2])
    except ValueError:
      raise ResourceParseError, "Line '"+line+"' has an invalid resource value '"+tokenlist[2]+"' in '"+filename+"'"

    # let's handle individual resources now...
    if tokenlist[1] in individual_item_resources:
      retdict[tokenlist[1]].add(float(tokenlist[2]))
      continue


    # non individual resources should not have been previously assigned
    if tokenlist[1] in retdict:
      raise ResourceParseError, "Line '"+line+"' has a duplicate resource rule for '"+tokenlist[1]+"' in '"+filename+"'"

    # Finally, we assign it to the dictionary
    retdict[tokenlist[1]] = float(tokenlist[2])

  return retdict




# reads a restrictions file (tossing the resource lines and returning a 
# string with all of the restrictions data)
def read_restrictionsstring_from_data(restrictionsdata):

  retstring = ''


  for line in restrictionsdata.split('\n'):
    # remove any comments
    noncommentline = line.split('#')[0]

    tokenlist = noncommentline.split()
   
#    if len(tokenlist) == 0:
#      # This was a blank or comment line
#      continue

    # append call lines
    if len(tokenlist) == 0 or tokenlist[0] != 'resource':
      retstring = retstring + line+'\n'
 
    #Ignore resource lines, etc.

  return retstring





def write_resource_dict(resourcedict, filename):
  outfo = open(filename,"w")
  for resource in resourcedict:
    if type(resourcedict[resource]) == set:
      for item in resourcedict[resource]:
        print >> outfo, "resource "+resource+" "+str(item)
    else:
      print >> outfo, "resource "+resource+" "+str(resourcedict[resource])

  outfo.close()


def check_for_negative_resources(newdict):
  for resource in newdict:
    if type(newdict[resource]) != set and newdict[resource] < 0.0:
      raise ResourceParseError, "Insufficient quantity: Resource '"+resource+"' has a negative quantity"


# Helper method to ensure that the given resource dict has all of the resources
# listed as required in nanny.py. -Brent
def check_for_required_resources(newdict):
  for resource in must_assign_resources:
    if resource not in newdict:
      raise ResourceParseError("Missing required resource: '"+resource+"'")
  

def add(dict1, dict2):
  retdict = dict1.copy()

  # then look at resourcefile1
  for resource in dict2:

    # if this is a set, then get the union
    if type(retdict[resource]) == set:
      retdict[resource] = retdict[resource].union(dict2[resource])
      continue

    # empty if not preexisting
    if resource not in retdict:
      retdict[resource] = 0.0

    # ... and add this item to what we have
    retdict[resource] = retdict[resource] + dict2[resource]

  return retdict



def subtract(dict1, dict2):
  retdict = dict1.copy()

  # then look at resourcefile1
  for resource in dict2:

    # empty if not preexisting
    if resource not in retdict:
      retdict[resource] = 0.0

    # ... and add this item to what we have
    retdict[resource] = retdict[resource] - dict2[resource]

  return retdict




# add vessels together
def combine(resourcefilename1, resourcefilename2, offcutfilename, newfilename):

  # first, read in the files.  
  offcutresourcedict = read_resources_from_file(offcutfilename)
  resourcefile1dict = read_resources_from_file(resourcefilename1)
  resourcefile2dict = read_resources_from_file(resourcefilename2)

  # combin2 the vessels
  tempdict = add(resourcefile1dict, resourcefile2dict)
  # add in the offcut resources
  newdict = add(offcutresourcedict, tempdict)

  # ensure there aren't negative resources here (how could there be?)
  check_for_negative_resources(newdict)
  
  # ensure the required resource limits are included. 
  # (how could this not be?) -Brent
  check_for_required_resources(newdict)

  # okay, now write out the new file...
  write_resource_dict(newdict, newfilename)


# split a vessel
def split(resourcefilename1, resourcefilename2, offcutfilename, newfilename):

  # first, read in the files.  
  offcutresourcedict = read_resources_from_file(offcutfilename)
  resourcefile1dict = read_resources_from_file(resourcefilename1)
  resourcefile2dict = read_resources_from_file(resourcefilename2)

  check_for_negative_resources(resourcefile1dict)
  check_for_negative_resources(resourcefile2dict)
  
  # Check to ensure that both resource files have values for all the
  # required resources.  Without this check, the node manager runs into
  # errors when trying to enforce the limits on the required resources
  # -Brent
  check_for_required_resources(resourcefile1dict)
  check_for_required_resources(resourcefile2dict)

  # subtract the vessels
  tempdict = subtract(resourcefile1dict, resourcefile2dict)
  # add in the offcut resources
  newdict = subtract(tempdict, offcutresourcedict)

  # ensure there aren't negative resources
  check_for_negative_resources(newdict)
  
  # Ensure that all the required resource limits are included -Brent
  check_for_required_resources(newdict)

  # okay, now write out the new file...
  write_resource_dict(newdict, newfilename)


