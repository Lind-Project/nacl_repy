if callfunc == "initialize":
  # first, initialize by creating the file we'll read.
  fobj = open("junk_test.out", 'w')
  fobj.write("hello")
  fobj.close()
  
  # now the actual test
  fobj = open("junk_test.out", 'rb')
  fobj.readlines()

  # No exception? Success.
