#!/usr/bin/python

import os,sys,fnmatch,math,pickle
from bisect import bisect_left
import numpy as np
from ROOT import *
gROOT.SetBatch(1)

##################################################################################################################
# The code looks for the input simulation tree in "DarkSimAllModules_<simDate>/DarkSimAllModules_<simDate>.root"
# The output files will be in "DarkSimAllModules_<simDate>/approvalPlots/". 
##################################################################################################################

#******************************Input to edit******************************************************
measDataPath = "MeasDataLocal/data_DCU_raw"
simDate = "2023_9_4"
readTree=False # This needs to be true if running the code on the tree for the first time. It will dump what's read from tree into pickle files and these can be loaded if this option set to "False"
readDCU=False
scaleCurrentToMeasTemp = True # Scale current to measured temperature (Check how this is done!!!! The default method assumes that the simulated current is at 20C)
datesToPlot = ['2012_8_30','2016_10_11','2018_10_18']
datesToPlot+= ['2022_10_20','2023_4_25','2023_5_12','2023_7_16','2023_9_1']
datesToPlot+= ['2023_6_6','2023_6_8','2023_6_13','2023_6_28','2023_6_30']
datesToPlot+= ['2023_7_9','2023_7_11','2023_7_12','2023_7_14','2023_7_15']
datesToPlot+= ['2023_9_1','2023_9_2','2023_9_3','2023_9_4']
datesToPlot = ['2023_6_6','2023_9_1']

#READ IN TREE
InTreeSim="DarkSimAllModules_"+simDate+"/DarkSimAllModules_"+simDate+".root"
print "Input Tree: ",InTreeSim
simFile = TFile(InTreeSim,'READ')
simTree = simFile.Get('tree')
print "/////////////////////////////////////////////////////////////////"
print "Number of Simulated Modules in the tree: ", simTree.GetEntries()
print "/////////////////////////////////////////////////////////////////"
# simTree.GetEntry(0)
# print type(simTree.DETID_T), type(simTree.ileakc_t_on), type(simTree.dtime_t)
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
		if nMod%1000==0: print "Finished reading ", nMod, "/", simTree.GetEntries(), " modules!"
	print "********************* FINISHED READING TREE *********************"
	print "- Dumping detector ids into pickle ..."
	pickle.dump(detid_t,open('DarkSimAllModules_'+simDate+'/detid_t.p','wb'))
	print "- Dumping partitions into pickle ..."
	pickle.dump(partition_t,open('DarkSimAllModules_'+simDate+'/partition_t.p','wb'))
	print "- Dumping time into pickle ..."
	pickle.dump(dtime_t,open('DarkSimAllModules_'+simDate+'/dtime_t.p','wb'))
	print "- Dumping temperature into pickle ..."
	pickle.dump(temp_t_on,open('DarkSimAllModules_'+simDate+'/temp_t_on.p','wb'))
	print "- Dumping leakage current into pickle ..."
	pickle.dump(ileakc_t_on,open('DarkSimAllModules_'+simDate+'/ileakc_t_on.p','wb'))
	print "*********************** FINISHED DUMPING ***********************"
else:
	print "******************* LOADING TREE FROM PICKLE ********************"
	print "-Loading detector ids ..."
	detid_t=pickle.load(open('DarkSimAllModules_'+simDate+'/detid_t.p','rb'))
	print "-Loading partitions ..."
	partition_t=pickle.load(open('DarkSimAllModules_'+simDate+'/partition_t.p','rb'))
	print "-Loading time ..."
	dtime_t=pickle.load(open('DarkSimAllModules_'+simDate+'/dtime_t.p','rb'))
	print "-Loading temperature ..."
	temp_t_on=pickle.load(open('DarkSimAllModules_'+simDate+'/temp_t_on.p','rb'))
	print "-Loading leakage current ..."
	ileakc_t_on=pickle.load(open('DarkSimAllModules_'+simDate+'/ileakc_t_on.p','rb'))
	print "******************* LOADED TREE FROM PICKLE ********************"
dtime_t_2 = [TDatime(int(item)).GetDate() for item in dtime_t]

