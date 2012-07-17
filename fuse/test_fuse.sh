#!/bin/bash
set -o xtrace

# Do some basic tests on a Lind-fuse file system

mkdir -p mnt
cd mnt
path=`pwd`/$$

# if something goes wrong, unmount
trap 'fusermount -u $path' INT TERM EXIT

mkdir $$

python ../lind_fuse.py $$ -f &

sleep 1

cd $$

echo "Small test"
echo "Hi there" > ./test_file

cat ./test_file

echo "Big test"
cp -r /var/log .
ls -R

echo "Data test"
mkdir data
cd data
# random file
dd if=/dev/zero of=/tmp/random.bits bs=1M count=10
cp /tmp/random.bits .

ls
md5sum /tmp/random.bits
md5sum ./random.bits
diff /tmp/random.bits ./random.bits
cd $path


cd ..
fusermount -u $path
wait
