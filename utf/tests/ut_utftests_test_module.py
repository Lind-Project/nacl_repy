import subprocess

sub = subprocess.Popen(['python', 'utf.py', '-m', 'stagedtest'], 
                                         stderr=subprocess.PIPE, 
                                         stdout=subprocess.PIPE)

(out, err) = sub.communicate()

#should cause test to fail if there's anything on stderr
if err != '':
  print "FAIL: test produced on standard out"
if not "Testing module: stagedtest" in out:
  print "FAIL: module test output incorrect"
if not "Running: ut_stagedtest_falsetestone.py" in out:
  print "FAIL: ut_stagedtest_falsetestone.py did not show up in test list"
if not "Running: ut_stagedtest_falsetesttwo.py" in out:
  print "FAIL: ut_stagedtest_falsetesttwo.py did not show up in test list"