print "========>>>>>>>> READING TRACKER MAP"
TrackMap="InputDataLocal/TrackMap.root"
TrackMapRFile = TFile(TrackMap,'READ')
TrackMapTTree = TrackMapRFile.Get('treemap')
part,pos,volume,dcuileak,dcutemp = {},{},{},{},{}
for event in TrackMapTTree:
	part[event.DETID] = event.Partition
	pos[event.DETID] = event.StructPos
	volume[event.DETID] = event.D*(event.W1+event.W2)*(event.L/2)*1e6 #cm^3
	dcuileak[event.DETID] = [-1]*len(dtime_t)
	dcutemp[event.DETID] = [-99]*len(dtime_t)
TrackMapRFile.Close()
print "========>>>>>>>> FINISHED READING TRACKER MAP"

runDir=os.getcwd()

k_B = 8.617343183775136189e-05
def LeakCorrection(Tref,T):
	E = 1.21 # formerly 1.12 eV
	return (Tref/T)*(Tref/T)*math.exp(-E/(2.*k_B)*(1./Tref-1./T))
	
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

if readDCU:
	dcufiles = []
	for file in findfiles(measDataPath+'/iLeak_perDay', '*.txt'):
		dcufiles.append(file)
	ind = 0
	print "Reading DCU data ..."
	for file in dcufiles:
		if ind%500==0: print "Finished",ind,"out of",len(dcufiles)
		ind+=1
		dcudata = open(file, 'r')
		linesdcu = dcudata.readlines()
		dcudata.close()
		dcutdata = open(file.replace("iLeak","TSil"), 'r')
		linesdcut = dcutdata.readlines()
		dcutdata.close()
		mod=int(file.split('/')[-1][:-4])
		for line in linesdcu:
			data = line.strip().split()
			lnxTime = int(data[0])
			ind_ = findClosest(dtime_t_2,TDatime(lnxTime).GetDate())
			modIleak = float(data[1])
			dcuileak[mod][ind_]=modIleak
		for line in linesdcut:
			data = line.strip().split()
			lnxTime = int(data[0])
			ind_ = findClosest(dtime_t_2,TDatime(lnxTime).GetDate())
			modTemp = float(data[1])
			dcutemp[mod][ind_]=modTemp
	print "Damping DCU data into pickle ..."
	pickle.dump(dcuileak,open('DarkSimAllModules_'+simDate+'/dcuileak.p','wb'))
	pickle.dump(dcutemp,open('DarkSimAllModules_'+simDate+'/dcutemp.p','wb'))
else:
	print "Loading DCU data from pickle ..."
	dcuileak=pickle.load(open('DarkSimAllModules_'+simDate+'/dcuileak.p','rb'))
	dcutemp=pickle.load(open('DarkSimAllModules_'+simDate+'/dcutemp.p','rb'))

outDir = 'DarkSimAllModules_'+simDate+'/allModules_'+measDataPath.split('/')[-1]
if not os.path.exists(runDir+'/'+outDir): os.system('mkdir '+runDir+'/'+outDir)
outRfile = TFile(outDir+"/outRfileAllModules.root",'RECREATE')

hi = {'TIB':{},'TID':{},'TOB':{},'TEC':{}}
ht = {'TIB':{},'TID':{},'TOB':{},'TEC':{}}
colors = {'TIB':kOrange,'TID':kGreen+1,'TOB':kBlue,'TEC':kBlack}
XaxisnameI = "Simulated current (#muA)"
YaxisnameI = "Measured current (#muA)"
XaxisnameT = "Simulated temperature (C)"
YaxisnameT = "Measured temperature (C)"
x1=.7 #for legs
y1=0.15
x2=x1+.15
y2=y1+.225

