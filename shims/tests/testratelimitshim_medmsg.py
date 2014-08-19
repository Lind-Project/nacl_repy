dy_import_module_symbols("testratelimit_helper")


UPLOAD_RATE = 1024 * 512 # 512KB/s
DOWNLOAD_RATE = 1024 * 512 # 512KB/s
DATA_TO_SEND = "HelloWorld" * 1024 * 1024


launch_test()
