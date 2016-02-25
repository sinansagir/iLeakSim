#!/usr/bin/python

import os,datetime

runDir=os.environ['CMSSW_BASE']+'/src/iLeakSim_master'

cTime=datetime.datetime.now()
date='%i_%i_%i'%(cTime.year,cTime.month,cTime.day)
time='%i_%i_%i'%(cTime.hour,cTime.minute,cTime.second)
pfix=''
#pfix+='_'+time

os.mkdir('condor_'+date+pfix)
outDir=runDir+'/'+'condor_'+date+pfix

NtotModules = 5#13196 #Nentries in dPdT.root
NmodulePerJob = 2#30

countJobs=0
for it in range(0,NtotModules/NmodulePerJob+1): # dpdtentries=11828
	outfile=outDir+'/entry_'+str(it)+'.root'
	dict={'RUNDIR':runDir, 'OUTFILE':outfile, 'ENTRY':it, 'Nmods':NmodulePerJob}
	jdfName=outDir+'/entry_%i.job'%(it)
	jdf=open(jdfName,'w')
	jdf.write(
"""universe = vanilla
Executable = %(RUNDIR)s/makeDarkCurrentSim.sh
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT
Output = entry_%(ENTRY)s.out
Error = entry_%(ENTRY)s.err
Log = entry_%(ENTRY)s.log
Notification = Never
Arguments = %(ENTRY)s %(Nmods)s %(RUNDIR)s %(OUTFILE)s

Queue 1"""%dict)
	jdf.close()
	os.chdir('%s'%(outDir))
	os.system('condor_submit '+jdfName)
	countJobs+=1
			 
print countJobs, "jobs submitted!!!"


