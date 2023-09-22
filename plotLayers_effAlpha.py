#!/usr/bin/python

import os,sys,fnmatch,math
import pickle
import numpy as np
from ROOT import *
from array import array
gROOT.SetBatch(1)

##################################################################################################################
# The code looks for the input simulation tree in "DarkSimAllModules_<simDate>/DarkSimAllModules_<simDate>.root"
# The output files will be in "DarkSimAllModules_<simDate>/plotSingleModules/". 
##################################################################################################################
# by 11/06/2011 --> 1.02 /fb
# by 08/10/2011 --> 5.03 /fb
# by 23/10/2011 --> 6.08 /fb
# by 08/05/2012 --> 7.53 /fb
# by 13/06/2012 --> 12.16 /fb
# by 18/06/2012 --> 13.02 /fb
# by 16/07/2012 --> 14.09 /fb
# by 02/09/2012 --> 20.15 /fb
# by 09/09/2012 --> 21.13 /fb
# by 06/10/2012 --> 22.74 /fb
# by 17/11/2012 --> 28.03 /fb
# by 05/12/2012 --> 30.01 /fb
# by 19/08/2015 --> 30.2  /fb
# by 24/09/2015 --> 31.0  /fb
# by 30/10/2015 --> 33.57 /fb

#******************************Input to edit******************************************************
measDataPath = "../iLeakSim_Feb16_leakCalcV1/MeasData/AllModules"
simDate = "2016_3_2"
readTree=False # This needs to be true if running the code on the tree for the first time. It will dump what's read from tree into pickle files and these can be loaded if this option is set to "False"
scaleCurrent = True # Scale current to measured temperature (Check how this is done!!!! The default method assumes that the simulated current is at 20C)
scaleTemp = 0

fitDates = {
			'block1':['11-06-2011','08-10-2011'],
			'block2':['09-05-2012','13-06-2012'],
			'block3':['16-07-2012','02-09-2012'],
			'block4':['06-10-2012','17-11-2012'],
			#'block5':['18-08-2015','24-09-2015','10-10-2015','30-10-2015']
			#'block5':['24-09-2015','10-10-2015','30-10-2015']
			#'block5':['24-09-2015','30-10-2015']
			'block5':['18-08-2015','08-09-2015','20-09-2015','24-09-2015','10-10-2015','16-10-2015','30-10-2015']
		    }
		    
#READ IN OUTLIERS
outliers = {}
# for block in fitDates.keys():
# 	for QDate in fitDates[block]:
# 		outliers[QDate] = []
# 		InFileData="DarkSimAllModules_"+simDate+"/plotAllModules/Ileak_"+QDate+"_outliers.txt"
# 		fIdata = open(InFileData, 'r')
# 		linesI = fIdata.readlines()
# 		fIdata.close()
# 		for line in linesI:
# 			data = line.strip().split()
# 			try: 
# 				outliers[QDate].append(int(data[2]))
# 			except: print "Warning! => Unknown data format: ",data,"in", InFileData

#READ IN TREE
InTreeSim="DarkSimAllModules_"+simDate+"/DarkSimAllModules_"+simDate+".root"
print "Input Tree: ",InTreeSim
RFile = TFile(InTreeSim,'READ')
TTree = RFile.Get('tree')
print "/////////////////////////////////////////////////////////////////"
print "Number of Simulated Modules in the tree: ", TTree.GetEntries()
print "/////////////////////////////////////////////////////////////////"
if readTree: 
	print "************************* READING TREE **************************"
	detid_t     = []
	dtime_t     = []
	partition_t = {}
	temp_t_on   = {}
	ileakc_t_on = {}
	fluence_t   = {}
	nMod=0
	for event in TTree:
		detid_t.append(event.DETID_T)
		partition_t[event.DETID_T] = event.PARTITION_T
		temp_t_on[event.DETID_T] = []
		ileakc_t_on[event.DETID_T] = []
		fluence_t[event.DETID_T] = []
		if len(dtime_t)==0: fillTime=True
		else: fillTime=False
		for i in range(len(event.dtime_t)):
			if fillTime: dtime_t.append(int(event.dtime_t[i]))
			temp_t_on[event.DETID_T].append(event.temp_t_on[i])
			ileakc_t_on[event.DETID_T].append(event.ileakc_t_on[i])
			fluence_t[event.DETID_T].append(event.fluence_t[i])
		nMod+=1
		if nMod%1000==0: print "Finished reading ", nMod, " modules out of ", TTree.GetEntries(), " modules!"
	print "********************* FINISHED READING TREE *********************"
	print "- Dumping detector ids into pickle"
	pickle.dump(detid_t,open("DarkSimAllModules_"+simDate+'/detid_t.p','wb'))
	print "- Dumping partitions into pickle"
	pickle.dump(partition_t,open("DarkSimAllModules_"+simDate+'/partition_t.p','wb'))
	print "- Dumping time into pickle"
	pickle.dump(dtime_t,open("DarkSimAllModules_"+simDate+'/dtime_t.p','wb'))
	print "- Dumping temperature into pickle"
	pickle.dump(temp_t_on,open("DarkSimAllModules_"+simDate+'/temp_t_on.p','wb'))
	print "- Dumping leakage current into pickle"
	pickle.dump(ileakc_t_on,open("DarkSimAllModules_"+simDate+'/ileakc_t_on.p','wb'))
	print "- Dumping fluence into pickle"
	pickle.dump(fluence_t,open("DarkSimAllModules_"+simDate+'/fluence_t.p','wb'))
	print "*********************** FINISHED DUMPING ***********************"
