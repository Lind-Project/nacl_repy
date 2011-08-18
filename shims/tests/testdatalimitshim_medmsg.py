dy_import_module_symbols("testdatalimit_helper")

# Send 10MB of data through with a high limit of 3MB. Which means as soon as it sends
# 3MB, the shim should block until the time limit (in this case 20 seconds) is up. 
UPLOAD_LIMIT = 1024 * 1024 * 3 # 3MB
DOWNLOAD_LIMIT = 1024 * 1024 * 3 # 3MB
TIME_LIMIT = 10
DATA_TO_SEND = "HelloWorld" * 1024 * 1024


launch_test()
