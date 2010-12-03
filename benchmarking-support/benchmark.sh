#!/bin/bash
# Used to automate benchmarking

# Number of iterations per test
NUM_ITERS="10000"

# The number of layers
#NUM_LAYERS="1 2 5 10 20 50 100"
NUM_LAYERS="1"
#NUM_LAYERS="2"

# The types of tests
TESTS="noarg immutarg mutarg excp"

# Command to run for seclayer
SEC_CMD="python repy.py restrictions.full encasementlib.repy"
NORM_CMD="python repy.py restrictions.full"

echo "Doing $NUM_ITERS iterations per test."

# CPU benchmarks
for TEST in $TESTS
do
    echo
    echo "####"
    echo "$TEST test"
    echo "####"
    for LAYER in $NUM_LAYERS
    do
       echo 
       echo "Layers: $LAYER"
       $SEC_CMD $TEST-seclayer-init.repy $LAYER $TEST-timediter.py $NUM_ITERS 
       $NORM_CMD $TEST-handop.repy $LAYER $NUM_ITERS 
       $NORM_CMD $TEST-nocheck.repy $LAYER $NUM_ITERS 
    done
done

echo
echo "####"
echo "Memory test"
echo "####"
TEST="noarg"
for LAYER in $NUM_LAYERS
do
   echo 
   echo "Layers: $LAYER"
   $SEC_CMD $TEST-seclayer-init.repy $LAYER $TEST-seclayer-memory.repy
   $NORM_CMD $TEST-nocheck-memory.repy $LAYER
done

