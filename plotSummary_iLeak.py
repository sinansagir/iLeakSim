#!/usr/bin/python

import os,sys,fnmatch,pickle
from bisect import bisect_left
from array import array
import numpy as np
from ROOT import *
import CMS_lumi, tdrstyle
gROOT.SetBatch(1)

#set the tdr style
tdrstyle.setTDRStyle()

#change the CMS_lumi variables (see CMS_lumi.py)
CMS_lumi.lumi_7TeV = "6.1 fb^{-1}"
CMS_lumi.lumi_8TeV = "13.4 fb^{-1}"
CMS_lumi.lumi_13TeV= "2.3 fb^{-1}"
CMS_lumi.writeExtraText = 1
CMS_lumi.extraText = "Preliminary"
CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)

iPos = 10
if( iPos==0 ): CMS_lumi.relPosX = 0.12

H_ref = 600; 
W_ref = 900;
W = W_ref
H = H_ref

iPeriod = 0

# references for T, B, L, R
T = 0.10*H_ref
B = 0.35*H_ref 
L = 0.12*W_ref
R = 0.07*W_ref

##################################################################################################################
# The code looks for the input simulation tree in "DarkSimAllModules_<simDate>/DarkSimAllModules_<simDate>.root"
# The output files will be in "DarkSimAllModules_<simDate>/plotLayers_DCU/". 
##################################################################################################################

#******************************Input to edit******************************************************
measDataPath = "MeasDataLocal/data_DCU_raw"
simDate = "2023_9_4"
readTree=False # This needs to be true if running the code on the tree for the first time. It will dump what's read from tree into pickle files and these can be loaded if this option is set to "False"
readDCU=False
doFit=False
mcSF=1.#40./35.
postFix=''

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
dcutemp = {}
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
	dcutemp[event.DETID] = [-1]*len(dtime_t)
TrackMapRFile.Close()

#update the ring positions!!!
infileRing = open('InputDataLocal/tracker.dat', 'r')
linesRing = infileRing.readlines()
infileRing.close()
for line in linesRing:
	data = line.strip().split()
	if 'TEC' in data[0] or 'TID' in data[0]:
		pos[int(data[-1][1:-1])]=int(data[data.index('Ring')+1])
	
print "========>>>>>>>> FINISHED READING TRACKER MAP"

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
IntLumR2=0.
dtime_t_2 = [TDatime(int(item)).GetDate() for item in dtime_t]
dtime_t = [int(item) for item in dtime_t]
for i in range(len(linesLumi)):
	data = linesLumi[i].strip().split()
	try: 
		IntLum+=float(data[2])/1e6 # in INVFB
		if int(data[0].split('/')[2]+data[0].split('/')[1]+data[0].split('/')[0]) in dtime_t_2:
			lumiAll.append(IntLum)
			lumiPerDay.append(float(data[2]))
			if data[0]=='03/06/2015':IntLumR1=IntLum
			if data[0]=='03/06/2019':IntLumR2=IntLum-IntLumR1
	except: print "Warning! => Unknown data format: ",data,"in",lumiFile
print "Total Integrated Lumi:",lumiAll[-1]
print "Total Integrated Lumi Run1:",IntLumR1
print "Total Integrated Lumi Run2:",IntLumR2
print "Total Integrated Lumi Run3:",lumiAll[-1]-IntLumR1-IntLumR2

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
for file in findfiles(measDataPath+'/iLeak_perDay', '*.txt'):
	dcufiles.append(file)

