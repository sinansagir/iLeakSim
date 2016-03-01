#!/usr/bin/python

import os,datetime

cmsswDir  =os.environ['CMSSW_BASE']+'/src'
scriptDir ='iLeakSim'
scriptName='iLeakSim.py'
queue = "1nd" # give bsub queue -- 8nm (8 minutes), 1nh (1 hour), 8nh, 1nd (1day), 2nd, 1nw (1 week), 2nw 

cTime=datetime.datetime.now()
date='%i_%i_%i'%(cTime.year,cTime.month,cTime.day)
time='%i_%i_%i'%(cTime.hour,cTime.minute,cTime.second)
pfix=''

outDir=cmsswDir+'/'+scriptDir+'/condor_'+pfix+date#+'_'+time
os.mkdir(outDir)

NtotModules = 13196 #Nentries in dPdT.root
NmodulePerJob = 30

countJobs=0
for it in range(0,NtotModules/NmodulePerJob+1):
	#create job directory
	os.system("mkdir "+outDir+"/"+str(it))
	os.chdir(outDir+"/"+str(it))
	outfile='entry_'+str(it)+'.root'
	#create jobs
	with open('job.sh', 'w') as fout:
		fout.write("#!/bin/sh\n\n\n")
		fout.write("echo 'START---------------'\n")
		fout.write("TOP=\"$PWD\"\n")
		fout.write("cd "+cmsswDir+"\n")
		fout.write("eval `scramv1 runtime -sh`\n")
		fout.write("cd $TOP\n")
		fout.write("cp -r "+cmsswDir+"/"+scriptDir+"/* ./\n")
		fout.write("python "+cmsswDir+"/"+scriptDir+"/"+scriptName+" "+str(it)+" "+str(NmodulePerJob)+" "+outfile+"\n")
		fout.write("rfcp *.root "+outDir+"/"+"\n")
		fout.write("echo 'STOP---------------'\n\n")
	os.system("chmod 755 job.sh")
	#submit bjobs
	os.system("bsub -q "+queue+" -o logs job.sh")
	print "job nr " + str(it) + " submitted"
	os.chdir("../..")
	countJobs+=1
			 
print countJobs, "jobs submitted!!!"



