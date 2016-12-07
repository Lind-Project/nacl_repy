Introduction:
--------------
The shim_files folder contains all the shim files that are necessary.
You can create shims by inheriting from BaseShim and using ShimStack.
This file contains an example of what a simple should be like. It 
includes the shim HelloWorldShim in helloworldshim.repy and
HelloWorldDeciderShim in helloworlddecidershim.repy. The HelloWorldShim
basically appends the tag 'HelloWorldSendTAG:::some_num@' when it does
a socket.send() on any tcp connection and appends the tag 
'HelloWorldRecvTAG:::some_num' when it does a socket.recv() on any tcp
connection.

The HelloWorldDeciderShim appends an extra layer of HelloWorldShim at 
the top of its stack. This displays how a decider shim can be used to
push new shims on top of its stack. You can similarly pop() shims from
the top of its stack.

The application sample_helloworld_shim_app.repy is an example of how you
can write an application that uses shims. It uses both the 
HelloWorldDeciderShim and HelloWorldShim. To run it please execute the
command:

  $> python repy.py restrictions.default dylink.repy sample_helloworld_shim_app.repy




Setup:
-------
In order to run the sample application 'sample_helloworld_shim_app.repy'
in this directory: 

1. Create a new folder
2. Run preparetest.py in the new folder to copy over all the repyV2
   library files.
3. Copy all the files in this directory in the new folder.
4. You are now ready to run sample_helloworld_shim_app.repy !


Files Included:
---------------
1. baseshim.repy
2. helloworlddecidershim.repy
3. helloworldshim.repy
4. restrictions.default
5. sample_helloworld_shim_app.repy
6. shim_exceptions.repy
7. shimstackinterface.repy
8. shim_stack.repy
9. shim_wrapper_lib.repy
10. This README file. 
