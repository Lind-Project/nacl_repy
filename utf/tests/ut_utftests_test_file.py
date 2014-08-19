import subprocess

sub = subprocess.Popen(['python', 'utf.py', '-f', 'ut_stagedtest_falsetestone.py'], 
                                         stderr=subprocess.PIPE, 
                                         stdout=subprocess.PIPE)
(out, err) = sub.communicate()

#should cause test to fail if there's anything on stderr
if err != '':
  print "FAIL: test produced on standard out"
  
if not "Running: ut_stagedtest_falsetestone.py" in out:
  print "FAIL: ut_stagedtest_falsetestone.py did not show up in test list"