else:
	print "******************* LOADING TREE FROM PICKLE ********************"
	detid_t=pickle.load(open("DarkSimAllModules_"+simDate+'/detid_t.p','rb'))
	print "-Loaded detector ids"
	partition_t=pickle.load(open("DarkSimAllModules_"+simDate+'/partition_t.p','rb'))
	print "-Loaded partitions"
	dtime_t=pickle.load(open("DarkSimAllModules_"+simDate+'/dtime_t.p','rb'))
	print "-Loaded time"
	temp_t_on=pickle.load(open("DarkSimAllModules_"+simDate+'/temp_t_on.p','rb'))
	print "-Loaded temperature"
	ileakc_t_on=pickle.load(open("DarkSimAllModules_"+simDate+'/ileakc_t_on.p','rb'))
	print "-Loaded leakage current"
	fluence_t=pickle.load(open("DarkSimAllModules_"+simDate+'/fluence_t.p','rb'))
	print "-Loaded fluence"
	print "******************* LOADED TREE FROM PICKLE ********************"

print "========>>>>>>>> READING TRACKER MAP"
TrackMap="InputData/TrackMap.root"
TrackMapRFile = TFile(TrackMap,'READ')
TrackMapTTree = TrackMapRFile.Get('treemap')
x,y,z,l,w1,w2,d,part,pos = {},{},{},{},{},{},{},{},{}
volume = {}
for event in TrackMapTTree:
	x[event.DETID] = event.X
	y[event.DETID] = event.Y
	z[event.DETID] = event.Z
	l[event.DETID] = event.L
	w1[event.DETID]= event.W1
	w2[event.DETID]= event.W2
	d[event.DETID] = event.D
	part[event.DETID] = event.Partition
	pos[event.DETID] = event.StructPos
	volume[event.DETID] = event.D*(event.W1+event.W2)*(event.L/2)*1e6 #cm^3
TrackMapRFile.Close()
print "========>>>>>>>> FINISHED READING TRACKER MAP"

print "========>>>>>>>> READING FLUENCE MATCHING"
TFileFluence = TFile("InputData/FluenceMatching.root",'READ')
TTreeFluence = TFileFluence.Get("SimTree_old")
fluenceNew = {}
for module in TTreeFluence:
	fluenceNew[module.DETID_T] = module.FINFLU_T # new algo
TFileFluence.Close()
print "========>>>>>>>> FINISHED READING FLUENCE MATCHING"

# Read Input Data for Lumi
lumiFile = "InputData/lumi/Lumi.txt"
infileLumi = open(lumiFile, 'r')
print "Reading Lumi File"
linesLumi = infileLumi.readlines()
infileLumi.close()
lumiAll=[]
lumiPerDay=[]
IntLum=0.
IntLumR1=0.
dtime_t_temp = [TDatime(int(item)).GetDate() for item in dtime_t]
dtime_t = [int(item) for item in dtime_t]
for i in range(len(linesLumi)):
	data = linesLumi[i].strip().split()
	try: 
		IntLum+=float(data[2])/1e6 # in INVFB
		#if int(data[1]) in dtime_t:
		if int(data[0].split('/')[2]+data[0].split('/')[1]+data[0].split('/')[0]) in dtime_t_temp:
			lumiAll.append(IntLum)
			lumiPerDay.append(float(data[2]))
			if data[0]=='01/01/2013':IntLumR1=IntLum
	except: print "Warning! => Unknown data format: ",data,"in",lumiFile
print "Total Integrated Lumi:",lumiAll[-1]
print "Total Integrated Lumi Run1:",IntLumR1
print "Total Integrated Lumi Run2:",lumiAll[-1]-IntLumR1

#Add missing fluences back!
xsec_7tev  = 7.35e7 #nb
xsec_13tev = 7.91e7 #nb
xsec_14tev = 7.99e7 #nb
for mod in fluenceNew.keys():
	if mod in fluence_t.keys():continue
	fluence_t[mod] = []
	for i in range(len(lumiPerDay)):
		if i/4>=1391: xsec=xsec_13tev # Tracker started to be cooled down to -15C (from 4C in Run 1) on 08/01/15 (?) according to Sasha tools. Number of days from the simulation start date -> 08/01/15-19/03/11=1391 days. Taking this as the starting date of the 13 TeV Run 2!!!!!
		else: xsec=xsec_7tev
		fluence_t[mod].append(lumiPerDay[i]*fluenceNew[mod]*xsec) # two different fluence matchings to calculate 1MeV equivalent fluence per day with Luminosity

k_B = 8.617343183775136189e-05
def LeakCorrection(Tref,T):
	E = 1.21 # formerly 1.12 eV
	return (Tref/T)*(Tref/T)*exp(-(E/(2.*k_B))*(1./Tref-1./T))

#READ IN DATA
dataTempCur = {}
for block in fitDates.keys():
	for QDate in fitDates[block]:
		dataTempCur[QDate] = {}
		for mod in x.keys(): dataTempCur[QDate][mod] = [-99.,-99.]
		InFileDatA_I=measDataPath+"/Ileak/Ileak_"+QDate+".txt"
		InFileDatA_T=measDataPath+"/Temp/Temp_"+QDate+".txt"
		fIdata = open(InFileDatA_I, 'r')
		linesI = fIdata.readlines()
		fIdata.close()
		fTdata = open(InFileDatA_T, 'r')
		linesT = fTdata.readlines()
		fTdata.close()
		for line in linesI:
			data = line.strip().split()
			try: dataTempCur[QDate][int(data[0])][0]=float(data[1])
			except: print "Warning! => Unknown data format: ",data,"in", InFileDatA_I
		for line in linesT:
			data = line.strip().split() 
			try: dataTempCur[QDate][int(data[0])][1]=float(data[1])
			except: print "Warning! => Unknown data format: ",data,"in", InFileDatA_T

