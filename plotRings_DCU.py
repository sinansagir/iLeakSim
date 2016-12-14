#!/usr/bin/python

import os,sys,fnmatch,math,pickle
from bisect import bisect_left
from array import array
import numpy as np
from ROOT import *
gROOT.SetBatch(1)

##################################################################################################################
# The code looks for the input simulation tree in "DarkSimAllModules_<simDate>/DarkSimAllModules_<simDate>.root"
# The output files will be in "DarkSimAllModules_<simDate>/plotSingleModules/". 
##################################################################################################################

# psudata = open('MeasData/PSU/TIBminus_4_3_1_4.txt', 'r')
# linespsu = psudata.readlines()
# psudata.close()
# for line in linespsu:
# 	data = line.strip().split()
# 	print TDatime(int(data[0])).GetDate(),data[1]
# os._exit(1)

#******************************Input to edit******************************************************
simDate = "2016_12_6"
readTree=False # This needs to be true if running the code on the tree for the first time. It will dump what's read from tree into pickle files and these can be loaded if this option is set to "False"
readDCU=True
doFit=False

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
	print "-Loading detector ids ... "
	detid_t=pickle.load(open("DarkSimAllModules_"+simDate+'/detid_t.p','rb'))
	print "                          done"
	print "-Loading partitions ... "
	partition_t=pickle.load(open("DarkSimAllModules_"+simDate+'/partition_t.p','rb'))
	print "                        done"
	print "-Loading time ... "
	dtime_t=pickle.load(open("DarkSimAllModules_"+simDate+'/dtime_t.p','rb'))
	print "                  done"
	print "-Loading temperature ... "
	temp_t_on=pickle.load(open("DarkSimAllModules_"+simDate+'/temp_t_on.p','rb'))
	print "                         done"
	print "-Loading leakage current ... "
	ileakc_t_on=pickle.load(open("DarkSimAllModules_"+simDate+'/ileakc_t_on.p','rb'))
	print "                             done"
	print "-Loading fluence ... "
	fluence_t=pickle.load(open("DarkSimAllModules_"+simDate+'/fluence_t.p','rb'))
	print "                     done"
	print "******************* LOADED TREE FROM PICKLE ********************"

print "========>>>>>>>> READING TRACKER MAP"
TrackMap="InputDataLocal/TrackMap.root"
TrackMapRFile = TFile(TrackMap,'READ')
TrackMapTTree = TrackMapRFile.Get('treemap')
x,y,z,l,w1,w2,d,part,pos = {},{},{},{},{},{},{},{},{}
volume = {}
dcuileak = {}
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
	dcuileak[event.DETID] = [-1]*len(dtime_t)
TrackMapRFile.Close()

infileRing = open('InputDataLocal/tracker.dat', 'r')
linesRing = infileRing.readlines()
infileRing.close()
ring = {}
for line in linesRing:
	data = line.strip().split()
	if 'TEC' in data[0] or 'TID' in data[0]:
		ring[int(data[-1][1:-1])]=int(data[data.index('Ring')+1])
	else: ring[int(data[-1][1:-1])]=-1
	
print "========>>>>>>>> FINISHED READING TRACKER MAP"

print "========>>>>>>>> READING FLUENCE MATCHING"
TFileFluence = TFile("InputDataLocal/FluenceMatching.root",'READ')
TTreeFluence = TFileFluence.Get("SimTree_old")
fluenceNew = {}
for module in TTreeFluence:
	fluenceNew[module.DETID_T] = module.FINFLU_T # new algo
TFileFluence.Close()
print "========>>>>>>>> FINISHED READING FLUENCE MATCHING"

# Read Input Data for Lumi
lumiFile = "InputDataLocal/lumi/Lumi.txt"
infileLumi = open(lumiFile, 'r')
print "Reading Lumi File"
linesLumi = infileLumi.readlines()
infileLumi.close()
lumiAll=[]
lumiPerDay=[]
IntLum=0.
IntLumR1=0.
dtime_t_2 = [TDatime(int(item)).GetDate() for item in dtime_t]
# print dtime_t_2
# os._exit(1)
dtime_t = [int(item) for item in dtime_t]
for i in range(len(linesLumi)):
	data = linesLumi[i].strip().split()
	try: 
		IntLum+=float(data[2])/1e6 # in INVFB
		#if int(data[1]) in dtime_t:
		if int(data[0].split('/')[2]+data[0].split('/')[1]+data[0].split('/')[0]) in dtime_t_2:
			lumiAll.append(IntLum)
			lumiPerDay.append(float(data[2]))
			if data[0]=='01/01/2013':IntLumR1=IntLum
	except: print "Warning! => Unknown data format: ",data,"in",lumiFile
