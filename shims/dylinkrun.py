#!/usr/bin/python

"""
Run a repy program in dylink mode.

Arguments: [repy file name] [argument1] [argument2] ...

"""

import sys
import dylink_portability


def main():
  try:
    filename = sys.argv[1]
    argslist = sys.argv[2:]
  except KeyError:
    print "Arguments: [repy file name] [argument1] [argument2] ..."
    return

  dylink_portability.run_unrestricted_repy_code(filename, argslist)



if __name__ == '__main__':
  main()
