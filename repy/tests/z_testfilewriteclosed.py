if callfunc == "initialize":
  # first, initialize by creating the file we'll read.
  fobj = open("junk_test.out", 'w')
  fobj.write("hello")
  fobj.close()
  
  # Test that write() on read-only files throws ValueError
  fobj = open("junk_test.out", 'r')
  try:
    fobj.write("a")
  except ValueError:
    pass
  else:
    print "This shouldn't happen!"
  finally:
    fobj.close()

  # Test that write() on closed files throws ValueError
  fobj = open("junk_test.out", 'w')
  fobj.close()

  try:
    fobj.write("a")
  except ValueError:
    pass
  else:
    print "This shouldn't happen!"