#Scale current to 0C and average to 1cm^3 volume:
print "========>>>>>>>> SCALING DATA TO 0C and AVERAGING"
for block in fitDates.keys():
	for QDate in fitDates[block]:
		for mod in dataTempCur[QDate].keys():
			if dataTempCur[QDate][mod][0] == -99. or dataTempCur[QDate][mod][1] == -99.: continue
			dataTempCur[QDate][mod][0]=dataTempCur[QDate][mod][0]*LeakCorrection(273.16,dataTempCur[QDate][mod][1]+273.16)/volume[mod] #muA/cm^3 @0C			
print "========>>>>>>>> SCALING SIM TO 0C and AVERAGING"
for mod in ileakc_t_on.keys():
	ileakc_t_on[mod]=[item*LeakCorrection(273.16,293.16)*1000./volume[mod] for item in ileakc_t_on[mod]] #muA/cm^3 @0C
print "========>>>>>>>> FINISHED SCALING TO 0C and AVERAGING"

limitsTIB = {
			"block1":{
					  fitDates["block1"][0]:{1:[0.,12.],2:[0.,10.],3:[0.,6.],4:[0.,4.]},
					  fitDates["block1"][1]:{1:[0.,12.],2:[3.,10.],3:[2.,6.],4:[0.,5.]}
					  },
		    "block2":{
					  fitDates["block2"][0]:{1:[5.,30.],2:[0.,20.],3:[0.,10.],4:[0.,10.]},
					  fitDates["block2"][1]:{1:[5.,30.],2:[0.,20.],3:[5.5,14.],4:[6.,10.]}
					  },
		    "block3":{
					  fitDates["block3"][0]:{1:[10.,50.],2:[0.,50.],3:[10.,20.],4:[0.,16.]},
					  fitDates["block3"][1]:{1:[15.,50.],2:[12.,50.],3:[14.,20.],4:[10.,16.]}
					  },
		    "block4":{
					  fitDates["block4"][0]:{1:[10.,60.],2:[10.,40.],3:[0.,25.],4:[11.,22.]},
					  fitDates["block4"][1]:{1:[10.,60.],2:[10.,40.],3:[0.,25.],4:[11.,22.]}
					  },
		    "block5":{
					  fitDates["block5"][0]:{1:[20.,60.],2:[10.,35.],3:[20.,40.],4:[0.,18.]},
					  fitDates["block5"][1]:{1:[20.,60.],2:[10.,35.],3:[20.,40.],4:[0.,18.]},
					  fitDates["block5"][2]:{1:[20.,60.],2:[10.,35.],3:[20.,40.],4:[0.,18.]},
					  fitDates["block5"][3]:{1:[20.,60.],2:[10.,35.],3:[20.,40.],4:[0.,18.]},
					  fitDates["block5"][4]:{1:[20.,60.],2:[10.,35.],3:[10.,40.],4:[0.,20.]},
					  fitDates["block5"][5]:{1:[20.,60.],2:[10.,35.],3:[10.,40.],4:[0.,20.]},
					  fitDates["block5"][6]:{1:[20.,60.],2:[10.,35.],3:[10.,40.],4:[0.,20.]}
					  }
		    }

limitsTOB = {
			"block1":{
					  fitDates["block1"][0]:{1:[0.,2.],2:[0.,1.5],3:[0.,1.],4:[0.,1.2],5:[0.,1.],6:[0.,0.9]},
					  fitDates["block1"][1]:{1:[2.,4.],2:[1.,3.],3:[1.5,4.],4:[1.6,3.],5:[0.,2.],6:[1.2,2.]}
					  },
		    "block2":{
					  fitDates["block2"][0]:{1:[0.,4.],2:[0.,4.],3:[0.,10.],4:[0.,3.],5:[1.,3.],6:[0.,3.]},
					  fitDates["block2"][1]:{1:[5.,8.],2:[4.,7.],3:[4.,10.],4:[3.,5.],5:[1.,5.],6:[3.,10.]}
					  },
		    "block3":{
					  fitDates["block3"][0]:{1:[0.,10.],2:[0.,10.],3:[0.,7.],4:[3.,10.],5:[2.,6.],6:[0.,10.]},
					  fitDates["block3"][1]:{1:[7.,14.],2:[6.,12.],3:[6.,20.],4:[5.,10.],5:[5.,8.],6:[4.,8.]}
					  },
		    "block4":{
					  fitDates["block4"][0]:{1:[0.,14.],2:[6.,20.],3:[6.,10.],4:[6.,10.],5:[4.,8.],6:[4.,8.]},
					  fitDates["block4"][1]:{1:[10.,16.],2:[6.,20.],3:[6.,20.],4:[8.,12.],5:[6.,10.],6:[6.,10.]}
					  },
		    "block5":{
					  fitDates["block5"][0]:{1:[9.,15.],2:[7.,15.],3:[5.,14.],4:[6.,9.],5:[5.,11.],6:[0.,10.]},
					  fitDates["block5"][1]:{1:[9.,15.],2:[7.,15.],3:[5.,14.],4:[6.,9.],5:[5.,11.],6:[0.,10.]},
					  fitDates["block5"][2]:{1:[9.,15.],2:[7.,15.],3:[5.,14.],4:[6.,9.],5:[5.,11.],6:[0.,10.]},
					  fitDates["block5"][3]:{1:[9.,15.],2:[7.,15.],3:[5.,14.],4:[6.,9.],5:[5.,11.],6:[0.,10.]},
					  fitDates["block5"][4]:{1:[9.,15.],2:[7.,15.],3:[8.,14.],4:[6.,11.],5:[6.,11.],6:[0.,10.]},
					  fitDates["block5"][5]:{1:[9.,15.],2:[7.,15.],3:[8.,14.],4:[6.,11.],5:[6.,11.],6:[0.,10.]},
					  fitDates["block5"][6]:{1:[9.,15.],2:[7.,15.],3:[8.,14.],4:[6.,11.],5:[6.,11.],6:[0.,10.]}
					  }
		    }
