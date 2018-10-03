"""
Demonstrate how dylink overrides variables when importing a library.
"""
from repyportability import *
add_dy_support(locals())

def check_variable_contents(variable, checkstring):
  if variable != checkstring:
    log("Unexpected contents in variable: " + variable +  
        " (expected " + checkstring + ")\n")

examplelib = dy_import_module("examplelib.repy")
check_variable_contents(examplelib.foo, "examplelib.repy's foo")

# Override the variable locally
examplelib.foo = "local override"
check_variable_contents(examplelib.foo, "local override")

# Re-import the library. The override should be intact.
examplelib = dy_import_module("examplelib.repy")
check_variable_contents(examplelib.foo, "local override")
