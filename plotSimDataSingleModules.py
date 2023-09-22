#!/usr/bin/python

from bisect import bisect_left
import os,sys,math,fnmatch,pickle
from array import array
import numpy as np
from ROOT import *
gROOT.SetBatch(1)

##################################################################################################################
# The code looks for the input simulation tree in "DarkSimAllModules_<simDate>/DarkSimAllModules_<simDate>.root"
# The output files will be in "DarkSimAllModules_<simDate>/approvalPlots/". 
##################################################################################################################

#******************************Input to edit******************************************************
measDataPath = "MeasDataLocal/data_DCU_raw"
simDate = "2023_9_12"
readTree=True # This needs to be true if running the code on the tree for the first time. It will dump what's read from tree into pickle files and these can be loaded if this option is set to "False"
isCurrentScaled = False # Scale current to measured temperature (Check how this is done!!!! The default method assumes that the simulated current is at 20C)
plotRawData = False
drawTempData = True

def findfiles(path, filtre):
    for root, dirs, files in os.walk(path):
        for f in fnmatch.filter(files, filtre):
            yield os.path.join(root, f)

QuerrMods = []
for file in findfiles(measDataPath+'/iLeak_perDay/', '*.txt'):
    QuerrMods.append(int(file.split('/')[-1][:-4]))
#QuerrMods=[369120486,436262468]

# Read Input Data for Lumi and Trackerstates of TOB
TempinTOB = "InputDataLocal/LumiPerDay_TOB.txt"
infileTOB = open(TempinTOB, 'r')
print "Reading TOB Lumi File"
linesTOB = infileTOB.readlines()
infileTOB.close()
Tstate = {}
for line in linesTOB:
	data = line.strip().split()
	try: 
		states_ = [float(data[3]), float(data[4]), float(data[5]), float(data[6])]# ON, OFF, STAND-BY, SHUT-DOWN
		Tstate[TDatime(int(data[1])).GetDate()] = max(xrange(len(states_)), key = lambda x: states_[x])
	except: print "Warning! => Unknown data format: ",data,"in",TempinTOB

print "Reading DCU LS1 data"
dcu_ls1 = {}
for file in findfiles('MeasDataLocal/DCU_LS1/', '*.txt'):
	lnxTime = 1357016401+int(file.split('/')[-1].split('_')[1])*86400
	dcu_ls1[lnxTime] = {}
	print "reading file:", file
	dcudata = open(file, 'r')
	linesdcu = dcudata.readlines()
	dcudata.close()
	for line in linesdcu:
		data = line.strip().split()
		dcu_ls1[lnxTime][int(data[0])] = [float(data[1]),float(data[2])/1000] #[temperature,current]

#READ IN TREE
InTreeSim="DarkSimAllModules_"+simDate+"/DarkSimAllModules_"+simDate+".root"
print "Input Tree: ",InTreeSim
simFile = TFile(InTreeSim,'READ')
simTree = simFile.Get('tree')
print "/////////////////////////////////////////////////////////////////"
print "Number of Simulated Modules in the tree: ", simTree.GetEntries()
print "/////////////////////////////////////////////////////////////////"
if readTree: 
	print "************************* READING TREE **************************"
	detid_t     = []
	dtime_t     = []
	partition_t = {}
	temp_t_on   = {}
	temp_t_al   = {}
	ileakc_t_on = {}
	fluence_t   = {}
	nMod=0
	for event in simTree:
		if event.DETID_T not in QuerrMods: continue
		detid_t.append(event.DETID_T)
		partition_t[event.DETID_T] = event.PARTITION_T
		temp_t_on[event.DETID_T] = []
		temp_t_al[event.DETID_T] = []
		ileakc_t_on[event.DETID_T] = []
		fluence_t[event.DETID_T] = []
		if len(dtime_t)==0: fillTime=True
		else: fillTime=False
		for i in range(len(event.dtime_t)):
			if fillTime: dtime_t.append(int(event.dtime_t[i]))
			temp_t_on[event.DETID_T].append(event.temp_t_on[i])
			date_ = TDatime(int(event.dtime_t[i])).GetDate()
			fluence_ = event.fluence_t[i]
			if fluence_ != 0.: temp_t_al[event.DETID_T].append(event.temp_t_on[i])
			else: temp_t_al[event.DETID_T].append(event.temp_t_al[i])
