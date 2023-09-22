#!/usr/bin/python

import os,sys,fnmatch,math,pickle
import matplotlib.pyplot as plt

runDir=os.getcwd()
simDate = "2016_12_6"

datFits = pickle.load(open(runDir+'/DarkSimAllModules_'+simDate+'/plotRings_DCU/datFits.p','rb'))
simFits = pickle.load(open(runDir+'/DarkSimAllModules_'+simDate+'/plotRings_DCU/simFits.p','rb'))

xdata = []
ydatas = {}
ydatad = {}
for prd in range(6):
	ydatas[prd]=[]
	ydatad[prd]=[]
	for i in range(1,4):
		if prd==0: xdata.append(i)
		ydatas[prd].append(simFits['TID'+str(i)][prd][1])
		ydatad[prd].append(datFits['TID'+str(i)][prd][1])
	for i in range(1,8):
		if prd==0: xdata.append(i+3)
		ydatas[prd].append(simFits['TEC'+str(i)][prd][1])
		ydatad[prd].append(datFits['TEC'+str(i)][prd][1])


fig = plt.figure(0)
ax = fig.add_subplot(111)
ax.set_title("")
ax.plot([1],[0], 'k', label='Measurement')
ax.plot([1],[0], 'k--', label='Simulation')
colors=['k','b','y','r','g','c','m','k','b','r']
lumiRs = [[0,5.8],[6.1,21],[30.2,34],[35,50],[53,67],[69,75]]
for prd in range(0,6):
	if prd==2: continue
	ax.plot(xdata,ydatad[prd], colors[prd], label='Lumi: '+str(lumiRs[prd][0])+' - '+str(lumiRs[prd][1])+' fb$^{-1}$')
	ax.plot(xdata,ydatas[prd], colors[prd]+'--')
#ax.set_xscale("log", nonposx='clip')
ax.set_xlabel("Ring #")
ax.set_ylabel("Leakage Current [$\mu$A fb/cm$^{3}$] @0$^{0}$C")
# ax.set_ylim([-0.001,0.25])
# ax.set_xlim([25,40])
ax.legend(loc=1,prop={'size':16},ncol=1)
fig.savefig(runDir+'/DarkSimAllModules_'+simDate+'/plotRings_DCU/slopeVSring.png')
#plt.show()

fig = plt.figure(44)
ax = fig.add_subplot(111)
ax.set_title("")
ax.plot([1],[0], 'k', label='Measurement')
ax.plot([1],[0], 'k--', label='Simulation')
for lyr in range(1,4):
	datax=[]
	datays=[]
	datayd=[]
	for prd in range(6):
		if prd==2: continue
		datax.append(prd+1)
		datays.append(simFits['TID'+str(lyr)][prd][1])
		datayd.append(datFits['TID'+str(lyr)][prd][1])
	ax.plot(datax,datayd, colors[lyr-1], label='TID_R'+str(lyr))
	ax.plot(datax,datays, colors[lyr-1]+'--')
plt.xticks(datax, [str(lumi[0])+' - '+str(lumi[1]) for lumi in lumiRs if lumi!=lumiRs[2]])
#ax.set_xscale("log", nonposx='clip')
#ax.set_xscale("log", nonposx='clip')
ax.set_xlabel("Fit region [fb$^{-1}$]")
ax.set_ylabel("Leakage Current [$\mu$A fb/cm$^{3}$] @0$^{0}$C")
# ax.set_ylim([-0.001,0.25])
# ax.set_xlim([25,40])
ax.legend(loc=3,prop={'size':12},ncol=3)
fig.savefig(runDir+'/DarkSimAllModules_'+simDate+'/plotRings_DCU/slopeVSlumiRegion_TID.png')
#plt.show()	

fig = plt.figure(45)
ax = fig.add_subplot(111)
ax.set_title("")
ax.plot([1],[0], 'k', label='Measurement')
ax.plot([1],[0], 'k--', label='Simulation')
for lyr in range(1,8):
	datax=[]
	datays=[]
	datayd=[]
	for prd in range(6):
		if prd==2: continue
		datax.append(prd+1)
		datays.append(simFits['TEC'+str(lyr)][prd][1])
		datayd.append(datFits['TEC'+str(lyr)][prd][1])
	ax.plot(datax,datayd, colors[lyr-1], label='TEC_R'+str(lyr))
	ax.plot(datax,datays, colors[lyr-1]+'--')
plt.xticks(datax, [str(lumi[0])+' - '+str(lumi[1]) for lumi in lumiRs if lumi!=lumiRs[2]])
#ax.set_xscale("log", nonposx='clip')
#ax.set_xscale("log", nonposx='clip')
ax.set_xlabel("Fit region [fb$^{-1}$]")
ax.set_ylabel("Leakage Current [$\mu$A fb/cm$^{3}$] @0$^{0}$C")
# ax.set_ylim([-0.001,0.25])
# ax.set_xlim([25,40])
ax.legend(loc=2,prop={'size':12},ncol=4)
fig.savefig(runDir+'/DarkSimAllModules_'+simDate+'/plotRings_DCU/slopeVSlumiRegion_TEC.png')
#plt.show()	