grs = {}
effAlpha = {}
par0 = {}
canvs = {}
Fits = {}
qdateInd = 0
QuerrDays = {}
for block in fitDates.keys():
	Fits[block] = TF1("fit_"+block, "pol1")
	if block=="dontfixit":
		Fits[block].FixParameter(0, 0)
	for QDate in fitDates[block]:
		qday   = int(QDate[:2])
		qmonth = int(QDate[3:5])
		qyear  = int(QDate[6:])
		querday = TDatime(qyear,qmonth,qday,0,0,1).Convert()
		for w in range(len(dtime_t)):
			if dtime_t[w]<=querday and dtime_t[w+1]>querday:
				QuerrDays[QDate]=w+1
				Datum = TDatime(int(dtime_t[QuerrDays[QDate]]))
				print "////////////////////////////////////////////////////////////////////////"
				print "************************************************************************"
				print "Data/Simulation on ",Datum.GetDate()," , ",QuerrDays[QDate], "days since simulation started"
				print "************************************************************************"
				print "////////////////////////////////////////////////////////////////////////"
				break
		try: print QuerrDays[QDate]
		except: 
			print QDate, "not found in the tree"
			continue
			
	grs[block] = {}
	canvs[block] = {}
	effAlpha[block] = {}
	par0[block] = {}
	for i in range(1,5):
		fluence=[]
		current=[]
		for QDate in fitDates[block]:
			indBefore=0
			indAfter =0
			for mod in dataTempCur[QDate].keys():
				if pos[mod]!=i: continue
				if 'TIB' not in part[mod]: continue
				indBefore+=1
				if mod not in fluence_t.keys(): continue
				if dataTempCur[QDate][mod][0]<limitsTIB[block][QDate][i][0]: continue
				if dataTempCur[QDate][mod][0]>limitsTIB[block][QDate][i][1]: continue
				#if dataTempCur[QDate][mod][0]<0.: continue
				#if dataTempCur[QDate][mod][0]>2000.: continue
				if dataTempCur[QDate][mod][1]<-20: continue
				if dataTempCur[QDate][mod][1]>50: continue
				fluence.append(sum(fluence_t[mod][:QuerrDays[QDate]+1]))
				current.append(dataTempCur[QDate][mod][0])
				indAfter+=1
			print QDate,indBefore,indAfter 
		print len(fluence),len(current)#,len(outliers[QDate])
		grs[block][i] = TGraph(len(fluence),array('d',fluence),array('d',current))
		grs[block][i].SetMarkerColor(4)
		grs[block][i].SetLineColor(4)
		grs[block][i].SetLineStyle(1)
		grs[block][i].SetLineWidth(6)
		grs[block][i].SetMarkerStyle(7)
		grs[block][i].SetMarkerSize(0.3)
		canvs[block][i] = TCanvas(block+"_"+str(i),block+"_"+str(i),800,600)
		gStyle.SetFillColor(kWhite)
		canvs[block][i].SetGrid()
		grs[block][i].Draw("AP")
		#if block=='block5': Fits[block].SetParLimits(0, -100, 0)
		grs[block][i].Fit(Fits[block],"B")
		#grs[block][i].Fit("pol1","F")
		grs[block][i].SetTitle('TIB (Layer '+str(i)+') -- '+block)
		grs[block][i].GetXaxis().SetTitle('Fluence (cm^{-2})')#x10^{6}cm^{-2})')
		grs[block][i].GetYaxis().SetTitle('Current (#muA/cm^{3}) 0C')
		effAlpha[block][i] = grs[block][i].GetFunction("fit_"+block).GetParameter(1)
		par0[block][i] = grs[block][i].GetFunction("fit_"+block).GetParameter(0)
		print effAlpha[block][i],par0[block][i]
		canvs[block][i].SaveAs("DarkSimAllModules_"+simDate+"/plotLayers_effAlpha/layerFits/TIB_"+block+"_L"+str(i)+".png")
	for i in range(1,7):
		fluence=[]
		current=[]
		for QDate in fitDates[block]:
			indBefore=0
			indAfter =0
			for mod in dataTempCur[QDate].keys():
				if pos[mod]!=i: continue
				if 'TOB' not in part[mod]: continue
				indBefore+=1
				if mod not in fluence_t.keys(): continue
				if dataTempCur[QDate][mod][0]<limitsTOB[block][QDate][i][0]: continue
				if dataTempCur[QDate][mod][0]>limitsTOB[block][QDate][i][1]: continue
				#if dataTempCur[QDate][mod][0]<0.: continue
				#if dataTempCur[QDate][mod][0]>2000.: continue
				if dataTempCur[QDate][mod][1]<-20: continue
				if dataTempCur[QDate][mod][1]>50: continue
				fluence.append(sum(fluence_t[mod][:QuerrDays[QDate]+1]))
				current.append(dataTempCur[QDate][mod][0])
				indAfter+=1
			print QDate,indBefore,indAfter 
		print len(fluence),len(current)#,len(outliers[QDate])
		grs[block][i+4] = TGraph(len(fluence),array('d',fluence),array('d',current))
		grs[block][i+4].SetMarkerColor(4)
		grs[block][i+4].SetLineColor(4)
		grs[block][i+4].SetLineStyle(1)
		grs[block][i+4].SetLineWidth(6)
		grs[block][i+4].SetMarkerStyle(7)
		grs[block][i+4].SetMarkerSize(0.3)
		canvs[block][i+4] = TCanvas(block+"_"+str(i+4),block+"_"+str(i+4),800,600)
		gStyle.SetFillColor(kWhite)
		canvs[block][i+4].SetGrid()
		grs[block][i+4].Draw("AP")
		grs[block][i+4].Fit(Fits[block],"B")
		#grs[block][i+4].Fit("pol1","F")
		grs[block][i+4].SetTitle('TOB (Layer '+str(i)+') -- '+block)
		grs[block][i+4].GetXaxis().SetTitle('Fluence (cm^{-2})')#x10^{6}cm^{-2})')
		grs[block][i+4].GetYaxis().SetTitle('Current (#muA/cm^{3}) 0C')
		effAlpha[block][i+4] = grs[block][i+4].GetFunction("fit_"+block).GetParameter(1)
		par0[block][i+4] = grs[block][i+4].GetFunction("fit_"+block).GetParameter(0)
		print effAlpha[block][i+4],par0[block][i+4]
		canvs[block][i+4].SaveAs("DarkSimAllModules_"+simDate+"/plotLayers_effAlpha/layerFits/TOB_"+block+"_L"+str(i)+".png")
	qdateInd+=1