print "Total Integrated Lumi:",lumiAll[-1]
print "Total Integrated Lumi Run1:",IntLumR1
print "Total Integrated Lumi Run2:",lumiAll[-1]-IntLumR1

print "Adding missing fluences!"
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

def findfiles(path, filtre):
    for root, dirs, files in os.walk(path):
        for f in fnmatch.filter(files, filtre):
            yield os.path.join(root, f)

def findClosest(theList, theNum): #Assumes theList is sorted and returns the closest value to theNum
    theInd = bisect_left(theList, theNum)
    if theInd == len(theList):
        return theInd-1
    if theList[theInd] - theNum < theNum - theList[theInd - 1]:
       return theInd
    else:
       return theInd-1

dcufiles = []
for file in findfiles('MeasDataLocal/DCU/Ileak_perDay', '*.txt'):
	dcufiles.append(file)

if readDCU:
	ind = 0
	print "Reading DCU data ..."
	for file in dcufiles:
		if ind%500==0: print "Finished",ind,"out of",len(dcufiles)
		ind+=1
		#if 'TIB' not in file.split('/')[-1] and 'TOB' not in file.split('/')[-1]: continue
		dcudata = open(file, 'r')
		linesdcu = dcudata.readlines()
		dcudata.close()
		mod=int(file.split('/')[-1][:-4])
		for line in linesdcu:
			data = line.strip().split()
			lnxTime = int(data[0])
			index = findClosest(dtime_t_2,TDatime(lnxTime).GetDate())
			modIleak = float(data[1])
			dcuileak[mod][index]=modIleak
	print "Damping DCU data into pickle ..."
	#pickle.dump(dcuileak,open("DarkSimAllModules_"+simDate+'/dcuileak.p','wb'))
else:
	print "Loading DCU data from pickle ..."
	dcuileak=pickle.load(open("DarkSimAllModules_"+simDate+'/dcuileak.p','rb'))

k_B = 8.617343183775136189e-05
def LeakCorrection(Tref,T):
	E = 1.21 # formerly 1.12 eV
	return (Tref/T)*(Tref/T)*math.exp(-(E/(2.*k_B))*(1./Tref-1./T))

print "========>>>>>>>> SCALING CURRENT TO 0C and AVERAGING"
for mod in ileakc_t_on.keys():
	ileakc_t_on[mod]=[item*LeakCorrection(273.16,293.16)*1.e3/volume[mod] for item in ileakc_t_on[mod]] #muA/cm^3 @0C
	dcuileak[mod]=[dcuileak[mod][ind]*LeakCorrection(273.16,temp_t_on[mod][ind])*1.e3/volume[mod] for ind in range(len(dcuileak[mod]))] #muA/cm^3 @0C

runDir=os.getcwd()
regions = {
		   '0': [0,5.8],
		   '1': [6.1,21],
		   '2': [30.2,34],
		   '3': [36,50],
		   '4': [53,67],
		   '5': [69,75]
		   }
datFits = {}
simFits = {}

