dy_import_module_symbols("testchunk_helper")

SERVER_IP = getmyip()
SERVER_PORT = 60606
DATA_RECV = 1024
CHUNK_SIZE_SEND = 2**16
CHUNK_SIZE_RECV = 2**20
DATA_TO_SEND = "HelloWorld" * 1024 * 1024 * 5 # 50MB of data

launch_test()
