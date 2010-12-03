#pragma out Now starting subprocess

import subprocess

process = subprocess.Popen(['python', 'utf.py', '-m', 'stagedtestsetup'], 
                           stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE)
(out, err) = process.communicate()

if out:
  print out
if err:
  print err
