import lind_fs_calls

from lind_fs_constants import *

# Let's add a few files, etc. to the system and see if it works...
lind_fs_calls._blank_fs_init()

myfd = lind_fs_calls.open_syscall('/foo',O_CREAT | O_EXCL | O_WRONLY,S_IRWXA)

# write should succeed
assert(lind_fs_calls.write_syscall(myfd,'hi') == 2)

stat_result = lind_fs_calls.stat_syscall('/foo')

# ensure the file has size 2
assert(stat_result[7] == 2)

# ensure the link count is 1
assert(stat_result[3] == 1)

             
# create a file with no perms...
lind_fs_calls.link_syscall('/foo','/foo2')

stat_result = lind_fs_calls.stat_syscall('/foo')
stat_result2 = lind_fs_calls.stat_syscall('/foo2')

# ensure they are the same now...
assert(stat_result2 == stat_result)

# and that the link count is 2
assert(stat_result[3] == 2)


# let's unlink one now...

lind_fs_calls.unlink_syscall('/foo')


stat_result = lind_fs_calls.stat_syscall('/foo2')

# ensure the link count is 1
assert(stat_result[3] == 1)

# file is gone...
try:
  stat_result = lind_fs_calls.stat_syscall('/foo')
except:
  pass
else:
  print "stat worked after unlinked!!!"


lind_fs_calls.unlink_syscall('/foo2')