def getTGraph(modPart,layer,color):
	Ion=[0]*len(dtime_t)
	nModsInLayer=0
	for mod in part.keys():
		if modPart not in part[mod]: continue
		if ring[mod]!=layer: continue
		if mod not in ileakc_t_on.keys(): continue
		for day in range(len(dtime_t)):
			Ion[day]+=ileakc_t_on[mod][day]
		nModsInLayer+=1
	Ion = [item/nModsInLayer for item in Ion]
	IonData=[]#[-1]*len(dtime_t)
	iperData=[]
	lumiAllData=[]
	for t in range(len(dtime_t_2)):
		leakTemppp = 0
		nMods = 0
		for mod in part.keys():
			if modPart not in part[mod]: continue
			if ring[mod]!=layer: continue
			if dcuileak[mod][t]>0:
				leakTemppp+=dcuileak[mod][t]
				nMods+=1
		if nMods!=0: 
			#IonData[t]=leakTemppp/nMods
			IonData.append(leakTemppp/nMods)
			iperData.append(dtime_t[t])
			lumiAllData.append(lumiAll[t])
	iper=dtime_t

	IGr_sim = TGraph(len(iper),array('d',iper),array('d',Ion))
	IGr_sim.SetMarkerColor(color)
	IGr_sim.SetLineColor(color)
	IGr_sim.SetLineStyle(1)
	IGr_sim.SetLineWidth(3)
	IGr_sim.SetMarkerStyle(7)
	IGr_sim.SetMarkerSize(0.3)
	IGr_vs_lumi_sim = TGraph(len(iper),array('d',lumiAll),array('d',Ion))
	IGr_vs_lumi_sim.SetMarkerColor(color)
	IGr_vs_lumi_sim.SetLineColor(color)
	IGr_vs_lumi_sim.SetLineStyle(1)
	IGr_vs_lumi_sim.SetLineWidth(3)
	IGr_vs_lumi_sim.SetMarkerStyle(7)
	IGr_vs_lumi_sim.SetMarkerSize(0.6)
	
	IGr_data = TGraph(len(iperData),array('d',iperData),array('d',IonData))
	IGr_data.SetMarkerColor(color)
	IGr_data.SetLineColor(color)
	IGr_data.SetLineStyle(1)
	IGr_data.SetLineWidth(3)
	IGr_data.SetMarkerStyle(2)
	IGr_data.SetMarkerSize(0.9)
	IGr_vs_lumi_data = TGraph(len(iperData),array('d',lumiAllData),array('d',IonData))
	IGr_vs_lumi_data.SetMarkerColor(color)
	IGr_vs_lumi_data.SetLineColor(color)
	IGr_vs_lumi_data.SetLineStyle(1)
	IGr_vs_lumi_data.SetLineWidth(3)
	IGr_vs_lumi_data.SetMarkerStyle(2)
	IGr_vs_lumi_data.SetMarkerSize(0.9)
	if doFit:
		lines = {}
		datFits[modPart+str(layer)] = []
		simFits[modPart+str(layer)] = []
		for reg in sorted(regions.keys()):
			lines[reg] = TF1("line"+reg,"pol1",regions[reg][0],regions[reg][1])
			IGr_vs_lumi_data.Fit("line"+reg,"RS")
			try: datFits[modPart+str(layer)].append([lines[reg].GetParameter(0),lines[reg].GetParameter(1)])
			except: datFits[modPart+str(layer)].append([-999,-999])
		
			IGr_vs_lumi_sim.Fit("line"+reg,"RS")
			try: simFits[modPart+str(layer)].append([lines[reg].GetParameter(0),lines[reg].GetParameter(1)])
			except: simFits[modPart+str(layer)].append([-999,-999])
	
	return IGr_sim,IGr_data,IGr_vs_lumi_sim,IGr_vs_lumi_data
	
print "Doing TEC_R1"
L1gr_sim, L1gr_data, L1gr_vs_lumi_sim, L1gr_vs_lumi_data = getTGraph("TEC",1,kBlack)
print "Doing TEC_R2"
L2gr_sim, L2gr_data, L2gr_vs_lumi_sim, L2gr_vs_lumi_data = getTGraph("TEC",2,kRed)
print "Doing TEC_R3"
L3gr_sim, L3gr_data, L3gr_vs_lumi_sim, L3gr_vs_lumi_data = getTGraph("TEC",3,kBlue)
print "Doing TEC_R4"
L4gr_sim, L4gr_data, L4gr_vs_lumi_sim, L4gr_vs_lumi_data = getTGraph("TEC",4,kGreen)
print "Doing TEC_R5"
L5gr_sim, L5gr_data, L5gr_vs_lumi_sim, L5gr_vs_lumi_data = getTGraph("TEC",5,kCyan)
print "Doing TEC_R6"
L6gr_sim, L6gr_data, L6gr_vs_lumi_sim, L6gr_vs_lumi_data = getTGraph("TEC",6,kMagenta)
print "Doing TEC_R7"
L7gr_sim, L7gr_data, L7gr_vs_lumi_sim, L7gr_vs_lumi_data = getTGraph("TEC",7,kYellow)

