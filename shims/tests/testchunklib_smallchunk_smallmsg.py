dy_import_module_symbols("testchunk_helper")

SERVER_IP = getmyip()
SERVER_PORT = 60606
DATA_RECV = 1024
CHUNK_SIZE_SEND = 2**9 # 512KB chunk size
CHUNK_SIZE_RECV = 2**9
DATA_TO_SEND = "Hello" # 5Bytes of data

launch_test()