if readDCU:
	ind = 0
	print "Reading DCU ileak data ..."
	for file in dcufiles:
		if ind%500==0: print "Finished",ind,"out of",len(dcufiles)
		ind+=1
		dcudata = open(file, 'r')
		linesdcu = dcudata.readlines()
		dcudata.close()
		mod=int(file.split('/')[-1][:-4])
		for line in linesdcu:
			data = line.strip().split()
			lnxTime = int(data[0])
			ind_ = findClosest(dtime_t_2,TDatime(lnxTime).GetDate())
			dcuileak[mod][ind_]=float(data[1])
	ind = 0
	print "Reading DCU temperature data ..."
	for file in dcufiles:
		if ind%500==0: print "Finished",ind,"out of",len(dcufiles)
		ind+=1
		dcudata = open(file.replace('iLeak','TSil'), 'r')
		linesdcu = dcudata.readlines()
		dcudata.close()
		mod=int(file.split('/')[-1][:-4])
		for line in linesdcu:
			data = line.strip().split()
			lnxTime = int(data[0])
			ind_ = findClosest(dtime_t_2,TDatime(lnxTime).GetDate())
			measTemp = float(data[1])
			if measTemp<-35: continue
			dcutemp[mod][ind_]=measTemp
	print "Damping DCU data into pickle ..."
	pickle.dump(dcuileak,open("DarkSimAllModules_"+simDate+'/dcuileak.p','wb'))
	pickle.dump(dcutemp,open("DarkSimAllModules_"+simDate+'/dcutemp.p','wb'))
else:
	print "Loading DCU data from pickle ..."
	dcuileak=pickle.load(open("DarkSimAllModules_"+simDate+'/dcuileak.p','rb'))
	dcutemp=pickle.load(open("DarkSimAllModules_"+simDate+'/dcutemp.p','rb'))

k_B = 8.617343183775136189e-05
def LeakCorrection(Tref,T):
	E = 1.21 # formerly 1.12 eV
	try: return (Tref/T)*(Tref/T)*np.exp(-(E/(2.*k_B))*(1./Tref-1./T))
	except:
		print Tref,T
		return 0

print "========>>>>>>>> SCALING CURRENT TO 0C and AVERAGING"
for mod in ileakc_t_on.keys():
	ileakc_t_on[mod]=[item*LeakCorrection(273.16,293.16)*1.e3/volume[mod] for item in ileakc_t_on[mod]] #muA/cm^3 @0C
	#ileakc_t_on[mod]=[ileakc_t_on[mod][ind]*mcSF*LeakCorrection(temp_t_on[mod][ind],293.16)*LeakCorrection(273.16,dcutemp[mod][ind]+273.16)*1.e3/volume[mod] for ind in range(len(ileakc_t_on[mod]))] #muA/cm^3 @0C
	#dcuileak[mod]=[dcuileak[mod][ind]*LeakCorrection(273.16,temp_t_on[mod][ind])/volume[mod] for ind in range(len(dcuileak[mod]))] #muA/cm^3 @0C
	dcuileak[mod]=[dcuileak[mod][ind]*LeakCorrection(273.16,dcutemp[mod][ind]+273.16)/volume[mod] for ind in range(len(dcuileak[mod]))] #muA/cm^3 @0C

def formatUpperHist(histogram):
	histogram.GetXaxis().SetLabelSize(0)
	histogram.GetYaxis().SetLabelSize(0.07)
	histogram.GetYaxis().SetTitleSize(0.08)
	histogram.GetYaxis().SetTitleOffset(.61)
	#histogram.GetXaxis().SetNdivisions(506)
	histogram.GetYaxis().CenterTitle()
		