dmmy_gr_sim = TGraph(len([1294120800,1294207200]),array('d',[1294120800,1294207200]),array('d',[-99,-100]))
dmmy_gr_sim.SetMarkerColor(kBlack)
dmmy_gr_sim.SetLineColor(kBlack)
dmmy_gr_sim.SetLineStyle(1)
dmmy_gr_sim.SetLineWidth(3)
dmmy_gr_sim.SetMarkerStyle(7)
dmmy_gr_sim.SetMarkerSize(0.6)
dmmy_gr_dat = TGraph(len([1294120800,1294207200]),array('d',[1294120800,1294207200]),array('d',[-99,-100]))
dmmy_gr_dat.SetMarkerColor(kBlack)
dmmy_gr_dat.SetLineColor(kBlack)
dmmy_gr_dat.SetLineStyle(1)
dmmy_gr_dat.SetLineWidth(3)
dmmy_gr_dat.SetMarkerStyle(2)
dmmy_gr_dat.SetMarkerSize(2.)

if not os.path.exists(runDir+'/DarkSimAllModules_'+simDate+'/plotRings_DCU/'): os.system('mkdir DarkSimAllModules_'+simDate+'/plotRings_DCU/')
outRfile = TFile("DarkSimAllModules_"+simDate+"/plotRings_DCU/TEC_avgOverRing.root",'RECREATE')
L1gr_sim.Write()
L2gr_sim.Write()
L3gr_sim.Write()
L4gr_sim.Write()
L5gr_sim.Write()
L6gr_sim.Write()
L7gr_sim.Write()
L1gr_data.Write()
L2gr_data.Write()
L3gr_data.Write()
L4gr_data.Write()
L5gr_data.Write()
L6gr_data.Write()
L7gr_data.Write()
L1gr_vs_lumi_sim.Write()
L2gr_vs_lumi_sim.Write()
L3gr_vs_lumi_sim.Write()
L4gr_vs_lumi_sim.Write()
L5gr_vs_lumi_sim.Write()
L6gr_vs_lumi_sim.Write()
L7gr_vs_lumi_sim.Write()
L1gr_vs_lumi_data.Write()
L2gr_vs_lumi_data.Write()
L3gr_vs_lumi_data.Write()
L4gr_vs_lumi_data.Write()
L5gr_vs_lumi_data.Write()
L6gr_vs_lumi_data.Write()
L7gr_vs_lumi_data.Write()
	
XaxisnameI = "Date"
YaxisnameI = "Current [#muA/cm^{3}] @0^{0}C"

mgnI = TMultiGraph()
mgnI.SetTitle("TEC")#+str(QuerrMod)+" ("+modPart+")")
mgnI.Add(L1gr_sim,"l")
mgnI.Add(L2gr_sim,"l")
mgnI.Add(L3gr_sim,"l")
mgnI.Add(L4gr_sim,"l")
mgnI.Add(L5gr_sim,"l")
mgnI.Add(L6gr_sim,"l")
mgnI.Add(L7gr_sim,"l")
mgnI.Add(L1gr_data,"p")
mgnI.Add(L2gr_data,"p")
mgnI.Add(L3gr_data,"p")
mgnI.Add(L4gr_data,"p")
mgnI.Add(L5gr_data,"p")
mgnI.Add(L6gr_data,"p")
mgnI.Add(L7gr_data,"p")

cI = TCanvas("Module_I","Module_I",1200,800)
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
legI.AddEntry(L1gr_sim,"Ring 1","pl")
legI.AddEntry(L2gr_sim,"Ring 2","pl")
legI.AddEntry(L3gr_sim,"Ring 3","pl")
legI.AddEntry(L4gr_sim,"Ring 4","pl")
legI.AddEntry(L5gr_sim,"Ring 5","pl")
legI.AddEntry(L6gr_sim,"Ring 6","pl")
legI.AddEntry(L7gr_sim,"Ring 7","pl")
legI.SetTextFont(10)
legI.Draw()
leg_dmmy = TLegend(x2+0.06,y2-0.175,x2+0.35,y2)
leg_dmmy.AddEntry(dmmy_gr_sim,"Simulated","l")
leg_dmmy.AddEntry(dmmy_gr_dat,"Measured","p")
leg_dmmy.SetTextFont(10)
leg_dmmy.Draw()

