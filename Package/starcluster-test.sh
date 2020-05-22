#!/bin/bash

#-------------------------------------------------------------------------------

# -- set -o nounset
# -- set -o verbose
# -- set -o xtrace

#--------------------------------------------------------------------------------

export STARCLUSTER_CONFIG=./config/test-ngscloud-config.txt

#-------------------------------------------------------------------------------

function end
{

    exit 0

}

#-------------------------------------------------------------------------------

function manage_error
{

    if [ $1 == '2' ]; then
        echo "*** ERROR: StarCluster has ended with return code $2."
        exit 1
    fi

}

#--------------------------------------------------------------------------------

if [ $1 == 'sshmaster' ] && [ -n "$3" ]; then
    starcluster $1 $2 "$3"
    RC=$?; [ $RC -ne 0 ] && manage_error 1 $RC
elif [ $1 == 'sshnode' ] && [ -n "$4" ]; then
    starcluster $1 $2 $3 "$4"
    RC=$?; [ $RC -ne 0 ] && manage_error 1 $RC
else
    starcluster $*
    RC=$?; [ $RC -ne 0 ] && manage_error 1 $RC
fi

end

#-------------------------------------------------------------------------------
