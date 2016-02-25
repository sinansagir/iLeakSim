#!/usr/bin/python

import os, sys, fnmatch
import math

condorDirName = 'condor_2016_2_20_11_15_20'
condorDir = '/home/ssagir/radMonitoring/CMSSW_7_3_0/src/iLeakSim_Feb16_leakCalcV1/'

def finddirs(path, filtre):
    for root, dirs, files in os.walk(path):
        for dir in fnmatch.filter(dirs, filtre):
            yield os.path.join(root, dir)

def findfiles(path, filtre):
    for root, dirs, files in os.walk(path):
        for f in fnmatch.filter(files, filtre):
            yield os.path.join(root, f)

# condordirlist = []
# for condordir in finddirs(condorDir, 'condor_*'):
#     entrynumberlist = []
#     for logfile in findfiles(condordir, '*.log'):
#     	entrynumberlist.append(int(logfile[logfile.find('entry_')+6:logfile.find('.log')]))
#     condordirlist.append((condordir.split('/')[-1],min(entrynumberlist),max(entrynumberlist)))

condordirlist = [[condorDirName, 0, 439]]
njobs = 0
for condor in condordirlist:
	count=0
	condordir = condor[0]
	print condordir
	logFileDir = condorDir+condorDirName
	rootFileDir = condorDir+condorDirName
	for i in range(condor[1],condor[2]+1):
		rFile = rootFileDir+'/entry_'+str(i)+'.root'
		jFile = logFileDir +'/entry_'+str(i)+'.job'
		lFile = logFileDir +'/entry_'+str(i)+'.log'
		eFile = logFileDir +'/entry_'+str(i)+'.err'
		statement1 = os.path.exists(rFile)
		statement2 = True
		if statement1: statement2 = os.path.getsize(rFile)>1000
		if not os.path.exists(eFile): statement3 = False
		if os.path.exists(eFile): 
			errFdata = open(eFile).read()
			statement3 = not ('error' in errFdata or 'Error' in errFdata)
		if not os.path.exists(lFile): statement4 = False
		if os.path.exists(lFile):
			logFdata = open(lFile).read()
			statement4 = ('Normal termination (return value 0)' in logFdata)
		statement = statement1 and statement2 and statement3 and statement4
		if not statement:
			print "*" * 40
			print "ERRORS:"
			if not statement1: print "-Root file does not exist!"
			if not statement2: print "-Root file size < 1000!"
			if not statement3: print "-Error in condor error file!"
			if not statement4: print "-Return value is not 0 in log file!"
			print ">condor_submit " + jFile
			#os.system('rm ' + lFile)
			#os.system('condor_submit ' + jFile)
			print "*" * 40
			count+=1
	njobs+=count
	print count, "jobs resubmitted!!!"
	
print njobs, "jobs resubmitted in total!!!"