# 			TrkState = Tstate[date_]
# 			if TrkState==0 or date_ < 20130101 or date_ > 20150506: temp_t_al[event.DETID_T].append(event.temp_t_on[i])
# 			elif TrkState==1: temp_t_al[event.DETID_T].append(event.temp_t_of[i])
# 			elif TrkState==2: temp_t_al[event.DETID_T].append(event.temp_t_sb[i])
# 			elif TrkState==3: temp_t_al[event.DETID_T].append(event.temp_t_sd[i])
# 			else: 
# 				print "UNKNOWN TRACKER STATE!!! Setting it to ON state"
# 				temp_t_al[event.DETID_T].append(event.temp_t_on[i])
			ileakc_t_on[event.DETID_T].append(event.ileakc_t_on[i])
			fluence_t[event.DETID_T].append(fluence_)
		nMod+=1
		if nMod%1000==0: print "Finished reading ", nMod, " modules out of ", simTree.GetEntries(), " modules!"
	print "********************* FINISHED READING TREE *********************"
	print "- Dumping detector ids into pickle ..."
	pickle.dump(detid_t,open("DarkSimAllModules_"+simDate+'/detid_t.p','wb'))
	print "- Dumping partitions into pickle ..."
	pickle.dump(partition_t,open("DarkSimAllModules_"+simDate+'/partition_t.p','wb'))
	print "- Dumping time into pickle ..."
	pickle.dump(dtime_t,open("DarkSimAllModules_"+simDate+'/dtime_t.p','wb'))
	print "- Dumping temperature (ON) into pickle ..."
	pickle.dump(temp_t_on,open("DarkSimAllModules_"+simDate+'/temp_t_on.p','wb'))
	print "- Dumping temperature (ALL) into pickle ..."
	pickle.dump(temp_t_al,open("DarkSimAllModules_"+simDate+'/temp_t_al.p','wb'))
	print "- Dumping leakage current into pickle ..."
	pickle.dump(ileakc_t_on,open("DarkSimAllModules_"+simDate+'/ileakc_t_on.p','wb'))
	print "- Dumping fluence into pickle"
	pickle.dump(fluence_t,open("DarkSimAllModules_"+simDate+'/fluence_t.p','wb'))
	print "*********************** FINISHED DUMPING ***********************"
else:
	print "******************* LOADING TREE FROM PICKLE ********************"
	print "-Loading detector ids ..."
	detid_t=pickle.load(open("DarkSimAllModules_"+simDate+'/detid_t.p','rb'))
	print "-Loading partitions ..."
	partition_t=pickle.load(open("DarkSimAllModules_"+simDate+'/partition_t.p','rb'))
	print "-Loading time ..."
	dtime_t=pickle.load(open("DarkSimAllModules_"+simDate+'/dtime_t.p','rb'))
	print "-Loading temperature (ON) ..."
	temp_t_on=pickle.load(open("DarkSimAllModules_"+simDate+'/temp_t_on.p','rb'))
	print "-Loading temperature (ALL) ..."
	temp_t_al=pickle.load(open("DarkSimAllModules_"+simDate+'/temp_t_al.p','rb'))
	print "-Loading leakage current ..."
	ileakc_t_on=pickle.load(open("DarkSimAllModules_"+simDate+'/ileakc_t_on.p','rb'))
	print "******************* LOADED TREE FROM PICKLE ********************"

runDir=os.getcwd()

def findClosest(theList, theNum): #Assumes theList is sorted and returns the closest value to theNum
    theInd = bisect_left(theList, theNum)
    if theInd == len(theList):
        return theInd-1
    if theList[theInd] - theNum < theNum - theList[theInd - 1]:
       return theInd
    else:
       return theInd-1

def formatUpperHist(histogram):
	histogram.GetXaxis().SetLabelSize(0)
	histogram.GetYaxis().SetLabelSize(0.07)
	histogram.GetYaxis().SetTitleSize(0.08)
	histogram.GetYaxis().SetTitleOffset(.61)
	histogram.GetYaxis().CenterTitle()
		
def formatLowerHist(histogram):
	histogram.GetXaxis().SetLabelSize(.07)
	histogram.GetXaxis().SetTitleSize(0.08)
	histogram.GetXaxis().SetTitleOffset(0.95)
	#histogram.GetXaxis().SetNdivisions(506)

	histogram.GetYaxis().SetLabelSize(0.07)
	histogram.GetYaxis().SetTitleSize(0.08)
	histogram.GetYaxis().SetTitleOffset(.61)
	histogram.GetYaxis().CenterTitle()