def formatLowerHist(histogram):
	histogram.GetXaxis().SetLabelSize(.12)
	histogram.GetXaxis().SetTitleSize(0.15)
	histogram.GetXaxis().SetTitleOffset(0.95)
	#histogram.GetXaxis().SetNdivisions(506)

	histogram.GetYaxis().SetLabelSize(0.12)
	histogram.GetYaxis().SetTitleSize(0.14)
	histogram.GetYaxis().SetTitleOffset(.37)
	histogram.GetYaxis().SetNdivisions(5)
	histogram.GetYaxis().CenterTitle()

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
IgrsAll = {}
def getTGraph(modPart,layer,color):
	IonS=[0]*len(dtime_t)
	IonD=[0]*len(dtime_t)
	IonDoS=[0]*len(dtime_t)
	partMods = [mod for mod in part.keys() if modPart in part[mod] and pos[mod]==layer and mod in ileakc_t_on.keys()]
	for day in range(len(dtime_t)):
		nModsInLayerS=0
		nModsInLayerD=0
		for mod in partMods:
			IonS[day]+=ileakc_t_on[mod][day]
			nModsInLayerS+=1
			if dcuileak[mod][day]>0 and abs(dcuileak[mod][day] - ileakc_t_on[mod][day])/dcuileak[mod][day]<0.6 and abs(dcutemp[mod][day]+273.16 - temp_t_on[mod][day])/(dcutemp[mod][day]+273.16)<0.6:
				IonD[day]+=dcuileak[mod][day]
				nModsInLayerD+=1
		IonS[day]/=nModsInLayerS
		if nModsInLayerD>0: 
			if abs(IonD[day] - IonS[day])/IonD[day]>1.: IonD[day]=0
			else: IonD[day]/=nModsInLayerD
		IonDoS[day]=IonD[day]/IonS[day]

	lyrKey = modPart+'_L'+str(layer)
	IgrsAll[lyrKey+'_sim'] = TGraph(len(dtime_t),array('d',dtime_t),array('d',IonS))
	IgrsAll[lyrKey+'_sim'].SetMarkerColor(color)
	IgrsAll[lyrKey+'_sim'].SetLineColor(color)
	IgrsAll[lyrKey+'_sim'].SetLineStyle(1)
	IgrsAll[lyrKey+'_sim'].SetLineWidth(3)
	IgrsAll[lyrKey+'_sim'].SetMarkerStyle(7)
	IgrsAll[lyrKey+'_sim'].SetMarkerSize(0.3)
	IgrsAll[lyrKey+'_vs_lumi_sim'] = TGraph(len(dtime_t),array('d',lumiAll),array('d',IonS))
	IgrsAll[lyrKey+'_vs_lumi_sim'].SetMarkerColor(color)
	IgrsAll[lyrKey+'_vs_lumi_sim'].SetLineColor(color)
	IgrsAll[lyrKey+'_vs_lumi_sim'].SetLineStyle(1)
	IgrsAll[lyrKey+'_vs_lumi_sim'].SetLineWidth(3)
	IgrsAll[lyrKey+'_vs_lumi_sim'].SetMarkerStyle(7)
	IgrsAll[lyrKey+'_vs_lumi_sim'].SetMarkerSize(0.6)
	
	IgrsAll[lyrKey+'_dat'] = TGraph(len(dtime_t),array('d',dtime_t),array('d',IonD))
	IgrsAll[lyrKey+'_dat'].SetMarkerColor(color)
	IgrsAll[lyrKey+'_dat'].SetLineColor(color)
	IgrsAll[lyrKey+'_dat'].SetLineStyle(1)
	IgrsAll[lyrKey+'_dat'].SetLineWidth(3)
	IgrsAll[lyrKey+'_dat'].SetMarkerStyle(2)
	IgrsAll[lyrKey+'_dat'].SetMarkerSize(0.9)
	IgrsAll[lyrKey+'_vs_lumi_dat'] = TGraph(len(dtime_t),array('d',lumiAll),array('d',IonD))
	IgrsAll[lyrKey+'_vs_lumi_dat'].SetMarkerColor(color)
	IgrsAll[lyrKey+'_vs_lumi_dat'].SetLineColor(color)
	IgrsAll[lyrKey+'_vs_lumi_dat'].SetLineStyle(1)
	IgrsAll[lyrKey+'_vs_lumi_dat'].SetLineWidth(3)
	IgrsAll[lyrKey+'_vs_lumi_dat'].SetMarkerStyle(2)
	IgrsAll[lyrKey+'_vs_lumi_dat'].SetMarkerSize(0.9)
	IgrsAll[lyrKey+'_ratio'] = TGraph(len(dtime_t),array('d',dtime_t),array('d',IonDoS))
	IgrsAll[lyrKey+'_ratio'].SetMarkerColor(color)
	IgrsAll[lyrKey+'_ratio'].SetLineColor(color)
	IgrsAll[lyrKey+'_ratio'].SetLineStyle(1)
	IgrsAll[lyrKey+'_ratio'].SetLineWidth(3)
	IgrsAll[lyrKey+'_ratio'].SetMarkerStyle(2)
	IgrsAll[lyrKey+'_ratio'].SetMarkerSize(0.9)
	IgrsAll[lyrKey+'_vs_lumi_ratio'] = TGraph(len(dtime_t),array('d',lumiAll),array('d',IonDoS))
	IgrsAll[lyrKey+'_vs_lumi_ratio'].SetMarkerColor(color)
	IgrsAll[lyrKey+'_vs_lumi_ratio'].SetLineColor(color)
	IgrsAll[lyrKey+'_vs_lumi_ratio'].SetLineStyle(1)
	IgrsAll[lyrKey+'_vs_lumi_ratio'].SetLineWidth(3)
	IgrsAll[lyrKey+'_vs_lumi_ratio'].SetMarkerStyle(2)
	IgrsAll[lyrKey+'_vs_lumi_ratio'].SetMarkerSize(0.9)
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
		
	return #IGr_sim,IGr_data,IGr_ratio,IGr_vs_lumi_sim,IGr_vs_lumi_data,IGr_vs_lumi_ratio
		
