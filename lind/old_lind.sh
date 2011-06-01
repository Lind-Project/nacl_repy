#!/bin/bash
# Launch the Lind Launcher with enviroment setup
# Chris Matthews cmatthew@cs.uvic.ca
# Thu May  5 12:13:17 PDT 2011
#
function print_debug {
   echo "[Lind] $1"
}

function problem {
   echo "[Lind] $1"
   exit 1
}

print_debug "Warning: Running Lind!"

#base of the NaCl Build to use
nacl_base=/home/cmatthew/lind/native_client

if [ ! -e ${nacl_base} ]; then
    problem "Could not find NaCl base: ${nacl_base}"
fi

# nacl_imc.so file location
#todo this is a bad name
nacl_bin=${nacl_base}/scons-out/dbg-linux-x86-64/staging

if [ ! -e "${nacl_bin}"  ]; then
    problem "Could not find nacl bin folder folder. Is nacl built correclty?: ${nacl_bin}"
fi

if [ ! -e "${nacl_bin}/naclimc.so" ]; then
    problem "Could not find naclimc . Is nacl built correclty?: ${nacl_bin}"
fi

if [ ! -e "${nacl_bin}/sel_ldr" ]; then
    problem "Could not find sel_ldr. Is nacl built correclty?: ${nacl_bin}"
fi


# set the python path
export PYTHONPATH=$nacl_bin


#the lind python location
lind=./lind_launcher.py

# NaCl loader location
export NACL_SEL_LDR=${nacl_bin}/sel_ldr

# Where should nacl get its runtime libs from
export NACL_DYN_LOADER=${nacl_base}/tools/modular-build/out/install/glibc_64/nacl64/lib/runnable-ld.so
export NACL_LIBRARY_DIR=${nacl_base}/tools/modular-build/out/install/full-gcc-glibc/nacl64/lib64/:${nacl_base}/tools/modular-build/out/install/glibc_64/nacl64/lib/:${nacl_base}/tools/modular-build/out/install/nacl_libs_glibc_64/nacl64/lib/

if [ ! -e ${nacl_base}/tools/modular-build/out/install/glibc_64/nacl64/lib/runnable-ld.so ]; then
    problem "Could not find NaCl's runnable-ld.so: ${nacl_base}/tools/modular-build/out/install/glibc_64/nacl64/lib/runnable-ld.so"
fi


export REPY_PATH=~/tmp/repy/



#check file to run, if not found run hello world. 
#if no program is given, run hello world
default_nacl_file=${nacl_base}/scons-out/nacl-x86-64-glibc/staging/hello_world.nexe

nacl_file=$default_nacl_file
if [ -e "$1" ]; then
    nacl_file=$1
fi

if [ ! -f ${nacl_file} ]; then
    problem "I can't find ${nacl_file}, aborting."
fi

#Now print env and run
print_debug ======================Setup=====================================
print_debug [PYTHONPATH]=$PYTHONPATH
print_debug [NACL_SEL_LDR]=$NACL_SEL_LDR
print_debug [NACL_LIBRARY_DIR]=$NACL_LIBRARY_DIR
print_debug Running: python $lind $nacl_file
print_debug =======================Execute==================================
python $lind $nacl_file
print_debug =======================Finished=================================
print_debug Done.

