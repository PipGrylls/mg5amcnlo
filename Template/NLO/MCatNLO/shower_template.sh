#!/bin/bash

SHOWER=$1
#HEP-> hepmc/stdhep
#TOP-> top
OUTPUT=$2
RUN_NAME=$3
NFILE=$4

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:%(extralibs)s

# if one is splitting file cd to a new dir and link all files here
if [[ "$NFILE" != "" ]]; then
    mkdir run_$NFILE
    cd run_$NFILE
    cp -H ../events_$NFILE.lhe events.lhe
    if [ $SHOWER == "PYTHIA8" ] ; then
        cp ../Pythia8.exe ../Pythia8.cmd ../config.sh .
    else
        cp ../MCATNLO_$SHOWER\_EXE ../MCATNLO_$SHOWER\_input .
    fi
fi

if [ -e events.lhe.gz ] ; then
    gunzip $RUN_NAME/events.lhe.gz
fi

if [ "$SHOWER" == "HERWIG6" ] || [ "$SHOWER" == "PYTHIA6Q" ] || [ "$SHOWER" == "PYTHIA6PT" ] || [ "$SHOWER" == "HERWIGPP" ] ; then
    ./MCATNLO_$SHOWER\_EXE < MCATNLO_$SHOWER\_input > mcatnlo_run.log 2>&1

elif [ $SHOWER == "PYTHIA8" ] ; then
    source config.sh
    ./Pythia8.exe Pythia8.cmd > mcatnlo_run.log 2>&1
fi

if [ "$OUTPUT" == "HEP" ] ; then
    # hep or hepmc output
    # this is for the final filename
    if [[ "$NFILE" != "" ]]; then
        NAME="../events_$NFILE"
    else
        NAME="events"
    fi
    # at the end a file called events.hep.gz or events.hepmc.gz will be delivered
    if [ "$SHOWER" == "HERWIG6" ] || [ "$SHOWER" == "PYTHIA6Q" ] || [ "$SHOWER" == "PYTHIA6PT" ] ; then
        mv events.lhe.hep $NAME.hep
        gzip $NAME.hep
    elif [ "$SHOWER" == "HERWIGPP" ] ; then
        mv MCATNLO_HERWIGPP.hepmc $NAME.hepmc
        gzip $NAME.hepmc
    elif [ "$SHOWER" == "PYTHIA8" ] ; then
        mv Pythia8.hep $NAME.hepmc
        gzip $NAME.hepmc
    fi

elif [ "$OUTPUT" == "TOP" ] ; then
    #top output 
    # this is for the final filename
    if [[ "$NFILE" != "" ]]; then
        NAME="../topfile_$NFILE"
    else
        NAME="topfile"
    fi
    # just tar all the topfiles which are found
    tar -cf $NAME.tar *.top *.TOP > tarlog.txt 2>&1
fi

if [[ "$NFILE" != "" ]]; then
    mv mcatnlo_run.log ../mcatnlo_run_$NFILE.log
fi