outDir = 'DarkSimAllModules_'+simDate+'/plotSummary_'+measDataPath.split('/')[-1]
if not os.path.exists(runDir+'/'+outDir): os.system('mkdir '+outDir)
outRfile = TFile(outDir+"/summaries_iLeak"+postFix+".root",'RECREATE')

dmmy_gr_sim = TGraph(len([1294120800,1294207200]),array('d',[1294120800,1294207200]),array('d',[-99,-100])) #dummy TGraph to add extra legends (there might be better ways!)
dmmy_gr_sim.SetMarkerColor(kBlack)
dmmy_gr_sim.SetLineColor(kBlack)
dmmy_gr_sim.SetLineStyle(1)
dmmy_gr_sim.SetLineWidth(3)
dmmy_gr_sim.SetMarkerStyle(7)
dmmy_gr_sim.SetMarkerSize(0.6)
dmmy_gr_dat = TGraph(len([1294120800,1294207200]),array('d',[1294120800,1294207200]),array('d',[-99,-100])) #dummy TGraph to add extra legends (there might be better ways!)
dmmy_gr_dat.SetMarkerColor(kBlack)
dmmy_gr_dat.SetLineColor(kBlack)
dmmy_gr_dat.SetLineStyle(1)
dmmy_gr_dat.SetLineWidth(3)
dmmy_gr_dat.SetMarkerStyle(2)
dmmy_gr_dat.SetMarkerSize(2.)
	
XaxisnameI = "Date"
YaxisnameI = "Current [#muA/cm^{3}] @0#circC"

canvs = {}
canvs['dummy'] = TCanvas('dummy','dummy',50,50,W,H)

yDiv=0.35
uPadt=TPad("uPadt","",0,yDiv,1,1) #for actual plots
uPadt.SetLeftMargin( L/W )
uPadt.SetRightMargin( R/W )
uPadt.SetTopMargin( T/H )
uPadt.SetBottomMargin( 0 )	
uPadt.SetFillColor(0)
uPadt.SetBorderMode(0)
uPadt.SetFrameFillStyle(0)
uPadt.SetFrameBorderMode(0)
# uPadt.SetTickx(0)
# uPadt.SetTicky(0)

lPadt=TPad("lPadt","",0,0,1,yDiv) #for sigma runner
lPadt.SetLeftMargin( L/W )
lPadt.SetRightMargin( R/W )
lPadt.SetTopMargin( 0 )
lPadt.SetBottomMargin( B/H )
lPadt.SetFillColor(0)
lPadt.SetBorderMode(0)
lPadt.SetFrameFillStyle(0)
lPadt.SetFrameBorderMode(0)
# lPadt.SetTickx(0)
# lPadt.SetTicky(0)
lPadt.SetGridy()

uPadl=TPad("uPadl","",0,yDiv,1,1) #for actual plots
uPadl.SetLeftMargin( L/W )
uPadl.SetRightMargin( R/W-0.03 )
uPadl.SetTopMargin( T/H )
uPadl.SetBottomMargin( 0 )	
uPadl.SetFillColor(0)
uPadl.SetBorderMode(0)
uPadl.SetFrameFillStyle(0)
uPadl.SetFrameBorderMode(0)
# uPadl.SetTickx(0)
# uPadl.SetTicky(0)

lPadl=TPad("lPadl","",0,0,1,yDiv) #for sigma runner
lPadl.SetLeftMargin( L/W )
lPadl.SetRightMargin( R/W-0.03 )
lPadl.SetTopMargin( 0 )
lPadl.SetBottomMargin( B/H )
lPadl.SetFillColor(0)
lPadl.SetBorderMode(0)
lPadl.SetFrameFillStyle(0)
lPadl.SetFrameBorderMode(0)
# lPadl.SetTickx(0)
# lPadl.SetTicky(0)
lPadl.SetGridy()

