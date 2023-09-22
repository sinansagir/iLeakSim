#!/usr/bin/python

import os,sys,fnmatch,math,pickle
import matplotlib.pyplot as plt

runDir=os.getcwd()
simDate = "2016_12_6"

datFits = pickle.load(open(runDir+'/DarkSimAllModules_'+simDate+'/plotLayers_DCU/datFits.p','rb'))
simFits = pickle.load(open(runDir+'/DarkSimAllModules_'+simDate+'/plotLayers_DCU/simFits.p','rb'))

xdata = []
ydatas = {}
ydatad = {}
for prd in range(6):
	ydatas[prd]=[]
	ydatad[prd]=[]
	for i in range(1,5):
		if prd==0: xdata.append(i)
		ydatas[prd].append(simFits['TIB'+str(i)][prd][1])
		ydatad[prd].append(datFits['TIB'+str(i)][prd][1])
	for i in range(1,7):
		if prd==0: xdata.append(i+4)
		ydatas[prd].append(simFits['TOB'+str(i)][prd][1])
		ydatad[prd].append(datFits['TOB'+str(i)][prd][1])


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
ax.set_xlabel("Layer #")
ax.set_ylabel("Leakage Current [$\mu$A fb/cm$^{3}$] @0$^{0}$C")
# ax.set_ylim([-0.001,0.25])
# ax.set_xlim([25,40])
ax.legend(loc=1,prop={'size':16},ncol=1)
fig.savefig(runDir+'/DarkSimAllModules_'+simDate+'/plotLayers_DCU/slopeVSlayer.png')
#plt.show()

fig = plt.figure(44)
ax = fig.add_subplot(111)
ax.set_title("")
ax.plot([1],[0], 'k', label='Measurement')
ax.plot([1],[0], 'k--', label='Simulation')
for lyr in range(1,5):
	datax=[]
	datays=[]
	datayd=[]
	for prd in range(6):
		if prd==2: continue
		datax.append(prd+1)
		datays.append(simFits['TIB'+str(lyr)][prd][1])
		datayd.append(datFits['TIB'+str(lyr)][prd][1])
	ax.plot(datax,datayd, colors[lyr-1], label='TIB_L'+str(lyr))
	ax.plot(datax,datays, colors[lyr-1]+'--')
plt.xticks(datax, [str(lumi[0])+' - '+str(lumi[1]) for lumi in lumiRs if lumi!=lumiRs[2]])
#ax.set_xscale("log", nonposx='clip')
#ax.set_xscale("log", nonposx='clip')
ax.set_xlabel("Fit region [fb$^{-1}$]")
ax.set_ylabel("Leakage Current [$\mu$A fb/cm$^{3}$] @0$^{0}$C")
# ax.set_ylim([-0.001,0.25])
# ax.set_xlim([25,40])
ax.legend(loc=3,prop={'size':12},ncol=3)
fig.savefig(runDir+'/DarkSimAllModules_'+simDate+'/plotLayers_DCU/slopeVSlumiRegion_TIB.png')
#plt.show()	

fig = plt.figure(45)
ax = fig.add_subplot(111)
ax.set_title("")
ax.plot([1],[0], 'k', label='Measurement')
ax.plot([1],[0], 'k--', label='Simulation')
for lyr in range(1,7):
	datax=[]
	datays=[]
	datayd=[]
	for prd in range(6):
		if prd==2: continue
		datax.append(prd+1)
		datays.append(simFits['TOB'+str(lyr)][prd][1])
		datayd.append(datFits['TOB'+str(lyr)][prd][1])
	ax.plot(datax,datayd, colors[lyr-1], label='TOB_L'+str(lyr))
	ax.plot(datax,datays, colors[lyr-1]+'--')
plt.xticks(datax, [str(lumi[0])+' - '+str(lumi[1]) for lumi in lumiRs if lumi!=lumiRs[2]])
#ax.set_xscale("log", nonposx='clip')
#ax.set_xscale("log", nonposx='clip')
ax.set_xlabel("Fit region [fb$^{-1}$]")
ax.set_ylabel("Leakage Current [$\mu$A fb/cm$^{3}$] @0$^{0}$C")
# ax.set_ylim([-0.001,0.25])
# ax.set_xlim([25,40])
ax.legend(loc=3,prop={'size':12},ncol=4)
fig.savefig(runDir+'/DarkSimAllModules_'+simDate+'/plotLayers_DCU/slopeVSlumiRegion_TOB.png')
#plt.show()	
