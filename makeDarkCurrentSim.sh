#!/bin/sh

entry=${1}
nmods=${2}
runDir=${3}
outfile=${4}

source /cvmfs/cms.cern.ch/cmsset_default.sh

cd $runDir
eval `scramv1 runtime -sh`

python iLeakSim.py ${entry} ${nmods} ${outfile}
