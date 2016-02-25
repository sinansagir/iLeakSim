#!/bin/sh

entry=${1}
nmods=${2}
runDir=${3}
outfile=${4}

source /cvmfs/cms.cern.ch/cmsset_default.sh

cd $runDir
eval `scramv1 runtime -sh`

# cp /home/ssagir/radMonitoring/CMSSW_7_3_0/src/Summary_RadMon_WT_newFLUKA/InputData/FluenceMatching.root .
# cp /home/ssagir/radMonitoring/CMSSW_7_3_0/src/Summary_RadMon_WT_July2015/InputData/LumiPerDay_TOB.txt .
# cp /home/ssagir/radMonitoring/CMSSW_7_3_0/src/Summary_RadMon_WT_July2015/InputData/LumiPerDay_TIB.txt .
# cp /home/ssagir/radMonitoring/CMSSW_7_3_0/src/Summary_RadMon_WT_July2015/InputData/LumiPerDay_TECn.txt .
# cp /home/ssagir/radMonitoring/CMSSW_7_3_0/src/Summary_RadMon_WT_July2015/InputData/LumiPerDay_TECp.txt .
# cp /home/ssagir/radMonitoring/CMSSW_7_3_0/src/Summary_RadMon_WT_newFLUKA/InputData/TempTree0_190311.root TempTree0.root
# #cp /home/ssagir/radMonitoring/CMSSW_7_3_0/src/Summary_RadMon_WT_newFLUKA/InputData/dpdt_Jul22.root .
# cp /home/ssagir/radMonitoring/CMSSW_7_3_0/src/Summary_RadMon_WT_newFLUKA/InputData/dPdTfromErik.root .
# cp /home/ssagir/radMonitoring/CMSSW_7_3_0/src/Summary_RadMon_WT_newFLUKA/InputData/IleakTree0_190311.root IleakTree0.root

python iLeakSim.py ${entry} ${nmods} ${outfile}
