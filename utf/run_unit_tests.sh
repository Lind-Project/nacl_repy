#!/bin/bash
#
# This helper script for Seattle Testbed, https://seattle.poly.edu/,
# * downloads Seattle Testbed's sources from GitHub,
# * builds them using Seattle's build scripts, and finally
# * runs Seattle's unit tests.
#
# Find documentation for Seattle's build scripts and unit test framework at 
#   https://seattle.poly.edu/wiki/BuildInstructions
#   https://seattle.poly.edu/wiki/UnitTestFramework
#
# The list of components (i.e. source repositories) for which the 
# tests are run is configurable via the REPOLIST variable, see below.
#
# Since other testbeds use the Seattle codebase, we make the testbed 
# name (and thus repo address) configurable too:

TESTBED=SeattleTestbed

# If you like to test the complete set of repos, get the list of 
# $TESTBED repositories via the GitHub API, grab entries like
#    "full_name": "SeattleTestbed/foo",
# cut out the repo names, and create a space-separated list:
#
# REPOLIST=`curl https://api.github.com/orgs/$TESTBED/repos | awk '/full_name/ {gsub("\"", ""); gsub(",", ""); split($2, a, "/"); printf a[2] " "}'`


# Otherwise, just supply the list yourself.
#
# Here's a mostly complete one, omitting but a few backup/outdated repos:
# REPOLIST="advertiseserver affix buildscripts common demokit experimentmanager geoip_server nodemanager overlord portability repy_v1 repy_v2 seash seattlelib_v1 seattlelib_v2 softwareupdater timeserver utf zenodotus"

# This is the "bare minimum" list. Whatever changes you make to the 
# Seattle codebase, do make sure these tests pass (in addition to the 
# repo you changed, of course!)
REPOLIST="common nodemanager repy_v2 seattlelib_v2 seash softwareupdater utf"

echo Running tests for this list of $TESTBED\'s repositories: $REPOLIST

# We will also measure the time elapsed for all tests
TEST_SUITE_STARTED_AT=`date +%s`

# For every repo name, ...
for REPO in $REPOLIST ;
  do echo Testing $TESTBED/$REPO now...

  # Remember in which directory we started
  pushd .

  # Clone the repo
  git clone https://github.com/$TESTBED/$REPO.git

  # If $REPO has a "tests" subdir, then prepare the 
  # test files and run the tests
  if [ -d $REPO/tests ] ; then 
    # Measure the time for this single repo's tests
    REPO_TEST_STARTED_AT=`date +%s`
    cd $REPO/scripts
    python initialize.py
    python build.py -t
    cd ../RUNNABLE
    python utf.py -a
    echo Tests for $TESTBED/$REPO took $(expr `date +%s` - $REPO_TEST_STARTED_AT) seconds, excluding download and build
  else
    echo $TESTBED/$REPO has no "tests" directory. Skipping.
  fi
  popd
done

echo Done running tests for $TESTBED, which took me $(expr `date +%s` - $TEST_SUITE_STARTED_AT) seconds overall.