cI.Write()
saveNameI = "DarkSimAllModules_"+simDate+"/plotRings_DCU/TEC_Ileak"
cI.SaveAs(saveNameI+"_avgOverRing.png")
cI.SaveAs(saveNameI+"_avgOverRing.pdf")

mgnIvsLumi = TMultiGraph()
mgnIvsLumi.SetTitle("TEC")
mgnIvsLumi.Add(L1gr_vs_lumi_sim,"l")
mgnIvsLumi.Add(L2gr_vs_lumi_sim,"l")
mgnIvsLumi.Add(L3gr_vs_lumi_sim,"l")
mgnIvsLumi.Add(L4gr_vs_lumi_sim,"l")
mgnIvsLumi.Add(L5gr_vs_lumi_sim,"l")
mgnIvsLumi.Add(L6gr_vs_lumi_sim,"l")
mgnIvsLumi.Add(L7gr_vs_lumi_sim,"l")
mgnIvsLumi.Add(L1gr_vs_lumi_data,"p")
mgnIvsLumi.Add(L2gr_vs_lumi_data,"p")
mgnIvsLumi.Add(L3gr_vs_lumi_data,"p")
mgnIvsLumi.Add(L4gr_vs_lumi_data,"p")
mgnIvsLumi.Add(L5gr_vs_lumi_data,"p")
mgnIvsLumi.Add(L6gr_vs_lumi_data,"p")
mgnIvsLumi.Add(L7gr_vs_lumi_data,"p")
	
cIvsLumi = TCanvas("Module_I_vs_Lumi","Module_I_vs_Lumi",1200,800)
gStyle.SetFillColor(kWhite)

cIvsLumi.SetGrid()
# cIvsLumi.SetLogx()
# cIvsLumi.SetLogy()
mgnIvsLumi.Draw("AP")
mgnIvsLumi.GetXaxis().SetTitle("Integrated Luminosity [fb^{-1}]")
mgnIvsLumi.GetYaxis().SetTitle(YaxisnameI)
mgnIvsLumi.GetXaxis().SetLimits(0,80)
mgnIvsLumi.GetHistogram().SetMinimum(0)#min(Ion))
#mgnIvsLumi.GetHistogram().SetMaximum(1.2*max(max(ileakc_t_on[L1Mod][5:-5]),max(ileakc_t_on[L2Mod][5:-5]),max(ileakc_t_on[L3Mod][5:-5]),max(ileakc_t_on[L4Mod][5:-5]))*LeakCorrection(273.16,293.16))#2.25*max(Ion))

if doFit:
	fits = {}
	for lyr in range(1,8):
		for reg in sorted(regions.keys()):
			fits["TEC"+str(lyr)+"_d"+reg] = TF1("TEC"+str(lyr)+"_d"+reg,str(datFits["TEC"+str(lyr)][int(reg)][1])+"*x+"+str(datFits["TEC"+str(lyr)][int(reg)][0]),regions[reg][0],regions[reg][1])
			fits["TEC"+str(lyr)+"_s"+reg] = TF1("TEC"+str(lyr)+"_s"+reg,str(simFits["TEC"+str(lyr)][int(reg)][1])+"*x+"+str(simFits["TEC"+str(lyr)][int(reg)][0]),regions[reg][0],regions[reg][1])
			fits["TEC"+str(lyr)+"_d"+reg].Draw("same")
			fits["TEC"+str(lyr)+"_s"+reg].Draw("same")

