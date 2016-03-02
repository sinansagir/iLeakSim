#!/usr/bin/python

import os,sys,fnmatch,pickle
from array import array
from ROOT import *
gROOT.SetBatch(1)

##################################################################################################################
# The code looks for the input simulation tree in "DarkSimAllModules_<simDate>/DarkSimAllModules_<simDate>.root"
# The output files will be in "DarkSimAllModules_<simDate>/plotSingleModules/". 
##################################################################################################################

#******************************Input to edit******************************************************
measDataPath = "MeasData/SingleModules"
simDate = "2016_3_2"
readTree=False # This needs to be true if running the code on the tree for the first time. It will dump what's read from tree into pickle files and these can be loaded if this option is set to "False"
isCurrentScaled = False # Scale current to measured temperature (Check how this is done!!!! The default method assumes that the simulated current is at 20C)
QuerrMods=[369120378,402672418,436228134,470046629]

# def findfiles(path, filtre):
#     for root, dirs, files in os.walk(path):
#         for f in fnmatch.filter(files, filtre):
#             yield os.path.join(root, f)
# 
# QuerrMods = []
# for file in findfiles(measDataPath+'/Ileak/', '*.txt'):
#     QuerrMods.append(int(file.split('/')[-1][:-4]))

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
	ileakc_t_on = {}
	nMod=0
	for event in simTree:
		detid_t.append(event.DETID_T)
		partition_t[event.DETID_T] = event.PARTITION_T
		temp_t_on[event.DETID_T] = []
		ileakc_t_on[event.DETID_T] = []
		if len(dtime_t)==0: fillTime=True
		else: fillTime=False
		for i in range(len(event.dtime_t)):
			if fillTime: dtime_t.append(int(event.dtime_t[i]))
			temp_t_on[event.DETID_T].append(event.temp_t_on[i])
			ileakc_t_on[event.DETID_T].append(event.ileakc_t_on[i])
		nMod+=1
		if nMod%1000==0: print "Finished reading ", nMod, " modules out of ", simTree.GetEntries(), " modules!"
	print "********************* FINISHED READING TREE *********************"
	print "- Dumping detector ids into pickle ..."
	pickle.dump(detid_t,open("DarkSimAllModules_"+simDate+'/detid_t.p','wb'))
	print "- Dumping partitions into pickle ..."
	pickle.dump(partition_t,open("DarkSimAllModules_"+simDate+'/partition_t.p','wb'))
	print "- Dumping time into pickle ..."
	pickle.dump(dtime_t,open("DarkSimAllModules_"+simDate+'/dtime_t.p','wb'))
	print "- Dumping temperature into pickle ..."
	pickle.dump(temp_t_on,open("DarkSimAllModules_"+simDate+'/temp_t_on.p','wb'))
	print "- Dumping leakage current into pickle ..."
	pickle.dump(ileakc_t_on,open("DarkSimAllModules_"+simDate+'/ileakc_t_on.p','wb'))
	print "*********************** FINISHED DUMPING ***********************"
else:
	print "******************* LOADING TREE FROM PICKLE ********************"
	print "-Loading detector ids ..."
	detid_t=pickle.load(open("DarkSimAllModules_"+simDate+'/detid_t.p','rb'))
	print "-Loading partitions ..."
	partition_t=pickle.load(open("DarkSimAllModules_"+simDate+'/partition_t.p','rb'))
	print "-Loading time ..."
	dtime_t=pickle.load(open("DarkSimAllModules_"+simDate+'/dtime_t.p','rb'))
	print "-Loading temperature ..."
	temp_t_on=pickle.load(open("DarkSimAllModules_"+simDate+'/temp_t_on.p','rb'))
	print "-Loading leakage current ..."
	ileakc_t_on=pickle.load(open("DarkSimAllModules_"+simDate+'/ileakc_t_on.p','rb'))
	print "******************* LOADED TREE FROM PICKLE ********************"

runDir=os.getcwd()

k_B = 8.617343183775136189e-05
def LeakCorrection(Tref,T):
	E = 1.21 # formerly 1.12 eV
	return (Tref/T)*(Tref/T)*exp(-E/(2.*k_B)*(1./Tref-1./T))

