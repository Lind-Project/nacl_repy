#!/usr/bin/env python
"""
<Program Name>
  setup.py

<Started>
  May 4, 2009

<Author>
  Michael Phan-Ba

<Purpose>
  Runs a test server for

"""

import sys
from SimpleXMLRPCServer import SimpleXMLRPCServer


def echo(obj):
  """
  <Purpose>
    Serves as the test function for the XML-RPC client.

  <Arguments>
    obj:
      An object to return to the client.

  <Exceptions>
    None.

  <Side Effects>
    None.

  <Returns>
    The object passed in.

  """
  return obj


def hello_world():
  """
  <Purpose>
    Serves as the no-args test function for the XML-RPC client.

  <Arguments>
    None.

  <Exceptions>
    None.

  <Side Effects>
    None.

  <Returns>
    "Hello World!"

  """
  return "Hello World!"


if __name__ == "__main__":
  server = SimpleXMLRPCServer(("localhost", 8000))
  server.register_function(echo)
  server.register_function(hello_world)
  server.serve_forever()
