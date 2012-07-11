#!/bin/bash
set -o xtrace
cd mnt
path=`pwd`/$$
trap 'fusermount -u $path' INT TERM EXIT
mkdir $$
python ../lind_fuse.py $$ -f &
sleep 1

cd $$

echo "Hi there" > ./test_file

cat ./test_file

cd ..
fusermount -u $path
wait