if not os.path.exists(runDir+'/DarkSimAllModules_'+simDate+'/plotSingleModules/'): os.system('mkdir DarkSimAllModules_'+simDate+'/plotSingleModules/')
outRfile = TFile("DarkSimAllModules_"+simDate+"/plotSingleModules/outRfile.root",'RECREATE')
for QuerrMod in QuerrMods:
	print "*****************************************************************"
	print "****************** Plotting Module:",QuerrMod,"******************"
	if QuerrMod not in detid_t:
		print "Module number: ", QuerrMod, " was not found in the simulation! Continuing to next module!"
		continue 
	if not isCurrentScaled: Ion=[item1*LeakCorrection(item2+1.e-10,293.16) for item1,item2 in zip(ileakc_t_on[QuerrMod],temp_t_on[QuerrMod])]
	if isCurrentScaled: Ion=ileakc_t_on[QuerrMod]
	Ton=[item-273.16 for item in temp_t_on[QuerrMod]]
	iper=dtime_t
	
	if partition_t[QuerrMod]==1 or partition_t[QuerrMod]==2: modPart = "TIB"
	if partition_t[QuerrMod]==3 or partition_t[QuerrMod]==4: modPart = "TOB"
	if partition_t[QuerrMod]==5 or partition_t[QuerrMod]==6: modPart = "TID"
	if partition_t[QuerrMod]==7 or partition_t[QuerrMod]==8: modPart = "TEC"
	
	#print runDir+'DarkSimAllModules_'+simDate+'/plotSingleModules/'
	saveNameI = "DarkSimAllModules_"+simDate+"/plotSingleModules/Ileak_"+str(QuerrMod)
	saveNameT = "DarkSimAllModules_"+simDate+"/plotSingleModules/TSil_"+str(QuerrMod)
	
	#READ IN DATA
	InFileDatS_I=measDataPath+"/Ileak/"+str(QuerrMod)+".txt"
	InFileDatS_T=measDataPath+"/TSil/"+str(QuerrMod)+".txt"
	fileFormat = 'txt'
	if os.path.exists(InFileDatS_I):
		fIdata = open(InFileDatS_I, 'r')
		linesI = fIdata.readlines()
		fIdata.close()
	elif os.path.exists(InFileDatS_I[:-3]+'pl'):
		fIdata = open(InFileDatS_I[:-3]+'pl', 'r')
		linesI = fIdata.readlines()
		fIdata.close()
		fileFormat = 'pl'
	else:
		print "Error: Leakage current data file for module",QuerrMod,"does not exist! Creating a dummy plot!"
		linesI=['14/02/2011 22:28:33	19.141','18/02/2013 10:20:57	535.948']
		fileFormat = 'txt'
	if os.path.exists(InFileDatS_T):
		fTdata = open(InFileDatS_T, 'r')
		linesT = fTdata.readlines()
		fTdata.close()
	elif os.path.exists(InFileDatS_T[:-3]+'pl'):
		fTdata = open(InFileDatS_T[:-3]+'pl', 'r')
		linesT = fTdata.readlines()
		fTdata.close()
		fileFormat = 'pl'
	else:
		print "Error: Temperature data file for module",QuerrMod,"does not exist! Creating a dummy plot!"
		linesT=['14/02/2011 22:28:33	12.8196','11/02/2013 13:21:07	17.644']
		fileFormat = 'txt'
	
	dtime_dd_I=[]
	ileak_dd=[]
	ileakmax=0.
	for line in linesI:
		data = line.strip().split()
		try: 
			if fileFormat=='txt':
				day    = int(data[0][:2])
				month  = int(data[0][3:5])
				year   = int(data[0][6:])
				hour   = int(data[1][:2])
				minute = int(data[1][3:5])
				second = int(data[1][6:])
				dtime_dd_I.append(TDatime(year,month,day,hour,minute,second).Convert())
				ileak_dd.append(float(data[2])/1000)
				if float(data[2])/1000>ileakmax and float(data[2])/1000-ileakmax<.025: ileakmax = float(data[2])/1000 
			if fileFormat=='pl':
				dtime_dd_I.append(int(data[0]))
				ileak_dd.append(float(data[1])/1000)
				if float(data[1])/1000>ileakmax and float(data[1])/1000-ileakmax<.025: ileakmax = float(data[1])/1000 
		except: print "Warning! => Unrecognized data format: ",data,"in", InFileDatS_I
	dtime_dd_T=[]
	temp_dd=[]
	for line in linesT:
		data = line.strip().split() 
		try:
			if fileFormat=='txt':
				day    = int(data[0][:2])
				month  = int(data[0][3:5])
				year   = int(data[0][6:])
				hour   = int(data[1][:2])
				minute = int(data[1][3:5])
				second = int(data[1][6:])
				dtime_dd_T.append(TDatime(year,month,day,hour,minute,second).Convert())
				temp_dd.append(float(data[2]))
			if fileFormat=='pl':
				dtime_dd_T.append(int(data[0]))
				temp_dd.append(float(data[1]))
		except: print "Warning! => Unrecognized data format: ",data,"in", InFileDatS_T
	
	#*****************Data Extraction*******************************

	IGr_on = TGraph(len(iper),array('d',iper),array('d',Ion))
	IGr_on.SetMarkerColor(kBlue)
	IGr_on.SetLineColor(kBlue)
	IGr_on.SetMarkerStyle(7)
	#IGr_on.SetMarkerSize(0.3)
	grI = TGraph(len(dtime_dd_I),array('d',dtime_dd_I),array('d',ileak_dd))
	grI.SetMarkerColor(kRed)
	grI.SetLineColor(kRed)
	grI.SetMarkerStyle(1)
	#grI.SetMarkerSize(0.3)
	
	TGr_on = TGraph(len(iper),array('d',iper),array('d',Ton))
	TGr_on.SetMarkerColor(kBlue)
	TGr_on.SetLineColor(kBlue)
	TGr_on.SetMarkerStyle(7)
	#TGr_on.SetMarkerSize(0.3)
	grT = TGraph(len(dtime_dd_T),array('d',dtime_dd_T),array('d',temp_dd))
	grT.SetMarkerColor(kRed)
	grT.SetLineColor(kRed)
	grT.SetMarkerStyle(1)
	#TGr_on.SetMarkerSize(0.3)
	XaxisnameI = "Date"
	YaxisnameI = "Current (mA)"
	XaxisnameT = "Date"
	YaxisnameT = "Temperature (C)"
	
	mgnI = TMultiGraph()
	mgnI.SetTitle("Simulated and measured data for Module: "+str(QuerrMod)+" ("+modPart+")")
	mgnI.Add(IGr_on,"p")
	mgnI.Add(grI,"p")
	
	mgnT = TMultiGraph()
	mgnT.SetTitle("Simulated and measured data for Module: "+str(QuerrMod)+" ("+modPart+")")
	mgnT.Add(TGr_on,"p")
	mgnT.Add(grT,"p")
	
	cI = TCanvas("Module_I_"+str(QuerrMod),"Module_I_"+str(QuerrMod),800,400)
	gStyle.SetFillColor(kWhite)
	
	cI.SetGrid()
	mgnI.Draw("AP")
	mgnI.GetXaxis().SetTimeDisplay(1)
	mgnI.GetXaxis().SetNdivisions(-503)
	mgnI.GetXaxis().SetTimeFormat("%Y-%m-%d")
	mgnI.GetXaxis().SetTimeOffset(0,"gmt")
	mgnI.GetXaxis().SetTitle(XaxisnameI)
	mgnI.GetYaxis().SetTitle(YaxisnameI)
	mgnI.GetXaxis().SetLimits(min(iper),max(iper))
	mgnI.GetHistogram().SetMinimum(0)#min(Ion))
	mgnI.GetHistogram().SetMaximum(1.5*max(ileakmax,max(Ion)))#2.25*max(Ion))
	#mgnI.GetYaxis().SetTitleOffset(1.5)
	x1=.7
	y1=.7
	x2=x1+.2
	y2=y1+.175
	legI = TLegend(x1,y1,x2,y2)
	legI.AddEntry(IGr_on,"Simulated data","pl")
	legI.AddEntry(grI,"Measured data","pl")
	legI.SetTextFont(10)
	legI.Draw()

	cI.Write()
	cI.SaveAs(saveNameI+".png")
	cI.SaveAs(saveNameI+".pdf")
	
	cT = TCanvas("Module_T_"+str(QuerrMod),"Module_T_"+str(QuerrMod),800,400)
	gStyle.SetFillColor(kWhite)
	
	cT.SetGrid()
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
	legT = TLegend(x1-.55,y1-.55,x2-.55,y2-.55)
	legT.AddEntry(TGr_on,"Simulated data","pl")
	legT.AddEntry(grT,"Measured data","pl")
	legT.SetTextFont(10)
	legT.Draw()
	
	cT.Write()
	cT.SaveAs(saveNameT+".png")
	cT.SaveAs(saveNameT+".pdf")
outRfile.Close()
simFile.Close()
print "***************************** DONE *********************************"
  