legIvsLumi = TLegend(x1,y1,x2,y2)
legIvsLumi.AddEntry(L1gr_vs_lumi_sim,"Ring 1","pl")
legIvsLumi.AddEntry(L2gr_vs_lumi_sim,"Ring 2","pl")
legIvsLumi.AddEntry(L3gr_vs_lumi_sim,"Ring 3","pl")
legIvsLumi.AddEntry(L4gr_vs_lumi_sim,"Ring 4","pl")
legIvsLumi.AddEntry(L5gr_vs_lumi_sim,"Ring 5","pl")
legIvsLumi.AddEntry(L6gr_vs_lumi_sim,"Ring 6","pl")
legIvsLumi.AddEntry(L7gr_vs_lumi_sim,"Ring 7","pl")
legIvsLumi.SetTextFont(10)
legIvsLumi.Draw()
leg_dmmy.Draw()

cIvsLumi.Write()
cIvsLumi.SaveAs(saveNameI+"_vs_lumi_avgOverRing.png")
cIvsLumi.SaveAs(saveNameI+"_vs_lumi_avgOverRing.pdf")

print "Doing TID_L1"
L1gr_sim_tib, L1gr_data_tib, L1gr_vs_lumi_sim_tib, L1gr_vs_lumi_data_tib = getTGraph("TID",1,kBlack)
print "Doing TID_L2"
L2gr_sim_tib, L2gr_data_tib, L2gr_vs_lumi_sim_tib, L2gr_vs_lumi_data_tib = getTGraph("TID",2,kRed)
print "Doing TID_L3"
L3gr_sim_tib, L3gr_data_tib, L3gr_vs_lumi_sim_tib, L3gr_vs_lumi_data_tib = getTGraph("TID",3,kBlue)

if not os.path.exists(runDir+'/DarkSimAllModules_'+simDate+'/plotRings_DCU/'): os.system('mkdir DarkSimAllModules_'+simDate+'/plotRings_DCU/')
outRfile_tid = TFile("DarkSimAllModules_"+simDate+"/plotRings_DCU/TID_avgOverRing.root",'RECREATE')
L1gr_sim_tib.Write()
L2gr_sim_tib.Write()
L3gr_sim_tib.Write()
L1gr_data_tib.Write()
L2gr_data_tib.Write()
L3gr_data_tib.Write()
L1gr_vs_lumi_sim_tib.Write()
L2gr_vs_lumi_sim_tib.Write()
L3gr_vs_lumi_sim_tib.Write()
L1gr_vs_lumi_data_tib.Write()
L2gr_vs_lumi_data_tib.Write()
L3gr_vs_lumi_data_tib.Write()
	
XaxisnameI = "Date"
YaxisnameI = "Current [#muA/cm^{3}] @0^{0}C"

mgnI_tib = TMultiGraph()
mgnI_tib.SetTitle("TID")#+str(QuerrMod)+" ("+modPart+")")
mgnI_tib.Add(L1gr_sim_tib,"l")
mgnI_tib.Add(L2gr_sim_tib,"l")
mgnI_tib.Add(L3gr_sim_tib,"l")
mgnI_tib.Add(L1gr_data_tib,"p")
mgnI_tib.Add(L2gr_data_tib,"p")
mgnI_tib.Add(L3gr_data_tib,"p")

cI_tib = TCanvas("Module_I_tid","Module_I_tid",1200,800)
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
#mgnI_tib.GetHistogram().SetMaximum(65)
#mgnI.GetHistogram().SetMaximum(1.2*max(max(ileakc_t_on[L1Mod][5:-5]),max(ileakc_t_on[L2Mod][5:-5]),max(ileakc_t_on[L3Mod][5:-5]),max(ileakc_t_on[L4Mod][5:-5]))*LeakCorrection(273.16,293.16))#2.25*max(Ion))
#mgnI.GetYaxis().SetTitleOffset(1.5)
y1=y2-.275
legI_tib = TLegend(x1,y1,x2,y2)
legI_tib.AddEntry(L1gr_sim,"Ring 1","pl")
legI_tib.AddEntry(L2gr_sim,"Ring 2","pl")
legI_tib.AddEntry(L3gr_sim,"Ring 3","pl")
legI_tib.SetTextFont(10)
legI_tib.Draw()
leg_dmmy.Draw()

cI_tib.Write()
saveNameI = "DarkSimAllModules_"+simDate+"/plotRings_DCU/TID_Ileak"
cI_tib.SaveAs(saveNameI+"_avgOverRing.png")
cI_tib.SaveAs(saveNameI+"_avgOverRing.pdf")

