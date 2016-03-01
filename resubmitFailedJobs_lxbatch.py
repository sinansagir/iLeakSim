#!/usr/bin/python

import os, sys

################# [<condor dir name>, <start job id>, <end job id>] ###########
condordirlist = [['condor_2016_3_1', 0, 439]]
NmodulePerJob = 30
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
		jFile = logFileDir +'/'+str(i)+'/job.sh'
		lFile = logFileDir +'/'+str(i)+'/logs'
		statement1 = os.path.exists(rFile)
		statement2 = True
		if statement1: statement2 = os.path.getsize(rFile)>1000
		if not os.path.exists(lFile): statement3 = False
		if os.path.exists(lFile):
			logFdata = open(lFile).read()
			statement4 = "Job finished" in logFdata
			statement3 = "error" not in logFdata and "Error" not in logFdata
		statement = statement1 and statement2 and statement3 and statement4
		if not statement:
			print "*" * 40
			print "Job File: "+jFile
			print "ERRORS:"
			if not statement1: print "-Root file does not exist!"
			if not statement2: print "-Root file size < 1000!"
			if not statement3: print "-Error in log file!"
			if not statement4: print "-Job finished statement is not in the log file!"
			#os.system('rm ' + lFile)
			#os.chdir(rootFileDir+'/'+str(i))
			#os.system("bsub -q "+queue+" -o logs job.sh")
			print "*" * 40
			count+=1
	njobs+=count
	print count, "jobs resubmitted!!!"
	
print njobs, "jobs resubmitted in total!!!"