fitLumiVals = {}
indTemp = 0
for block in fitDates.keys():
	for QDate in fitDates[block]:
		qday   = QDate[:2]
		qmonth = QDate[3:5]
		qyear  = QDate[6:]
		date = int(qyear+qmonth+qday)
		fitLumiVals[QDate] = lumiAll[dtime_t_temp.index(date)]
	
runDir=os.getcwd()

def binarySearch(data, val):
    lo, hi = 0, len(data) - 1
    best_ind = lo
    while lo <= hi:
        mid = lo + (hi - lo) / 2
        if data[mid] < val:
            lo = mid + 1
        elif data[mid] > val:
            hi = mid - 1
        else:
            best_ind = mid
            break
        # check if data[mid] is closer to val than data[best_ind] 
        if abs(data[mid] - val) < abs(data[best_ind] - val):
            best_ind = mid
    return best_ind

def getTGraph(modPart,layer,color):
	Ion=[0]*len(dtime_t)
	IonData=[0]*len(dtime_t)
	nModsInLayer=0
	for mod in part.keys():
		if modPart not in part[mod]: continue
		if layer!=pos[mod]: continue
		if mod not in ileakc_t_on.keys(): continue
		#print part[mod],pos[mod]
		#print ileakc_t_on[mod][1650:1710]
		isCurrentNaN = [math.isnan(item) for item in ileakc_t_on[mod]]
		if any(isCurrentNaN): 
			print "Current values NaN:",mod
			continue
		fluency=0.
		for day in range(len(dtime_t)):
			Ion[day]+=ileakc_t_on[mod][day]
			fluency+=fluence_t[mod][day]
			if TDatime(int(dtime_t[day])).GetDate()<20111023: IonData[day]+=effAlpha['block1'][layer+4]*fluency+par0['block1'][layer+4]
			elif TDatime(int(dtime_t[day])).GetDate()<20120618: IonData[day]+=effAlpha['block2'][layer+4]*fluency+par0['block2'][layer+4]
			elif TDatime(int(dtime_t[day])).GetDate()<20120909: IonData[day]+=effAlpha['block3'][layer+4]*fluency+par0['block3'][layer+4]
			elif TDatime(int(dtime_t[day])).GetDate()<20121205: IonData[day]+=effAlpha['block4'][layer+4]*fluency+par0['block4'][layer+4]
			else: IonData[day]+=effAlpha['block5'][layer+4]*fluency+par0['block5'][layer+4]
		#Ion=[a+b for a,b in zip(Ion,ileakc_t_on[mod])]
		#IonData=[a+effAlpha*b for a,b in zip(IonData,fluence_t[mod])]
		nModsInLayer+=1
	Ion = [item/nModsInLayer for item in Ion]
	IonData = [item/nModsInLayer for item in IonData]
	iper=dtime_t

	IGr_sim = TGraph(len(iper),array('d',iper),array('d',Ion))
	IGr_sim.SetMarkerColor(color)
	IGr_sim.SetLineColor(color)
	IGr_sim.SetLineStyle(1)
	IGr_sim.SetLineWidth(6)
	IGr_sim.SetMarkerStyle(7)
	IGr_sim.SetMarkerSize(0.3)
	IGr_vs_lumi_sim = TGraph(len(iper),array('d',lumiAll),array('d',Ion))
	IGr_vs_lumi_sim.SetMarkerColor(color)
	IGr_vs_lumi_sim.SetLineColor(color)
	IGr_vs_lumi_sim.SetLineStyle(1)
	IGr_vs_lumi_sim.SetLineWidth(3)
	IGr_vs_lumi_sim.SetMarkerStyle(7)
	IGr_vs_lumi_sim.SetMarkerSize(0.4)

	IGr_data = TGraph(len(iper),array('d',iper),array('d',IonData))
	IGr_data.SetMarkerColor(color)
	IGr_data.SetLineColor(color)
	IGr_data.SetLineStyle(1)
	IGr_data.SetLineWidth(3)
	IGr_data.SetMarkerStyle(7)
	IGr_data.SetMarkerSize(0.3)
	IGr_vs_lumi_data = TGraph(len(iper),array('d',lumiAll),array('d',IonData))
	IGr_vs_lumi_data.SetMarkerColor(color)
	IGr_vs_lumi_data.SetLineColor(color)
	IGr_vs_lumi_data.SetLineStyle(1)
	IGr_vs_lumi_data.SetLineWidth(3)
	IGr_vs_lumi_data.SetMarkerStyle(7)
	IGr_vs_lumi_data.SetMarkerSize(0.3)
	return IGr_sim,IGr_data,IGr_vs_lumi_sim,IGr_vs_lumi_data

