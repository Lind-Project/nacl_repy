dy_import_module_symbols("testratelimit_helper")


UPLOAD_RATE = 1024 * 56 # 100KB/s
DOWNLOAD_RATE = 1024 * 56 # 100KB/s
DATA_TO_SEND = "HelloWorld" * 1024 * 128


launch_test()