k_B = 8.617343183775136189e-05
def LeakCorrection(Tref,T):
	E = 1.21 # formerly 1.12 eV
	return (Tref/T)*(Tref/T)*math.exp(-E/(2.*k_B)*(1./Tref-1./T))

outDir = 'DarkSimAllModules_'+simDate+'/singleModules_'+measDataPath.split('/')[-1]
if plotRawData: outDir+='_raw'
if not os.path.exists(runDir+'/'+outDir): os.system('mkdir '+runDir+'/'+outDir)
outRfile = TFile(outDir+"/outRfileSingleModules.root",'RECREATE')
numberModules = len(QuerrMods)
indexMod = 0
for QuerrMod in QuerrMods:
	print "*****************************************************************"
	print "****************** Plotting Module:",QuerrMod,indexMod,"/",numberModules,"******************"
	indexMod+=1
	if QuerrMod not in detid_t:
		print "Module number: ", QuerrMod, " was not found in the simulation! Continuing to next module!"
		continue 
	if not isCurrentScaled: Ion=[item1*LeakCorrection(item2+1.e-10,293.16) for item1,item2 in zip(ileakc_t_on[QuerrMod],temp_t_al[QuerrMod])]
	if isCurrentScaled: Ion=ileakc_t_on[QuerrMod]
	Ton=[item-273.16 for item in temp_t_al[QuerrMod]]
	iper=dtime_t
	
	if partition_t[QuerrMod]==1 or partition_t[QuerrMod]==2: modPart = "TIB"
	if partition_t[QuerrMod]==3 or partition_t[QuerrMod]==4: modPart = "TOB"
	if partition_t[QuerrMod]==5 or partition_t[QuerrMod]==6: modPart = "TID"
	if partition_t[QuerrMod]==7 or partition_t[QuerrMod]==8: modPart = "TEC"
	
	#READ IN DATA
	InFileDatS_I=measDataPath+"/iLeak_perDay/"+str(QuerrMod)+".txt"
	InFileDatS_T=measDataPath.replace("iLeak","TSil")+"/TSil_perDay/"+str(QuerrMod)+".txt"
	if os.path.exists(InFileDatS_I):
		fIdata = open(InFileDatS_I, 'r')
		linesI = fIdata.readlines()
		fIdata.close()
	else:
		print "Warning: Leakage current data file for module",QuerrMod,"does not exist! Creating a dummy plot!"
		linesI=['14/02/2011 22:28:33	19.141','18/02/2013 10:20:57	535.948']
	if os.path.exists(InFileDatS_T):
		fTdata = open(InFileDatS_T, 'r')
		linesT = fTdata.readlines()
		fTdata.close()
	else:
		print "Warning: Temperature data file for module",QuerrMod,"does not exist! Creating a dummy plot!"
		linesT=['14/02/2011 22:28:33	12.8196','11/02/2013 13:21:07	17.644']
	if len(linesI)==0 or len(linesT)==0:
		print "Warning: Skipping the module",QuerrMod,"Empty data file!"
		continue
	
	#*****************Data Extraction*******************************
	dtime_dd_I=[]
	ileak_dd=[]
	dtime_dd_I_raw=[]
	ileak_dd_raw=[]
	ileakmax=0.
	for line in linesI:
		data = line.strip().split()
		try: 
			lnxTime = int(data[0])
			dtime_dd_I_raw.append(lnxTime)
			ileak_dd_raw.append(float(data[1])/1000)
			if TDatime(lnxTime).GetDate()<20130101 or TDatime(lnxTime).GetDate()>20150507:
				if float(data[1])<10.: continue
			else: 
				if float(data[1])==0.: continue
				simulatedCur = Ion[findClosest(dtime_t, lnxTime)]
				if abs(simulatedCur-float(data[1])/1000)/simulatedCur>0.6: continue
			dtime_dd_I.append(lnxTime)
			ileak_dd.append(float(data[1])/1000)
			if float(data[1])/1000>ileakmax and float(data[1])/1000-ileakmax<.025: ileakmax = float(data[1])/1000 
		except: print "Warning! => Unknown data format: ",data,"in", InFileDatS_I
	dtime_dd_T=[]
	temp_dd=[]
	dtime_dd_T_raw=[]
	temp_dd_raw=[]
	for line in linesT:
		data = line.strip().split() 
		try:
			lnxTime = int(data[0])
			dtime_dd_T_raw.append(lnxTime)
			temp_dd_raw.append(float(data[1]))
			if TDatime(lnxTime).GetDate()<20130101 or TDatime(lnxTime).GetDate()>20150507: 
				if float(data[1])>50. or float(data[1])<-20.: continue
				simulatedTemp = Ton[findClosest(dtime_t, lnxTime)]+273.16
				if abs((simulatedTemp-(float(data[1])+273.16))/simulatedTemp)>0.6: continue
			dtime_dd_T.append(lnxTime)
			temp_dd.append(float(data[1]))
		except: print "Warning! => Unknown data format: ",data,"in", InFileDatS_T
	
	#*****************Smooth Leakage Current*******************************
	dtime_dd_I_dic={}
	ileak_dd_dic={}
	for ind in range(len(dtime_dd_I)):
		date=TDatime(dtime_dd_I[ind]).GetDate()
		dtime_dd_I_dic[date] = []
		ileak_dd_dic[date] = []
	for ind in range(len(dtime_dd_I)):
		date=TDatime(dtime_dd_I[ind]).GetDate()
		dtime_dd_I_dic[date].append(dtime_dd_I[ind])
		ileak_dd_dic[date].append(ileak_dd[ind])
	# Add LS1 period:
	for lnxTime in dcu_ls1.keys():
		if QuerrMod not in dcu_ls1[lnxTime].keys(): continue
		date=TDatime(lnxTime).GetDate()
		dtime_dd_I_dic[date] = []
		ileak_dd_dic[date] = []
	for lnxTime in dcu_ls1.keys():
		if QuerrMod not in dcu_ls1[lnxTime].keys(): continue
		date=TDatime(lnxTime).GetDate()
		dtime_dd_I_dic[date].append(lnxTime)
		ileak_dd_dic[date].append(dcu_ls1[lnxTime][QuerrMod][1])
				
	ileak_dd_avgPerDay = []
	dtime_dd_I_avgPerDay = []			
	for date in sorted(ileak_dd_dic.keys()):
		if (dtime_dd_I_dic[date][0]>TDatime(2013,1,1,0,0,1).Convert() and dtime_dd_I_dic[date][0]<TDatime(2015,5,7,0,0,1).Convert()):
			dtime_dd_I_avgPerDay.append(dtime_dd_I_dic[date][0])
			ileak_dd_avgPerDay.append(ileak_dd_dic[date][0])
		else:
			avgLeak = sum(ileak_dd_dic[date])/len(ileak_dd_dic[date])
			newLeakSum = 0
			ind = 0
			for item in ileak_dd_dic[date]:
				if abs((avgLeak-item)/avgLeak)<0.15:
					newLeakSum+=item
					ind+=1
			if ind!=0: 
				dtime_dd_I_avgPerDay.append(dtime_dd_I_dic[date][0])
				ileak_dd_avgPerDay.append(newLeakSum/ind)
	
