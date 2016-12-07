dy_import_module_symbols("udptest_helper")

SHIM_STR = "(MultiPipeShim,(FECShim),(FECShim)(FECShim,3))(NoopShim)"

launch_test(SHIM_STR)
