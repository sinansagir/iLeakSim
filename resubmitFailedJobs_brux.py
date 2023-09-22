#!/usr/bin/python

import os, sys, fnmatch
import math

################# [<condor dir name>, <start job id>, <end job id>] ###########
condordirlist = [['condor_2023_9_12', 0, 439]]
condorDir = os.getcwd()+'/'

njobs = 0
for condor in condordirlist:
	count=0
	condorDirName = condor[0]
	print condorDirName
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

