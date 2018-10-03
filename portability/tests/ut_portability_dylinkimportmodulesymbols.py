"""
Demonstrate how dylink overrides variables when importing a library.
"""
from repyportability import *
add_dy_support(locals())

def check_variable_contents(variable, checkstring):
  if variable != checkstring:
    log("Unexpected contents in variable: " + variable +  
        " (expected " + checkstring + ")\n")

dy_import_module_symbols("examplelib.repy")
check_variable_contents(foo, "examplelib.repy's foo")

# Override the variable locally
foo = "local override"
check_variable_contents(foo, "local override")

# Re-import the library. The variable contents should be reset.
dy_import_module_symbols("examplelib.repy")
check_variable_contents(foo, "examplelib.repy's foo")