print "Doing TOB_L1"
L1gr_sim, L1gr_data, L1gr_vs_lumi_sim, L1gr_vs_lumi_data = getTGraph("TOB",1,kBlack)
print "Doing TOB_L2"
L2gr_sim, L2gr_data, L2gr_vs_lumi_sim, L2gr_vs_lumi_data = getTGraph("TOB",2,kRed)
print "Doing TOB_L3"
L3gr_sim, L3gr_data, L3gr_vs_lumi_sim, L3gr_vs_lumi_data = getTGraph("TOB",3,kBlue)
print "Doing TOB_L4"
L4gr_sim, L4gr_data, L4gr_vs_lumi_sim, L4gr_vs_lumi_data = getTGraph("TOB",4,kGreen)
print "Doing TOB_L5"
L5gr_sim, L5gr_data, L5gr_vs_lumi_sim, L5gr_vs_lumi_data = getTGraph("TOB",5,kCyan)
print "Doing TOB_L6"
L6gr_sim, L6gr_data, L6gr_vs_lumi_sim, L6gr_vs_lumi_data = getTGraph("TOB",6,kMagenta)

if not os.path.exists(runDir+'/DarkSimAllModules_'+simDate+'/plotLayers_effAlpha/'): os.system('mkdir DarkSimAllModules_'+simDate+'/plotLayers_effAlpha/')
outRfile = TFile("DarkSimAllModules_"+simDate+"/plotLayers_effAlpha/TOB_avgOverLayer.root",'RECREATE')
L1gr_sim.Write()
L2gr_sim.Write()
L3gr_sim.Write()
L4gr_sim.Write()
L5gr_sim.Write()
L6gr_sim.Write()
L1gr_data.Write()
L2gr_data.Write()
L3gr_data.Write()
L4gr_data.Write()
L5gr_data.Write()
L6gr_data.Write()
L1gr_vs_lumi_sim.Write()
L2gr_vs_lumi_sim.Write()
L3gr_vs_lumi_sim.Write()
L4gr_vs_lumi_sim.Write()
L5gr_vs_lumi_sim.Write()
L6gr_vs_lumi_sim.Write()
L1gr_vs_lumi_data.Write()
L2gr_vs_lumi_data.Write()
L3gr_vs_lumi_data.Write()
L4gr_vs_lumi_data.Write()
L5gr_vs_lumi_data.Write()
L6gr_vs_lumi_data.Write()
	
XaxisnameI = "Date"
YaxisnameI = "Current [#muA/cm^{3}] @0^{0}C"

mgnI = TMultiGraph()
mgnI.SetTitle("Simulated data for TOB")#+str(QuerrMod)+" ("+modPart+")")
mgnI.Add(L1gr_sim,"p")
mgnI.Add(L2gr_sim,"p")
mgnI.Add(L3gr_sim,"p")
mgnI.Add(L4gr_sim,"p")
mgnI.Add(L5gr_sim,"p")
mgnI.Add(L6gr_sim,"p")
mgnI.Add(L1gr_data,"l")
mgnI.Add(L2gr_data,"l")
mgnI.Add(L3gr_data,"l")
mgnI.Add(L4gr_data,"l")
mgnI.Add(L5gr_data,"l")
mgnI.Add(L6gr_data,"l")

cI = TCanvas("Module_I","Module_I",800,400)
gStyle.SetFillColor(kWhite)

cI.SetGrid()
mgnI.Draw("AP")
mgnI.GetXaxis().SetTimeDisplay(1)
mgnI.GetXaxis().SetNdivisions(-503)
mgnI.GetXaxis().SetTimeFormat("%Y-%m-%d")
mgnI.GetXaxis().SetTimeOffset(0,"gmt")
mgnI.GetXaxis().SetTitle(XaxisnameI)
mgnI.GetYaxis().SetTitle(YaxisnameI)
mgnI.GetXaxis().SetLimits(min(dtime_t),max(dtime_t))
mgnI.GetHistogram().SetMinimum(0)#min(Ion))
#mgnI.GetHistogram().SetMaximum(1.2*max(max(ileakc_t_on[L1Mod][5:-5]),max(ileakc_t_on[L2Mod][5:-5]),max(ileakc_t_on[L3Mod][5:-5]),max(ileakc_t_on[L4Mod][5:-5]))*LeakCorrection(273.16,293.16))#2.25*max(Ion))
#mgnI.GetYaxis().SetTitleOffset(1.5)
x1=0.15#.7
y2=.875
x2=x1+.13
y1=y2-.375
legI = TLegend(x1,y1,x2,y2)
legI.AddEntry(L1gr_sim,"Layer 1","pl")
legI.AddEntry(L2gr_sim,"Layer 2","pl")
legI.AddEntry(L3gr_sim,"Layer 3","pl")
legI.AddEntry(L4gr_sim,"Layer 4","pl")
legI.AddEntry(L5gr_sim,"Layer 5","pl")
legI.AddEntry(L6gr_sim,"Layer 6","pl")
legI.SetTextFont(10)
legI.Draw()

cI.Write()
saveNameI = "DarkSimAllModules_"+simDate+"/plotLayers_effAlpha/TOB_Ileak"
cI.SaveAs(saveNameI+"_avgOverLayer.png")
cI.SaveAs(saveNameI+"_avgOverLayer.pdf")

grsForLumiTOB = {}
for date in fitLumiVals.keys():
	fluence = [fitLumiVals[date],fitLumiVals[date]]
	current = [0,14.5]
	grsForLumiTOB[date] = TGraph(len(fluence),array('d',fluence),array('d',current))
	grsForLumiTOB[date].SetMarkerColor(1)
	grsForLumiTOB[date].SetLineColor(1)
	grsForLumiTOB[date].SetLineStyle(2)
	grsForLumiTOB[date].SetLineWidth(3)