# 	if not os.path.exists(runDir+'/'+measDataPath+'/iLeak_perDay/'): os.system('mkdir '+measDataPath+'/iLeak_perDay/')
# 	with open(measDataPath+'/iLeak_perDay/'+str(QuerrMod)+'.txt','w') as fout:
# 		for t in range(len(dtime_dd_I_avgPerDay)):
# 			fout.write(str(dtime_dd_I_avgPerDay[t])+'\t'+str(ileak_dd_avgPerDay[t])+'\n')

	#*****************Smooth Temperature*******************************
	dtime_dd_T_dic={}
	temp_dd_dic={}
	for ind in range(len(dtime_dd_T)):
		date=TDatime(dtime_dd_T[ind]).GetDate()
		dtime_dd_T_dic[date] = []
		temp_dd_dic[date] = []
	for ind in range(len(dtime_dd_T)):
		date=TDatime(dtime_dd_T[ind]).GetDate()
		dtime_dd_T_dic[date].append(dtime_dd_T[ind])
		temp_dd_dic[date].append(temp_dd[ind]+273.16)
	# Add LS1 period:
	for lnxTime in dcu_ls1.keys():
		if QuerrMod not in dcu_ls1[lnxTime].keys(): continue
		date=TDatime(lnxTime).GetDate()
		dtime_dd_T_dic[date] = []
		temp_dd_dic[date] = []
	for lnxTime in dcu_ls1.keys():
		if QuerrMod not in dcu_ls1[lnxTime].keys(): continue
		date=TDatime(lnxTime).GetDate()
		dtime_dd_T_dic[date].append(lnxTime)
		temp_dd_dic[date].append(dcu_ls1[lnxTime][QuerrMod][0]+273.16)

	temp_dd_avgPerDay = []
	dtime_dd_T_avgPerDay = []			
	for date in sorted(temp_dd_dic.keys()):
		if (dtime_dd_T_dic[date][0]>TDatime(2013,1,1,0,0,1).Convert() and dtime_dd_T_dic[date][0]<TDatime(2015,5,7,0,0,1).Convert()):
			dtime_dd_T_avgPerDay.append(dtime_dd_T_dic[date][0])
			temp_dd_avgPerDay.append(temp_dd_dic[date][0]-273.16)
		else:
			avgTemp = sum(temp_dd_dic[date])/len(temp_dd_dic[date])
