#!/usr/bin/python

import os,datetime

cmsswDir=os.environ['CMSSW_BASE']+'/src'
scriptDir ='iLeakSim'
scriptName='iLeakSim.py'
queue = "1nh"

cTime=datetime.datetime.now()
date='%i_%i_%i'%(cTime.year,cTime.month,cTime.day)
time='%i_%i_%i'%(cTime.hour,cTime.minute,cTime.second)
pfix=''

os.mkdir('condor_'+date+pfix)
outDir=cmsswDir+'/'+scriptDir+'/condor_'+pfix+date#+'_'+time

NtotModules = 5#13196 #Nentries in dPdT.root
NmodulePerJob = 1#30

countJobs=0
for it in range(0,NtotModules/NmodulePerJob+1):
	##### creates directory and file list for job #######
	os.system("mkdir "+outDir+"/"+str(it))
	os.chdir(outDir+"/"+str(it))
	outfile='entry_'+str(it)+'.root'
	##### creates jobs #######
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
		fout.write("echo 'STOP---------------'\n")
		fout.write("echo\n")
		fout.write("echo\n")
	os.system("chmod 755 job.sh")
	###### sends bjobs ######
	os.system("bsub -q "+queue+" -o logs job.sh")
	print "job nr " + str(it) + " submitted"
	os.chdir("../..")
	countJobs+=1
			 
print countJobs, "jobs submitted!!!"