mgnIvsLumi = TMultiGraph()
mgnIvsLumi.SetTitle("TOB")
mgnIvsLumi.Add(L1gr_vs_lumi_sim,"p")
mgnIvsLumi.Add(L2gr_vs_lumi_sim,"p")
mgnIvsLumi.Add(L3gr_vs_lumi_sim,"p")
mgnIvsLumi.Add(L4gr_vs_lumi_sim,"p")
mgnIvsLumi.Add(L5gr_vs_lumi_sim,"p")
mgnIvsLumi.Add(L6gr_vs_lumi_sim,"p")
mgnIvsLumi.Add(L1gr_vs_lumi_data,"l")
mgnIvsLumi.Add(L2gr_vs_lumi_data,"l")
mgnIvsLumi.Add(L3gr_vs_lumi_data,"l")
mgnIvsLumi.Add(L4gr_vs_lumi_data,"l")
mgnIvsLumi.Add(L5gr_vs_lumi_data,"l")
mgnIvsLumi.Add(L6gr_vs_lumi_data,"l")
for date in grsForLumiTOB.keys(): mgnIvsLumi.Add(grsForLumiTOB[date],"l")
	
cIvsLumi = TCanvas("Module_I_vs_Lumi","Module_I_vs_Lumi",800,400)
gStyle.SetFillColor(kWhite)

cIvsLumi.SetGrid()
mgnIvsLumi.Draw("AP")
mgnIvsLumi.GetXaxis().SetTitle("Integrated Luminosity [fb^{-1}]")
mgnIvsLumi.GetYaxis().SetTitle(YaxisnameI)
mgnIvsLumi.GetXaxis().SetLimits(0,35)
mgnIvsLumi.GetHistogram().SetMinimum(0)#min(Ion))
#mgnIvsLumi.GetHistogram().SetMaximum(1.2*max(max(ileakc_t_on[L1Mod][5:-5]),max(ileakc_t_on[L2Mod][5:-5]),max(ileakc_t_on[L3Mod][5:-5]),max(ileakc_t_on[L4Mod][5:-5]))*LeakCorrection(273.16,293.16))#2.25*max(Ion))

legIvsLumi = TLegend(x1,y1,x2,y2)
legIvsLumi.AddEntry(L1gr_vs_lumi_sim,"Layer 1","pl")
legIvsLumi.AddEntry(L2gr_vs_lumi_sim,"Layer 2","pl")
legIvsLumi.AddEntry(L3gr_vs_lumi_sim,"Layer 3","pl")
legIvsLumi.AddEntry(L4gr_vs_lumi_sim,"Layer 4","pl")
legIvsLumi.AddEntry(L5gr_vs_lumi_sim,"Layer 5","pl")
legIvsLumi.AddEntry(L6gr_vs_lumi_sim,"Layer 6","pl")
legIvsLumi.SetTextFont(10)
legIvsLumi.Draw()

cIvsLumi.Write()
cIvsLumi.SaveAs(saveNameI+"_vs_lumi_avgOverLayer.png")
cIvsLumi.SaveAs(saveNameI+"_vs_lumi_avgOverLayer.pdf")

print "Doing TIB_L1"
L1gr_sim_tib, L1gr_data_tib, L1gr_vs_lumi_sim_tib, L1gr_vs_lumi_data_tib = getTGraph("TIB",1,kBlack)
print "Doing TIB_L2"
L2gr_sim_tib, L2gr_data_tib, L2gr_vs_lumi_sim_tib, L2gr_vs_lumi_data_tib = getTGraph("TIB",2,kRed)
print "Doing TIB_L3"
L3gr_sim_tib, L3gr_data_tib, L3gr_vs_lumi_sim_tib, L3gr_vs_lumi_data_tib = getTGraph("TIB",3,kBlue)
print "Doing TIB_L4"
L4gr_sim_tib, L4gr_data_tib, L4gr_vs_lumi_sim_tib, L4gr_vs_lumi_data_tib = getTGraph("TIB",4,kGreen)

if not os.path.exists(runDir+'/DarkSimAllModules_'+simDate+'/plotLayers_effAlpha/'): os.system('mkdir DarkSimAllModules_'+simDate+'/plotLayers_effAlpha/')
outRfile_tib = TFile("DarkSimAllModules_"+simDate+"/plotLayers_effAlpha/TIB_avgOverLayer.root",'RECREATE')
L1gr_sim_tib.Write()
L2gr_sim_tib.Write()
L3gr_sim_tib.Write()
L4gr_sim_tib.Write()
L1gr_data_tib.Write()
L2gr_data_tib.Write()
L3gr_data_tib.Write()
L4gr_data_tib.Write()
L1gr_vs_lumi_sim_tib.Write()
L2gr_vs_lumi_sim_tib.Write()
L3gr_vs_lumi_sim_tib.Write()
L4gr_vs_lumi_sim_tib.Write()
L1gr_vs_lumi_data_tib.Write()
L2gr_vs_lumi_data_tib.Write()
L3gr_vs_lumi_data_tib.Write()
L4gr_vs_lumi_data_tib.Write()
	
XaxisnameI = "Date"
YaxisnameI = "Current [#muA/cm^{3}] @0^{0}C"

mgnI_tib = TMultiGraph()
mgnI_tib.SetTitle("Simulated data for TIB")#+str(QuerrMod)+" ("+modPart+")")
mgnI_tib.Add(L1gr_sim_tib,"p")
mgnI_tib.Add(L2gr_sim_tib,"p")
mgnI_tib.Add(L3gr_sim_tib,"p")
mgnI_tib.Add(L4gr_sim_tib,"p")
mgnI_tib.Add(L1gr_data_tib,"l")
mgnI_tib.Add(L2gr_data_tib,"l")
mgnI_tib.Add(L3gr_data_tib,"l")
mgnI_tib.Add(L4gr_data_tib,"l")