x1=.40
y2=.87
x2=x1+.13
y1=y2-.38
leg_dmmy = TLegend(x1-.25,.4,x1-.01,.4+.175)
SetOwnership( leg_dmmy, 0 )   # 0 = release (not keep), 1 = keep
leg_dmmy.SetShadowColor(0)
leg_dmmy.SetFillColor(0)
leg_dmmy.SetFillStyle(0)
leg_dmmy.SetLineColor(0)
leg_dmmy.SetLineStyle(0)
leg_dmmy.SetBorderSize(0) 
leg_dmmy.SetTextFont(62)
leg_dmmy.AddEntry(dmmy_gr_sim,"Simulated","l")
leg_dmmy.AddEntry(dmmy_gr_dat,"Measured","p")

colorList = [kBlack,kRed+1,kBlue+1,kGreen+2,kCyan+1,kMagenta+1,kYellow+2]
nLayers = {'TIB':4,'TOB':6,'TID':3,'TEC':7}
legs = {}
mgnIs = {}
for subdet in ['TIB','TOB','TID','TEC']:
	mgnIs[subdet] = TMultiGraph()
	mgnIs[subdet].SetTitle("")
	mgnIs[subdet+'ratio'] = TMultiGraph()
	mgnIs[subdet+'ratio'].SetTitle("")
	for lyr in range(1,nLayers[subdet]+1):
		print "Doing "+subdet+"_L"+str(lyr)
		getTGraph(subdet,lyr,colorList[lyr-1])
		mgnIs[subdet].Add(IgrsAll[subdet+'_L'+str(lyr)+'_sim'],"l")
		mgnIs[subdet].Add(IgrsAll[subdet+'_L'+str(lyr)+'_dat'],"p")
		mgnIs[subdet+'ratio'].Add(IgrsAll[subdet+'_L'+str(lyr)+'_ratio'],"p")
	if subdet=='TIB': 
		CMS_lumi.lumi_sqrtS = "Tracker Inner Barrel [TIB]"
		y1=y2-.28
	if subdet=='TOB': 
		CMS_lumi.lumi_sqrtS = "Tracker Outer Barrel [TOB]"
		y1=y2-.38
	if subdet=='TID': 
		CMS_lumi.lumi_sqrtS = "Tracker Inner Disk [TID]"
		y1=y2-.23
	if subdet=='TEC': 
		CMS_lumi.lumi_sqrtS = "Tracker End-Cap [TEC]"
		y1=y2-.43
	canvs[subdet] = TCanvas(subdet,subdet,50,50,W,H)
	canvs[subdet].SetFillColor(0)
	canvs[subdet].SetBorderMode(0)
	canvs[subdet].SetFrameFillStyle(0)
	canvs[subdet].SetFrameBorderMode(0)
	canvs[subdet].SetTickx(0)
	canvs[subdet].SetTicky(0)
	uPadt.Draw()
	lPadt.Draw()
	
	uPadt.cd()
	mgnIs[subdet].Draw("AP")
	formatUpperHist(mgnIs[subdet])
	mgnIs[subdet].GetXaxis().SetTimeDisplay(1)
	mgnIs[subdet].GetXaxis().SetNdivisions(-503)
	mgnIs[subdet].GetXaxis().SetTimeFormat("%Y-%m-%d")
	mgnIs[subdet].GetXaxis().SetTimeOffset(0,"gmt")
	mgnIs[subdet].GetXaxis().SetTitle(XaxisnameI)
	mgnIs[subdet].GetYaxis().SetTitle(YaxisnameI)
	mgnIs[subdet].GetXaxis().SetLimits(min(dtime_t),max(dtime_t))
	mgnIs[subdet].GetHistogram().SetMinimum(0.0001)

	legs[subdet] = TLegend(x1,y1,x2,y2)	
	legs[subdet].SetShadowColor(0)
	legs[subdet].SetFillColor(0)
	legs[subdet].SetFillStyle(0)
	legs[subdet].SetLineColor(0)
	legs[subdet].SetLineStyle(0)
	legs[subdet].SetBorderSize(0) 
	legs[subdet].SetTextFont(42)
	legText = "Layer "
	if subdet=="TID" or subdet=="TEC": legText = "Ring "
	for lyr in range(1,nLayers[subdet]+1):
		legs[subdet].AddEntry(IgrsAll[subdet+'_L'+str(lyr)+'_sim'],legText+str(lyr),"pl")
	legs[subdet].Draw()
	leg_dmmy.Draw()

	lPadt.cd()
	# lPadt.SetGrid()
	mgnIs[subdet+'ratio'].Draw("AP")
	formatLowerHist(mgnIs[subdet+'ratio'])
	mgnIs[subdet+'ratio'].GetXaxis().SetTimeDisplay(1)
	mgnIs[subdet+'ratio'].GetXaxis().SetNdivisions(-503)
	mgnIs[subdet+'ratio'].GetXaxis().SetTimeFormat("%Y-%m-%d")
	mgnIs[subdet+'ratio'].GetXaxis().SetTimeOffset(0,"gmt")
	mgnIs[subdet+'ratio'].GetXaxis().SetTitle(XaxisnameI)
	mgnIs[subdet+'ratio'].GetYaxis().SetTitle(YaxisnameI)
	mgnIs[subdet+'ratio'].GetXaxis().SetLimits(min(dtime_t),max(dtime_t))
	mgnIs[subdet+'ratio'].GetXaxis().SetTitle("Date")
	mgnIs[subdet+'ratio'].GetYaxis().SetTitle('Mea/Sim')
	mgnIs[subdet+'ratio'].GetHistogram().SetMinimum(0.5)#min(Ion))
	mgnIs[subdet+'ratio'].GetHistogram().SetMaximum(1.5)

	#draw the lumi text on the canvas
	CMS_lumi.CMS_lumi(uPadt, iPeriod, iPos)

	uPadt.Update()
	uPadt.RedrawAxis()
	frame = uPadt.GetFrame()
	uPadt.Draw()

	canvs[subdet].Write()
	saveNameI = outDir+"/"+subdet+"_Ileak_avgOverLayer"+postFix
	canvs[subdet].SaveAs(saveNameI+".png")
	canvs[subdet].SaveAs(saveNameI+".pdf")
	
	mgnIs[subdet+'vslumi'] = TMultiGraph()
	mgnIs[subdet+'vslumi'].SetTitle("")
	mgnIs[subdet+'vslumiratio'] = TMultiGraph()
	mgnIs[subdet+'vslumiratio'].SetTitle("")
	for lyr in range(1,nLayers[subdet]+1):
		mgnIs[subdet+'vslumi'].Add(IgrsAll[subdet+'_L'+str(lyr)+'_vs_lumi_sim'],"l")
		mgnIs[subdet+'vslumi'].Add(IgrsAll[subdet+'_L'+str(lyr)+'_vs_lumi_dat'],"p")
		mgnIs[subdet+'vslumiratio'].Add(IgrsAll[subdet+'_L'+str(lyr)+'_vs_lumi_ratio'],"p")
	if subdet=='TIB': 
		CMS_lumi.lumi_sqrtS = "Tracker Inner Barrel [TIB]"
		y1=y2-.28
	if subdet=='TOB': 
		CMS_lumi.lumi_sqrtS = "Tracker Outer Barrel [TOB]"
		y1=y2-.38
	if subdet=='TID': 
		CMS_lumi.lumi_sqrtS = "Tracker Inner Disk [TID]"
		y1=y2-.23
	if subdet=='TEC': 
		CMS_lumi.lumi_sqrtS = "Tracker End-Cap [TEC]"
		y1=y2-.43
	canvs[subdet+'vslumi'] = TCanvas(subdet+'vslumi',subdet+'vslumi',50,50,W,H)
	canvs[subdet+'vslumi'].SetFillColor(0)
	canvs[subdet+'vslumi'].SetBorderMode(0)
	canvs[subdet+'vslumi'].SetFrameFillStyle(0)
	canvs[subdet+'vslumi'].SetFrameBorderMode(0)
	canvs[subdet+'vslumi'].SetTickx(0)
	canvs[subdet+'vslumi'].SetTicky(0)
	uPadl.Draw()
	lPadl.Draw()
	
	uPadl.cd()
	mgnIs[subdet+'vslumi'].Draw("AP")
	formatUpperHist(mgnIs[subdet+'vslumi'])
	mgnIs[subdet+'vslumi'].GetXaxis().SetTitle("Integrated Luminosity [fb^{-1}]")
	mgnIs[subdet+'vslumi'].GetYaxis().SetTitle(YaxisnameI)
	mgnIs[subdet+'vslumi'].GetXaxis().SetLimits(0,255)
	mgnIs[subdet+'vslumi'].GetHistogram().SetMinimum(0.0001)#min(Ion))
	#if subdet=='TOB': mgnIs[subdet+'vslumi'].GetHistogram().SetMaximum(44)

	legs[subdet+'vslumi'] = TLegend(x1,y1,x2,y2)	
	legs[subdet+'vslumi'].SetShadowColor(0)
	legs[subdet+'vslumi'].SetFillColor(0)
	legs[subdet+'vslumi'].SetFillStyle(0)
	legs[subdet+'vslumi'].SetLineColor(0)
	legs[subdet+'vslumi'].SetLineStyle(0)
	legs[subdet+'vslumi'].SetBorderSize(0) 
	legs[subdet+'vslumi'].SetTextFont(42)
	legText = "Layer "
	if subdet=="TID" or subdet=="TEC": legText = "Ring "
	for lyr in range(1,nLayers[subdet]+1):
		legs[subdet+'vslumi'].AddEntry(IgrsAll[subdet+'_L'+str(lyr)+'_vs_lumi_sim'],legText+str(lyr),"pl")
	legs[subdet+'vslumi'].Draw()
	leg_dmmy.Draw()

	lPadl.cd()
	# lPadl.SetGrid()
	mgnIs[subdet+'vslumiratio'].Draw("AP")
	formatLowerHist(mgnIs[subdet+'vslumiratio'])
	mgnIs[subdet+'vslumiratio'].GetXaxis().SetTitle("Integrated Luminosity [fb^{-1}]")
	mgnIs[subdet+'vslumiratio'].GetYaxis().SetTitle('Mea/Sim')
	mgnIs[subdet+'vslumiratio'].GetXaxis().SetLimits(0,255)
	mgnIs[subdet+'vslumiratio'].GetHistogram().SetMinimum(0.5)#min(Ion))
	mgnIs[subdet+'vslumiratio'].GetHistogram().SetMaximum(1.5)

	#draw the lumi text on the canvas
	CMS_lumi.CMS_lumi(uPadl, iPeriod, iPos)

	uPadl.Update()
	uPadl.RedrawAxis()
	frame = uPadl.GetFrame()
	uPadl.Draw()

	canvs[subdet+'vslumi'].Write()
	saveNameI = outDir+"/"+subdet+"_Ileak_vs_lumi_avgOverLayer"+postFix
	canvs[subdet+'vslumi'].SaveAs(saveNameI+".png")
	canvs[subdet+'vslumi'].SaveAs(saveNameI+".pdf")
for gr in IgrsAll.keys(): IgrsAll[gr].Write()
outRfile.Close()
# if doFit:
# 	fits = {}
# 	for lyr in range(1,7):
# 		for reg in sorted(regions.keys()):
# 			fits["TOB"+str(lyr)+"_d"+reg] = TF1("TOB"+str(lyr)+"_d"+reg,str(datFits["TOB"+str(lyr)][int(reg)][1])+"*x+"+str(datFits["TOB"+str(lyr)][int(reg)][0]),regions[reg][0],regions[reg][1])
# 			fits["TOB"+str(lyr)+"_s"+reg] = TF1("TOB"+str(lyr)+"_s"+reg,str(simFits["TOB"+str(lyr)][int(reg)][1])+"*x+"+str(simFits["TOB"+str(lyr)][int(reg)][0]),regions[reg][0],regions[reg][1])
# 			fits["TOB"+str(lyr)+"_d"+reg].Draw("same")
# 			fits["TOB"+str(lyr)+"_s"+reg].Draw("same")

print "***************************** DONE *********************************" 