for QuerrDay in range(0,len(dtime_t)):#range(2081,len(dtime_t)):
	querday= dtime_t[QuerrDay]
	qday   = TDatime(querday).GetDay() 
	qmonth = TDatime(querday).GetMonth() 
	qyear  = TDatime(querday).GetYear()
	QDate  = str(qyear)+'_'+str(qmonth)+'_'+str(qday)
	print "Day: %i/%i (%s)" % (QuerrDay,len(dtime_t),QDate)
	if QDate not in datesToPlot: continue
	print "        Plotting this date...."
	
	#*****************Data Extraction*******************************
	for key in hi.keys():
		hi[key],ht[key]={},{}
		hi[key][QDate] = TH1D('hi_'+key+'_'+QDate, '', 100,-1,1)
		ht[key][QDate] = TH1D('ht_'+key+'_'+QDate, '', 100,-0.02,0.02)
	
	detid_ileak = {}
	ileak_sim = {}
	ileak_dat = {}
	ileak_count = {}
	detid_temp = {}
	temp_sim = {}
	temp_dat = {}
	temp_count = {}
	for key in hi.keys():
		detid_ileak[key] = []
		ileak_sim[key] = []
		ileak_dat[key] = []
		ileak_count[key] = 0
		detid_temp[key] = []
		temp_sim[key] = []
		temp_dat[key] = []
		temp_count[key] = 0
			
	tempMin = 300
	tempMax = -300
	ileakMin = 1e20
	ileakMax = -1e6
	for mod in dcuileak.keys():
		mpart = part[mod][:3]
		if mod not in ileakc_t_on.keys(): continue
		if not dcuileak[mod][QuerrDay]>0: continue
		#print ileakc_t_on[mod][QuerrDay],dcuileak[mod][QuerrDay],temp_t_on[mod][QuerrDay],dcutemp[mod][QuerrDay]
		if dcutemp[mod][QuerrDay]<=-25: continue
		#leakage current:
		if scaleCurrentToMeasTemp: currentScaleMeasTemp = LeakCorrection(dcutemp[mod][QuerrDay]+273.16,293.16)
		else: currentScaleMeasTemp = LeakCorrection(temp_t_on[mod][QuerrDay],293.16)
		simLeak = ileakc_t_on[mod][QuerrDay]*1e3*currentScaleMeasTemp
		meaLeak = dcuileak[mod][QuerrDay]#*1e3
		#temperature:
		simTemp = temp_t_on[mod][QuerrDay]
		meaTemp = dcutemp[mod][QuerrDay]+273.16
		#deviations:
		leak_dev = (simLeak-meaLeak)/meaLeak
		temp_dev = (simTemp-meaTemp)/meaTemp
		if temp_dev<-0.025:
			print mpart,mod,simTemp,meaTemp,temp_dev
		#print simTemp,meaTemp,temp_dev
		#clean outliers:
		if abs(leak_dev)>0.5: continue
		detid_ileak[mpart].append(mod)
		ileak_sim[mpart].append(simLeak)
		ileak_dat[mpart].append(meaLeak)
		hi[mpart][QDate].Fill(leak_dev)
		ileak_count[mpart]+=1
		if ileakMin>simLeak: ileakMin = simLeak
		if ileakMin>meaLeak: ileakMin = meaLeak
		if ileakMax<simLeak: ileakMax = simLeak
		if ileakMax<meaLeak: ileakMax = meaLeak
		ileakMax = min([ileakMax,5000])
		detid_temp[mpart].append(mod)
		temp_sim[mpart].append(simTemp-273.16)
		temp_dat[mpart].append(meaTemp-273.16)
		ht[mpart][QDate].Fill(temp_dev)
		temp_count[mpart]+=1
		if tempMin>(simTemp-273.16): tempMin = (simTemp-273.16)
		if tempMin>(meaTemp-273.16): tempMin = (meaTemp-273.16)
		if tempMax<(simTemp-273.16): tempMax = (simTemp-273.16)
		if tempMax<(meaTemp-273.16): tempMax = (meaTemp-273.16)
		#tempMin = max([tempMin,-50])
		#tempMax = min([tempMax,50])
	
	plotIleak = True
	plotTemp  = True
	if all([ileak_count[item]==0 for item in ileak_count.keys()]): 
		print "ileak all zero"
		plotIleak = False
	if all([temp_count[item]==0 for item in temp_count.keys()]): 
		print "temp all zero"
		plotTemp = False
	if plotIleak or plotTemp:
		Igr = {}#leakage current graphs
		for par in hi.keys():
			if ileak_count[par]==0: ileak_count[par],ileak_sim[par],ileak_dat[par]=1,[0],[0]
			Igr[par] = TGraph(ileak_count[par],np.array(ileak_sim[par]),np.array(ileak_dat[par]))
			Igr[par].SetName('gri_'+par+'_'+QDate)
			Igr[par].SetMarkerColor(colors[par])
			Igr[par].SetFillColor(colors[par])
			Igr[par].SetMarkerStyle(8)
			Igr[par].SetMarkerSize(0.3)

		mgnI = TMultiGraph()
		mgnI.SetTitle("")#Simulated and measured data on "+QDate)
		mgnI.Add(Igr['TID'],"p")
		mgnI.Add(Igr['TIB'],"p")
		mgnI.Add(Igr['TOB'],"p")
		mgnI.Add(Igr['TEC'],"p")
		
		Tgr = {}#temperature graphs
		for par in ht.keys():
			if temp_count[par]==0: temp_count[par],temp_sim[par],temp_dat[par]=1,[0],[0]
			Tgr[par] = TGraph(temp_count[par],np.array(temp_sim[par]),np.array(temp_dat[par]))
			Tgr[par].SetName('grt_'+par+'_'+QDate)
			Tgr[par].SetMarkerColor(colors[par])
			Tgr[par].SetFillColor(colors[par])
			Tgr[par].SetMarkerStyle(8)
			Tgr[par].SetMarkerSize(0.3)
		
		mgnT = TMultiGraph()
		mgnT.SetTitle("")#Simulated and measured data on "+QDate)
		mgnT.Add(Tgr['TID'],"p")
		mgnT.Add(Tgr['TIB'],"p")
		mgnT.Add(Tgr['TOB'],"p")
		mgnT.Add(Tgr['TEC'],"p")
	
		canv = TCanvas(QDate,QDate,1200,1200)
		gStyle.SetFillColor(kWhite)
		gStyle.SetStatFormat("6.2g")
		title = TPaveLabel(0.1,0.96,0.9,0.99,QDate)
		title.SetBorderSize(0)
		title.SetFillColor(gStyle.GetTitleFillColor())
		title.Draw()
		canv.Divide(2,2)
	
		canv.cd(1).SetGrid()#leakage current pad
		mgnI.Draw("AP")
		mgnI.GetXaxis().SetTitle(XaxisnameI)
		mgnI.GetYaxis().SetTitle(YaxisnameI)
		mgnI.GetXaxis().SetLimits(ileakMin,ileakMax)
		mgnI.GetHistogram().SetMinimum(ileakMin)
		mgnI.GetHistogram().SetMaximum(ileakMax)
		mgnI.GetYaxis().SetTitleOffset(1.5)
		legI = TLegend(x1,y1,x2,y2)
		legI.AddEntry(Igr['TIB'],"TIB","f")
		legI.AddEntry(Igr['TOB'],"TOB","f")
		legI.AddEntry(Igr['TID'],"TID","f")
		legI.AddEntry(Igr['TEC'],"TEC","f")
		legI.SetTextFont(10)
		legI.Draw()
		
		canv.cd(2).SetGrid()#temperature pad
		mgnT.Draw("AP")
		mgnT.GetXaxis().SetTitle(XaxisnameT)
		mgnT.GetYaxis().SetTitle(YaxisnameT)
		mgnT.GetXaxis().SetLimits(tempMin,tempMax)
		mgnT.GetHistogram().SetMinimum(tempMin)
		mgnT.GetHistogram().SetMaximum(tempMax)
		legT = TLegend(x1,y1,x2,y2)
		legT.AddEntry(Tgr['TIB'],"TIB","f")
		legT.AddEntry(Tgr['TOB'],"TOB","f")
		legT.AddEntry(Tgr['TID'],"TID","f")
		legT.AddEntry(Tgr['TEC'],"TEC","f")
		legT.SetTextFont(10)
		legT.Draw()
	
		canv.cd(3).SetGrid()#pull for leakage current
		histMax = 1.1*max(hi['TIB'][QDate].GetMaximum(),hi['TID'][QDate].GetMaximum(),hi['TOB'][QDate].GetMaximum(),hi['TEC'][QDate].GetMaximum())
		hi['TIB'][QDate].Draw()
		hi['TIB'][QDate].GetXaxis().SetTitle("(sim-data)/data")
		hi['TIB'][QDate].GetYaxis().SetTitle("Entries")
		hi['TIB'][QDate].GetYaxis().SetTitleOffset(1.5)
		hi['TIB'][QDate].SetMaximum(histMax)
		hi['TIB'][QDate].SetLineColor(colors['TIB'])
		canv.GetPad(1).Update()
		statsI1 = hi['TIB'][QDate].GetListOfFunctions().FindObject("stats").Clone("statsI1")
		statsI1.SetY1NDC(.33)
		statsI1.SetY2NDC(.48)
		statsI1.SetTextColor(colors['TIB'])
		hi['TOB'][QDate].Draw("SAMES")
		hi['TOB'][QDate].SetLineColor(colors['TOB'])
		canv.GetPad(1).Update()
		statsI2 = hi['TOB'][QDate].GetListOfFunctions().FindObject("stats").Clone("statsI2")
		statsI2.SetY1NDC(.48)
		statsI2.SetY2NDC(.63)
		statsI2.SetTextColor(colors['TOB'])
		hi['TID'][QDate].Draw("SAMES")
		hi['TID'][QDate].SetLineColor(colors['TID'])
		canv.GetPad(1).Update()
		statsI3 = hi['TID'][QDate].GetListOfFunctions().FindObject("stats").Clone("statsI3")
		statsI3.SetY1NDC(.63)
		statsI3.SetY2NDC(.78)
		statsI3.SetTextColor(colors['TID'])
		hi['TEC'][QDate].Draw("SAMES")
		hi['TEC'][QDate].SetLineColor(colors['TEC'])
		canv.GetPad(1).Update()
		statsI4 = hi['TEC'][QDate].GetListOfFunctions().FindObject("stats").Clone("statsI4")
		statsI4.SetTextColor(colors['TEC'])
		statsI1.Draw()
		statsI2.Draw()
		statsI3.Draw()
		statsI4.Draw()
	
		canv.cd(4).SetGrid()#pull for temperature
		histMax = 1.1*max(ht['TIB'][QDate].GetMaximum(),ht['TID'][QDate].GetMaximum(),ht['TOB'][QDate].GetMaximum(),ht['TEC'][QDate].GetMaximum())
		ht['TIB'][QDate].Draw()
		ht['TIB'][QDate].GetXaxis().SetTitle("(sim-data)/data")
		ht['TIB'][QDate].GetYaxis().SetTitle("Entries")
		ht['TIB'][QDate].GetYaxis().SetTitleOffset(1.5)
		ht['TIB'][QDate].SetMaximum(histMax)
		ht['TIB'][QDate].SetLineColor(colors['TIB'])
		canv.GetPad(1).Update()
		statsT1 = ht['TIB'][QDate].GetListOfFunctions().FindObject("stats").Clone("statsT1")
		statsT1.SetY1NDC(.33)
		statsT1.SetY2NDC(.48)
		statsT1.SetTextColor(colors['TIB'])
		ht['TOB'][QDate].Draw("SAMES")
		ht['TOB'][QDate].SetLineColor(colors['TOB'])
		canv.GetPad(1).Update()
		statsT2 = ht['TOB'][QDate].GetListOfFunctions().FindObject("stats").Clone("statsT2")
		statsT2.SetY1NDC(.48)
		statsT2.SetY2NDC(.63)
		statsT2.SetTextColor(colors['TOB'])
		ht['TID'][QDate].Draw("SAMES")
		ht['TID'][QDate].SetLineColor(colors['TID'])
		canv.GetPad(1).Update()
		statsT3 = ht['TID'][QDate].GetListOfFunctions().FindObject("stats").Clone("statsT3")
		statsT3.SetY1NDC(.63)
		statsT3.SetY2NDC(.78)
		statsT3.SetTextColor(colors['TID'])
		ht['TEC'][QDate].Draw("SAMES")
		ht['TEC'][QDate].SetLineColor(colors['TEC'])
		canv.GetPad(1).Update()
		statsT4 = ht['TEC'][QDate].GetListOfFunctions().FindObject("stats").Clone("statsT4")
		statsT4.SetTextColor(colors['TEC'])
		statsT1.Draw()
		statsT2.Draw()
		statsT3.Draw()
		
		canv.cd()
		title.Draw()

		canv.SaveAs(outDir+"/"+QDate+".png")
		canv.SaveAs(outDir+"/"+QDate+".pdf")
		
		for par in Igr.keys():
			Igr[par].Write()
			Tgr[par].Write()
			hi[par][QDate].Write()
			ht[par][QDate].Write()

outRfile.Close()
simFile.Close()
	
print "***************************** DONE *********************************"
  