cI_tib = TCanvas("Module_I_tib","Module_I_tib",800,400)
gStyle.SetFillColor(kWhite)

cI_tib.SetGrid()
mgnI_tib.Draw("AP")
mgnI_tib.GetXaxis().SetTimeDisplay(1)
mgnI_tib.GetXaxis().SetNdivisions(-503)
mgnI_tib.GetXaxis().SetTimeFormat("%Y-%m-%d")
mgnI_tib.GetXaxis().SetTimeOffset(0,"gmt")
mgnI_tib.GetXaxis().SetTitle(XaxisnameI)
mgnI_tib.GetYaxis().SetTitle(YaxisnameI)
mgnI_tib.GetXaxis().SetLimits(min(dtime_t),max(dtime_t))
mgnI_tib.GetHistogram().SetMinimum(0)#min(Ion))
#mgnI.GetHistogram().SetMaximum(1.2*max(max(ileakc_t_on[L1Mod][5:-5]),max(ileakc_t_on[L2Mod][5:-5]),max(ileakc_t_on[L3Mod][5:-5]),max(ileakc_t_on[L4Mod][5:-5]))*LeakCorrection(273.16,293.16))#2.25*max(Ion))
#mgnI.GetYaxis().SetTitleOffset(1.5)
y1=y2-.275
legI_tib = TLegend(x1,y1,x2,y2)
legI_tib.AddEntry(L1gr_sim,"Layer 1","pl")
legI_tib.AddEntry(L2gr_sim,"Layer 2","pl")
legI_tib.AddEntry(L3gr_sim,"Layer 3","pl")
legI_tib.AddEntry(L4gr_sim,"Layer 4","pl")
legI_tib.SetTextFont(10)
legI_tib.Draw()

cI_tib.Write()
saveNameI = "DarkSimAllModules_"+simDate+"/plotLayers_effAlpha/TIB_Ileak"
cI_tib.SaveAs(saveNameI+"_avgOverLayer.png")
cI_tib.SaveAs(saveNameI+"_avgOverLayer.pdf")

grsForLumiTIB = {}
for date in fitLumiVals.keys():
	fluence = [fitLumiVals[date],fitLumiVals[date]]
	current = [0,50]
	grsForLumiTIB[date] = TGraph(len(fluence),array('d',fluence),array('d',current))
	grsForLumiTIB[date].SetMarkerColor(1)
	grsForLumiTIB[date].SetLineColor(1)
	grsForLumiTIB[date].SetLineStyle(2)
	grsForLumiTIB[date].SetLineWidth(3)

mgnIvsLumi_tib = TMultiGraph()
mgnIvsLumi_tib.SetTitle("TIB")
mgnIvsLumi_tib.Add(L1gr_vs_lumi_sim_tib,"p")
mgnIvsLumi_tib.Add(L2gr_vs_lumi_sim_tib,"p")
mgnIvsLumi_tib.Add(L3gr_vs_lumi_sim_tib,"p")
mgnIvsLumi_tib.Add(L4gr_vs_lumi_sim_tib,"p")
mgnIvsLumi_tib.Add(L1gr_vs_lumi_data_tib,"l")
mgnIvsLumi_tib.Add(L2gr_vs_lumi_data_tib,"l")
mgnIvsLumi_tib.Add(L3gr_vs_lumi_data_tib,"l")
mgnIvsLumi_tib.Add(L4gr_vs_lumi_data_tib,"l")
for date in grsForLumiTIB.keys(): mgnIvsLumi_tib.Add(grsForLumiTIB[date],"l")

cIvsLumi_tib = TCanvas("Module_I_vs_Lumi_tib","Module_I_vs_Lumi_tib",800,400)
gStyle.SetFillColor(kWhite)

cIvsLumi_tib.SetGrid()
mgnIvsLumi_tib.Draw("AP")
mgnIvsLumi_tib.GetXaxis().SetTitle("Integrated Luminosity [fb^{-1}]")
mgnIvsLumi_tib.GetYaxis().SetTitle(YaxisnameI)
mgnIvsLumi_tib.GetXaxis().SetLimits(0,35)
mgnIvsLumi_tib.GetHistogram().SetMinimum(0)#min(Ion))
#mgnIvsLumi.GetHistogram().SetMaximum(1.2*max(max(ileakc_t_on[L1Mod][5:-5]),max(ileakc_t_on[L2Mod][5:-5]),max(ileakc_t_on[L3Mod][5:-5]),max(ileakc_t_on[L4Mod][5:-5]))*LeakCorrection(273.16,293.16))#2.25*max(Ion))
#mgnI.GetYaxis().SetTitleOffset(1.5)

legIvsLumi_tib = TLegend(x1,y1,x2,y2)
legIvsLumi_tib.AddEntry(L1gr_vs_lumi_sim_tib,"Layer 1","pl")
legIvsLumi_tib.AddEntry(L2gr_vs_lumi_sim_tib,"Layer 2","pl")
legIvsLumi_tib.AddEntry(L3gr_vs_lumi_sim_tib,"Layer 3","pl")
legIvsLumi_tib.AddEntry(L4gr_vs_lumi_sim_tib,"Layer 4","pl")
legIvsLumi_tib.SetTextFont(10)
legIvsLumi_tib.Draw()

cIvsLumi_tib.Write()
cIvsLumi_tib.SaveAs(saveNameI+"_vs_lumi_avgOverLayer.png")
cIvsLumi_tib.SaveAs(saveNameI+"_vs_lumi_avgOverLayer.pdf")

outRfile.Close()	
outRfile_tib.Close()
RFile.Close()

print "***************************** DONE *********************************" 
