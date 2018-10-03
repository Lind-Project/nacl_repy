""" 
Author: Justin Cappos

Module: Node Manager resource math.   Helper routines to figure out how to add
        two vessels together and divide a vessel into two others.

Start date: September 5th 2008

The design goals of this version are to be secure, simple, and reliable (in 
that order).   

This is where we worry about the offcut resources...
"""

# What we throw when getting an invalid resource / restriction file
class ResourceParseError(Exception):
  pass




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







