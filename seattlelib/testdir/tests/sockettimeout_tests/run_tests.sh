#!/bin/bash

trunkdir=$1
logfile=$2

if [ -z "$trunkdir" ] || [ -z "$logfile" ]; then
  echo "Usage: $0 trunkdir logfile (where logfile should be an absolute path, not a relative one)"
  exit 1
fi

# A mktemp command that works on mac/bsd and linux.
tmpdir=`mktemp -d -t tmp.XXXXXXXX` || exit 1

# Change directory to the directory that preparetest.py is in.
cd $trunkdir

# We don't run preparetests.py to actually include tests and then we manually
# copy in the tests we want to run.
python preparetest.py $tmpdir
cp repy/tests/run_tests.py $tmpdir
cp repy/tests/testportfiller.py $tmpdir
cp seattlelib/tests/sockettimeout_tests/z_* $tmpdir
cp seattlelib/tests/sockettimeout_tests/restrictions.default $tmpdir

cd $tmpdir

# Preprocess the repy files.
for i in z_*; do
  python repypp.py $i $i.py
done

python run_tests.py --pattern='z_*.repy.py' >$logfile 2>&1

result=$?

rm -rf $tmpdir

if [ "$result" != "0" ]; then
  echo "run_tests.sh didn't run properly"
  exit 1
fi

# We don't include "exception" because it is in the name of some of the tests
# themselves which end up in the log file.
FAILURE_WORDS="[failed] failure: traceback"

for word in `echo $FAILURE_WORDS`; do
  if [ ! -z "`grep -iF \"$word\" $logfile`" ]; then
    echo "Encountered failure word '$word' in logfile."
    exit 1
  fi
done

SUCCESS_STRING=" tests passed, 0 tests failed"

if [ -z "`grep -F \"$SUCCESS_STRING\" $logfile`" ]; then
  echo "Did not find success string '$SUCCESS_STRING' in logfile."
  exit 1
fi