# 			dtime_dd_T_avgPerDay.append(dtime_dd_T_dic[date][0])
# 			temp_dd_avgPerDay.append(avgLeak)
			newTempSum = 0
			ind = 0
			for item in temp_dd_dic[date]:
				if abs((avgTemp-item)/avgTemp)<0.15:
					newTempSum+=item
					ind+=1
			if ind!=0: 
				dtime_dd_T_avgPerDay.append(dtime_dd_T_dic[date][0])
				temp_dd_avgPerDay.append(newTempSum/ind-273.16)

# 	if not os.path.exists(runDir+'/'+measDataPath.replace("iLeak","TSil")+'/TSil_perDay/'): os.system('mkdir '+measDataPath.replace("iLeak","TSil")+'/TSil_perDay/')
# 	with open(measDataPath.replace("iLeak","TSil")+'/TSil_perDay/'+str(QuerrMod)+'.txt','w') as fout:
# 		for t in range(len(dtime_dd_T_avgPerDay)):
# 			fout.write(str(dtime_dd_T_avgPerDay[t])+'\t'+str(temp_dd_avgPerDay[t])+'\n')
			
	IGr_on = TGraph(len(iper),array('d',iper),array('d',Ion))
	IGr_on.SetName(str(QuerrMod)+'_ileak_sim')
	IGr_on.SetMarkerColor(kBlue)
	IGr_on.SetLineColor(kBlue)
	IGr_on.SetMarkerStyle(7)
	#IGr_on.SetMarkerSize(0.3)
	if not len(dtime_dd_I_avgPerDay)==0:
		grI = TGraph(len(dtime_dd_I_avgPerDay),array('d',dtime_dd_I_avgPerDay),array('d',ileak_dd_avgPerDay))
		grI.SetName(str(QuerrMod)+'_ileak_mea')
		grI.SetMarkerColor(kRed)
		grI.SetLineColor(kRed)
		grI.SetMarkerStyle(7)
	else: print "All data are filtered!!!!!!!"
	grIraw =TGraph(len(dtime_dd_I_raw),array('d',dtime_dd_I_raw),array('d',ileak_dd_raw))
	grIraw.SetName(str(QuerrMod)+'_ileak_mea_raw')
	grIraw.SetMarkerColor(kGreen)
	grIraw.SetLineColor(kGreen)
	grIraw.SetMarkerStyle(7)
	
	TGr_on = TGraph(len(iper),array('d',iper),array('d',Ton))
	TGr_on.SetName(str(QuerrMod)+'_temp_sim')
	TGr_on.SetMarkerColor(kBlue)
	TGr_on.SetLineColor(kBlue)
	TGr_on.SetMarkerStyle(7)
	if drawTempData: grT = TGraph(len(dtime_dd_T_avgPerDay),array('d',dtime_dd_T_avgPerDay),array('d',temp_dd_avgPerDay))
	else: grT = TGraph(len(iper),array('d',iper),array('d',Ton))
	grT.SetName(str(QuerrMod)+'_temp_mea')
	grT.SetMarkerColor(kRed)
	grT.SetLineColor(kRed)
	grT.SetMarkerStyle(7)
	if drawTempData: grTraw = TGraph(len(dtime_dd_T_raw),array('d',dtime_dd_T_raw),array('d',temp_dd_raw))
	else: grTraw = TGraph(len(iper),array('d',iper),array('d',Ton))
	grTraw.SetName(str(QuerrMod)+'_temp_mea_raw')
	grTraw.SetMarkerColor(kGreen)
	grTraw.SetLineColor(kGreen)
	grTraw.SetMarkerStyle(7)
	XaxisnameI = "Date"
	YaxisnameI = "Current (mA)"
	XaxisnameT = "Date"
	YaxisnameT = "Temperature (C)"
	
	mgnI = TMultiGraph()
	mgnI.SetTitle(modPart+" Module detector ID: "+str(QuerrMod))
	mgnI.Add(IGr_on,"p")
	if plotRawData: mgnI.Add(grIraw,"p")
	if not len(dtime_dd_I_avgPerDay)==0: mgnI.Add(grI,"p")
	
	mgnT = TMultiGraph()
	mgnT.SetTitle("")
	mgnT.Add(TGr_on,"p")
	if drawTempData: 
		if plotRawData: mgnT.Add(grTraw,"p")
		mgnT.Add(grT,"p")
	
	cIT = TCanvas("Module_"+str(QuerrMod),"Module_"+str(QuerrMod),1200,800)
	yDiv = 0.45
	uMargin = 0.10
	bMargin = 0.18
	rMargin = 0.06
	lMargin = 0.12
	uPad=TPad("uPad","",0,yDiv,1,1) #for actual plots
	uPad.SetTopMargin(uMargin)
	uPad.SetBottomMargin(0)
	uPad.SetRightMargin(rMargin)
	uPad.SetLeftMargin(lMargin)
	uPad.SetGrid()#SetGridy()
	uPad.Draw()
	lPad=TPad("lPad","",0,0,1,yDiv) #for sigma runner
	lPad.SetTopMargin(0)
	lPad.SetBottomMargin(bMargin)
	lPad.SetRightMargin(rMargin)
	lPad.SetLeftMargin(lMargin)
	lPad.SetGrid()#SetGridy()
	lPad.Draw()
	
	uPad.cd()
	mgnI.Draw("AP")
	mgnI.GetXaxis().SetTimeDisplay(1)
	mgnI.GetXaxis().SetNdivisions(-503)
	mgnI.GetXaxis().SetTimeFormat("%Y-%m-%d")
	mgnI.GetXaxis().SetTimeOffset(0,"gmt")
	mgnI.GetXaxis().SetTitle(XaxisnameI)
	mgnI.GetYaxis().SetTitle(YaxisnameI)
	mgnI.GetXaxis().SetLimits(min(iper),max(iper))
	mgnI.GetHistogram().SetMinimum(-0.02)#min(Ion))
	mgnI.GetHistogram().SetMaximum(1.5*max(ileakmax,max(Ion)))#2.25*max(Ion))
	#mgnI.GetYaxis().SetTitleOffset(1.5)
	formatUpperHist(mgnI)
	x1=.7
	y1=.7
	x2=x1+.15
	y2=y1+.175
	legI = TLegend(x1,y1,x2,y2)
	legI.AddEntry(IGr_on,"Simulated","pl")
	if not len(dtime_dd_I_avgPerDay)==0: legI.AddEntry(grI,"Measured","pl")
	elif plotRawData: legI.AddEntry(grIraw,"Measured","pl")
	legI.SetTextFont(10)
	legI.Draw()
	
	lPad.cd()
	mgnT.Draw("AP")
	mgnT.GetXaxis().SetTimeDisplay(1)
	mgnT.GetXaxis().SetNdivisions(-503)
	mgnT.GetXaxis().SetTimeFormat("%Y-%m-%d")
	mgnT.GetXaxis().SetTimeOffset(0,"gmt")
	mgnT.GetXaxis().SetTitle(XaxisnameT)
	mgnT.GetYaxis().SetTitle(YaxisnameT)
	mgnT.GetXaxis().SetLimits(min(iper),max(iper))
	mgnT.GetHistogram().SetMinimum(min(Ton[:-1])-5)
	mgnT.GetHistogram().SetMaximum(max(Ton)+10)
	formatLowerHist(mgnT)
	
	cIT.Write()
	IGr_on.Write()
	grI.Write()
	grIraw.Write()
	TGr_on.Write()
	grT.Write()
	grTraw.Write()
	cIT.SaveAs(outDir+"/IleakT_"+str(QuerrMod)+".png")
	#cIT.SaveAs(outDir+"/IleakT_"+str(QuerrMod)+".pdf")

outRfile.Close()
simFile.Close()
print "***************************** DONE *********************************"
  