mgnIvsLumi_tib = TMultiGraph()
mgnIvsLumi_tib.SetTitle("TID")
mgnIvsLumi_tib.Add(L1gr_vs_lumi_sim_tib,"l")
mgnIvsLumi_tib.Add(L2gr_vs_lumi_sim_tib,"l")
mgnIvsLumi_tib.Add(L3gr_vs_lumi_sim_tib,"l")
mgnIvsLumi_tib.Add(L1gr_vs_lumi_data_tib,"p")
mgnIvsLumi_tib.Add(L2gr_vs_lumi_data_tib,"p")
mgnIvsLumi_tib.Add(L3gr_vs_lumi_data_tib,"p")

cIvsLumi_tib = TCanvas("Module_I_vs_Lumi_tid","Module_I_vs_Lumi_tid",1200,800)
gStyle.SetFillColor(kWhite)

cIvsLumi_tib.SetGrid()
# cIvsLumi_tib.SetLogx()
# cIvsLumi_tib.SetLogy()
mgnIvsLumi_tib.Draw("AP")
mgnIvsLumi_tib.GetXaxis().SetTitle("Integrated Luminosity [fb^{-1}]")
mgnIvsLumi_tib.GetYaxis().SetTitle(YaxisnameI)
mgnIvsLumi_tib.GetXaxis().SetLimits(0,80)
mgnIvsLumi_tib.GetHistogram().SetMinimum(0)#min(Ion))
#mgnIvsLumi_tib.GetHistogram().SetMaximum(65)
#mgnIvsLumi.GetHistogram().SetMaximum(1.2*max(max(ileakc_t_on[L1Mod][5:-5]),max(ileakc_t_on[L2Mod][5:-5]),max(ileakc_t_on[L3Mod][5:-5]),max(ileakc_t_on[L4Mod][5:-5]))*LeakCorrection(273.16,293.16))#2.25*max(Ion))
#mgnI.GetYaxis().SetTitleOffset(1.5)

if doFit:
	for lyr in range(1,4):
		for reg in sorted(regions.keys()):
			fits["TID"+str(lyr)+"_d"+reg] = TF1("TID"+str(lyr)+"_d"+reg,str(datFits["TID"+str(lyr)][int(reg)][1])+"*x+"+str(datFits["TID"+str(lyr)][int(reg)][0]),regions[reg][0],regions[reg][1])
			fits["TID"+str(lyr)+"_s"+reg] = TF1("TID"+str(lyr)+"_s"+reg,str(simFits["TID"+str(lyr)][int(reg)][1])+"*x+"+str(simFits["TID"+str(lyr)][int(reg)][0]),regions[reg][0],regions[reg][1])
			fits["TID"+str(lyr)+"_d"+reg].Draw("same")
			fits["TID"+str(lyr)+"_s"+reg].Draw("same")

legIvsLumi_tib = TLegend(x1,y1,x2,y2)
legIvsLumi_tib.AddEntry(L1gr_vs_lumi_sim_tib,"Ring 1","pl")
legIvsLumi_tib.AddEntry(L2gr_vs_lumi_sim_tib,"Ring 2","pl")
legIvsLumi_tib.AddEntry(L3gr_vs_lumi_sim_tib,"Ring 3","pl")
legIvsLumi_tib.SetTextFont(10)
legIvsLumi_tib.Draw()
leg_dmmy.Draw()

cIvsLumi_tib.Write()
cIvsLumi_tib.SaveAs(saveNameI+"_vs_lumi_avgOverRing.png")
cIvsLumi_tib.SaveAs(saveNameI+"_vs_lumi_avgOverRing.pdf")

if doFit:
	pickle.dump(datFits,open(runDir+'/DarkSimAllModules_'+simDate+'/plotRings_DCU/datFits.p','wb'))
	pickle.dump(simFits,open(runDir+'/DarkSimAllModules_'+simDate+'/plotRings_DCU/simFits.p','wb'))

outRfile.Close()	
outRfile_tid.Close()
RFile.Close()

print "***************************** DONE *********************************" 
