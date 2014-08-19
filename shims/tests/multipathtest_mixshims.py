dy_import_module_symbols("multipathtest_helper")
SERVER_IP = getmyip()
SERVER_PORT_NODEA = 36829
SERVER_PORT_NODEB = 35349

MSG_TO_SEND = "HelloWorld" * 1024 * 1024 # 10MB of Data
DATA_RECV_BYTES = 2**16

SHIM_STR = "(MultiPathShim,(CompressionShim,8192),(CompressionShim,512),(NoopShim))(StatShim)(LogShim)"

launch_test(SHIM_STR)
