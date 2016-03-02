#!/usr/bin/python

import os,sys,pickle
import numpy as np
from ROOT import *
gROOT.SetBatch(1)

##################################################################################################################
# The code looks for the input simulation tree in "DarkSimAllModules_<simDate>/DarkSimAllModules_<simDate>.root"
# The output files will be in "DarkSimAllModules_<simDate>/plotAllModules/". 
##################################################################################################################

#******************************Input to edit******************************************************
measDataPath = "../iLeakSim_Feb16_leakCalcV1/MeasData/AllModules"
simDate = "2016_3_2"
Dates=["02-04-2012","30-01-2013","11-12-2015"]
IleakMax=[400.,2000.,200.]
TempMax=[50.,50.,20.]

plotBadModules=False
removeBadModules=False # This will remove the modules with too high and too low temperature and leakage current. It doesn't remove all of the outliers!
readTree=False # This needs to be true if running the code on the tree for the first time. It will dump what's read from tree into pickle files and these can be loaded if this option set to "False"
scaleCurrentToMeasTemp = True # Scale current to measured temperature (Check how this is done!!!! The default method assumes that the simulated current is at 20C)

#READ IN TREE
InTreeSim="DarkSimAllModules_"+simDate+"/DarkSimAllModules_"+simDate+".root"
print "Input Tree: ",InTreeSim
simFile = TFile(InTreeSim,'READ')
simTree = simFile.Get('tree')
print "/////////////////////////////////////////////////////////////////"
print "Number of Simulated Modules in the tree: ", simTree.GetEntries()
print "/////////////////////////////////////////////////////////////////"
simTree.GetEntry(0)
print type(simTree.DETID_T), type(simTree.ileakc_t_on), type(simTree.dtime_t)
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

hi_all,hi_TIB,hi_TID,hi_TOB,hi_TEC,ht_all,ht_TIB,ht_TID,ht_TOB,ht_TEC={},{},{},{},{},{},{},{},{},{}
hi_badmodules,ht_badmodules={},{}
outlierModules_I,outlierModules_T={},{}
for q in range(len(Dates)):
	QDate  = Dates[q]
	#if QDate!='11-12-2015': continue
	qday   = int(QDate[:2])
	qmonth = int(QDate[3:5])
	qyear  = int(QDate[6:])
	querday = TDatime(qyear,qmonth,qday,0,0,1).Convert()
		
	if not os.path.exists(runDir+'/DarkSimAllModules_'+simDate+'/plotAllModules/'): os.system('mkdir DarkSimAllModules_'+simDate+'/plotAllModules/')
	saveNameI = "DarkSimAllModules_"+simDate+"/plotAllModules/Ileak_"+QDate
	saveNameT = "DarkSimAllModules_"+simDate+"/plotAllModules/Temp_"+QDate
	outRfile = TFile("DarkSimAllModules_"+simDate+"/plotAllModules/outRfile"+QDate+".root",'RECREATE')
	
	#READ IN DATA
	InFileDatA_I=measDataPath+"/Ileak/Ileak_"+QDate+".txt"
	InFileDatA_T=measDataPath+"/Temp/Temp_"+QDate+".txt"
	fIdata = open(InFileDatA_I, 'r')
	linesI = fIdata.readlines()
	fIdata.close()
	fTdata = open(InFileDatA_T, 'r')
	linesT = fTdata.readlines()
	fTdata.close()
	
	detid_dd_I=[]
	ileak_dd=[]
	for line in linesI:
		data = line.strip().split()
		try: 
			detid_dd_I.append(int(data[0]))
			ileak_dd.append(float(data[1]))
		except: print "Warning! => Unknown data format: ",data,"in", InFileDatA_I
	detid_dd_T=[]
	temp_dd=[]
	for line in linesT:
		data = line.strip().split() 
		try:
			detid_dd_T.append(int(data[0]))
			temp_dd.append(float(data[1]))
		except: print "Warning! => Unknown data format: ",data,"in", InFileDatA_T
	
	#*****************Data Extraction*******************************
	hi_all[QDate] = TH1D('hi_all_'+QDate, '', 100,-1,1)
	hi_TOB[QDate] = TH1D('hi_TOB_'+QDate, '', 100,-1,1)
	hi_TIB[QDate] = TH1D('hi_TIB_'+QDate, '', 100,-1,1)
	hi_TID[QDate] = TH1D('hi_TID_'+QDate, '', 100,-1,1)
	hi_TEC[QDate] = TH1D('hi_TEC_'+QDate, '', 100,-1,1)
	ht_all[QDate] = TH1D('ht_all_'+QDate, '', 100,-1,1)
	ht_TOB[QDate] = TH1D('ht_TOB_'+QDate, '', 100,-1,1)
	ht_TIB[QDate] = TH1D('ht_TIB_'+QDate, '', 100,-1,1)
	ht_TID[QDate] = TH1D('ht_TID_'+QDate, '', 100,-1,1)
	ht_TEC[QDate] = TH1D('ht_TEC_'+QDate, '', 100,-1,1)
	hi_badmodules[QDate] = TH1D('hi_badmodules'+QDate, '', 100,-1,1)
	ht_badmodules[QDate] = TH1D('ht_badmodules'+QDate, '', 100,-1,1)
	outlierModules_I[QDate] = []
	outlierModules_T[QDate] = []
	
	for w in range(len(dtime_t)):
		if dtime_t[w]<=querday and dtime_t[w+1]>querday:
			QuerrDay=w
			Datum = TDatime(dtime_t[QuerrDay+1])
			print "////////////////////////////////////////////////////////////////////////"
			print "************************************************************************"
			print "Data/Simulation on ",Datum.GetDate()," , ",QuerrDay, "days since simulation started"
			print "************************************************************************"
			print "////////////////////////////////////////////////////////////////////////"
			break
			
	try: print QuerrDay
	except: 
		print QDate, "not found in the tree"
		continue
	
	detid_f1,detid_f2,detid_f3,detid_f4             = [],[],[],[]
	ileakson_f1,ileakson_f2,ileakson_f3,ileakson_f4 = [],[],[],[]
	isimbadmods,idatbadmods,tsimbadmods,tdatbadmods = [],[],[],[]
	ileakd_f1,ileakd_f2,ileakd_f3,ileakd_f4         = [],[],[],[]
	ts_f1,ts_f2,ts_f3,ts_f4,td_f1,td_f2,td_f3,td_f4 = [],[],[],[],[],[],[],[]
	i1,i2,i3,i4,t1,t2,t3,t4 = 0,0,0,0,0,0,0,0
	print "************* Started matching data and simulation! *************"
	badModFileI = open(saveNameI+'_outliers.txt','w')
	modDataFileIForTKmap = open(saveNameI+'.txt','w')
	
	badModFileT = open(saveNameT+'_outliers.txt','w')
	modDataFileTForTKmap = open(saveNameT+'.txt','w')
	
	nMods=0
	for module in detid_dd_I:
		if module not in detid_dd_T or module not in detid_t: continue
		if removeBadModules:
			if ileakc_t_on[module][QuerrDay]*1000<0 or ileakc_t_on[module][QuerrDay]>1000: continue
			if temp_t_on[module][QuerrDay]<263.16 or temp_t_on[module][QuerrDay]>323.16: continue
		iLeakMatchInd = detid_dd_I.index(module)
		tempMatchInd  = detid_dd_T.index(module)
		if removeBadModules:
			if ileak_dd[iLeakMatchInd]>2000 or ileak_dd[iLeakMatchInd]<0: continue
			if temp_dd[tempMatchInd]<-20. or temp_dd[tempMatchInd]>50.: continue
		if scaleCurrentToMeasTemp: currentScaleMeasTemp = LeakCorrection(temp_dd[tempMatchInd]+273.16,293.16)
		if not scaleCurrentToMeasTemp: currentScaleMeasTemp = LeakCorrection(temp_t_on[module][QuerrDay],293.16)
		if partition_t[module]==1 or partition_t[module]==2: # TIB
			detid_f1.append(module)
			ileakson_f1.append(ileakc_t_on[module][QuerrDay]*1000*currentScaleMeasTemp)
			ileakd_f1.append(ileak_dd[iLeakMatchInd])
			hi_TIB[QDate].Fill((ileakc_t_on[module][QuerrDay]*1000*currentScaleMeasTemp-ileak_dd[iLeakMatchInd])/ileak_dd[iLeakMatchInd])
			i1+=1
			ts_f1.append(temp_t_on[module][QuerrDay]-273.16)
			td_f1.append(temp_dd[tempMatchInd])
			ht_TIB[QDate].Fill((temp_t_on[module][QuerrDay]-273.16-temp_dd[tempMatchInd])/temp_dd[tempMatchInd])
			t1+=1
		if partition_t[module]==3 or partition_t[module]==4: # TOB
			detid_f2.append(module)
			ileakson_f2.append(ileakc_t_on[module][QuerrDay]*1000*currentScaleMeasTemp)
			ileakd_f2.append(ileak_dd[iLeakMatchInd])
			hi_TOB[QDate].Fill((ileakc_t_on[module][QuerrDay]*1000*currentScaleMeasTemp-ileak_dd[iLeakMatchInd])/ileak_dd[iLeakMatchInd])
			i2+=1
			ts_f2.append(temp_t_on[module][QuerrDay]-273.16)
			td_f2.append(temp_dd[tempMatchInd])
			ht_TOB[QDate].Fill((temp_t_on[module][QuerrDay]-273.16-temp_dd[tempMatchInd])/temp_dd[tempMatchInd])
			t2+=1
		if partition_t[module]==5 or partition_t[module]==6: # TID
			detid_f3.append(module)
			ileakson_f3.append(ileakc_t_on[module][QuerrDay]*1000*currentScaleMeasTemp)
			ileakd_f3.append(ileak_dd[iLeakMatchInd])
			hi_TID[QDate].Fill((ileakc_t_on[module][QuerrDay]*1000*currentScaleMeasTemp-ileak_dd[iLeakMatchInd])/ileak_dd[iLeakMatchInd])
			i3+=1
			ts_f3.append(temp_t_on[module][QuerrDay]-273.16)
			td_f3.append(temp_dd[tempMatchInd])
			ht_TID[QDate].Fill((temp_t_on[module][QuerrDay]-273.16-temp_dd[tempMatchInd])/temp_dd[tempMatchInd])
			t3+=1
		if partition_t[module]==7 or partition_t[module]==8: # TEC
			detid_f4.append(module)
			ileakson_f4.append(ileakc_t_on[module][QuerrDay]*1000*currentScaleMeasTemp)
			ileakd_f4.append(ileak_dd[iLeakMatchInd])
			hi_TEC[QDate].Fill((ileakc_t_on[module][QuerrDay]*1000*currentScaleMeasTemp-ileak_dd[iLeakMatchInd])/ileak_dd[iLeakMatchInd])
			i4+=1
			ts_f4.append(temp_t_on[module][QuerrDay]-273.16)
			td_f4.append(temp_dd[tempMatchInd])
			ht_TEC[QDate].Fill((temp_t_on[module][QuerrDay]-273.16-temp_dd[tempMatchInd])/temp_dd[tempMatchInd])
			t4+=1
		pullIleak=(ileakc_t_on[module][QuerrDay]*1000*currentScaleMeasTemp-ileak_dd[iLeakMatchInd])/ileak_dd[iLeakMatchInd]
		if abs(pullIleak) > 0.4:
			isimbadmods.append(ileakc_t_on[module][QuerrDay]*1000*currentScaleMeasTemp)
			idatbadmods.append(ileak_dd[iLeakMatchInd])
			badModFileI.write('Mod Number: '+str(module)+'\t'+'IleakSim = '+str(ileakc_t_on[module][QuerrDay]*1000*currentScaleMeasTemp)+'\t'+'IleakData = '+str(ileak_dd[iLeakMatchInd])+'\t'+'TempSim = '+str(temp_t_on[module][QuerrDay]-273.16)+'\t'+'TempData = '+str(temp_dd[tempMatchInd])+'\n')
			outlierModules_I[QDate].append(module)
		modDataFileIForTKmap.write('Mod Number: '+str(module)+'\t'+'IleakSim = '+str(ileakc_t_on[module][QuerrDay]*1000*currentScaleMeasTemp)+'\t'+'IleakData = '+str(ileak_dd[iLeakMatchInd])+'\n')
		pullTemp=(temp_t_on[module][QuerrDay]-273.16-temp_dd[tempMatchInd])/temp_dd[tempMatchInd]
		#if abs(pullTemp) > 0.4 and abs(temp_t_on[module][QuerrDay]-273.16-temp_dd[tempMatchInd])>2:
		if abs(pullTemp) > 0.6:
			tsimbadmods.append(temp_t_on[module][QuerrDay]-273.16)
			tdatbadmods.append(temp_dd[tempMatchInd])
			badModFileT.write('Mod Number: '+str(module)+'\t'+'TempSim = '+str(temp_t_on[module][QuerrDay]-273.16)+'\t'+'TempData = '+str(temp_dd[tempMatchInd])+'\n')
			outlierModules_T[QDate].append(module)
		modDataFileTForTKmap.write('Mod Number: '+str(module)+'\t'+'TempSim = '+str(temp_t_on[module][QuerrDay]-273.16)+'\t'+'TempData = '+str(temp_dd[tempMatchInd])+'\n')
		hi_all[QDate].Fill(pullIleak)
		ht_all[QDate].Fill(pullTemp)
		nMods+=1
		if nMods%1000==0: print "Finished matching detids for", nMods, "/", simTree.GetEntries(), "modules!"
	
	print "*** Finished matching data and simulation! Plotting results now! ***"
	I1n = TGraph(i1,np.array(ileakson_f1),np.array(ileakd_f1))
	I1n.SetMarkerColor(kRed)
	I1n.SetFillColor(kRed)
	I1n.SetMarkerStyle(8)
	I1n.SetMarkerSize(0.3)
	I2n = TGraph(i2,np.array(ileakson_f2),np.array(ileakd_f2))
	I2n.SetMarkerColor(kBlue)
	I2n.SetFillColor(kBlue)
	I2n.SetMarkerStyle(8)
	I2n.SetMarkerSize(0.3)
	I3n = TGraph(i3,np.array(ileakson_f3),np.array(ileakd_f3))
	I3n.SetMarkerColor(kGreen)
	I3n.SetFillColor(kGreen)
	I3n.SetMarkerStyle(8)
	I3n.SetMarkerSize(0.3)
	I4n = TGraph(i4,np.array(ileakson_f4),np.array(ileakd_f4))
	I4n.SetMarkerColor(kBlack)
	I4n.SetFillColor(kBlack)
	I4n.SetMarkerStyle(8)
	I4n.SetMarkerSize(0.3)
	if plotBadModules:
		Ibad = TGraph(len(isimbadmods),np.array(isimbadmods),np.array(idatbadmods))
		Ibad.SetMarkerColor(kYellow)
		Ibad.SetFillColor(kYellow)
		Ibad.SetMarkerStyle(8)
		Ibad.SetMarkerSize(0.3)
	
	T1n = TGraph(t1,np.array(ts_f1),np.array(td_f1))
	T1n.SetMarkerColor(kRed)
	T1n.SetFillColor(kRed)
	T1n.SetMarkerStyle(8)
	T1n.SetMarkerSize(0.3)
	T2n = TGraph(t2,np.array(ts_f2),np.array(td_f2))
	T2n.SetMarkerColor(kBlue)
	T2n.SetFillColor(kBlue)
	T2n.SetMarkerStyle(8)
	T2n.SetMarkerSize(0.3)
	T3n = TGraph(t3,np.array(ts_f3),np.array(td_f3))
	T3n.SetMarkerColor(kGreen)
	T3n.SetFillColor(kGreen)
	T3n.SetMarkerStyle(8)
	T3n.SetMarkerSize(0.3)
	T4n = TGraph(t4,np.array(ts_f4),np.array(td_f4))
	T4n.SetMarkerColor(kBlack)
	T4n.SetFillColor(kBlack)
	T4n.SetMarkerStyle(8)
	T4n.SetMarkerSize(0.3)
	if plotBadModules:
		Tbad = TGraph(len(tsimbadmods),np.array(tsimbadmods),np.array(tdatbadmods))
		Tbad.SetMarkerColor(kYellow)
		Tbad.SetFillColor(kYellow)
		Tbad.SetMarkerStyle(8)
		Tbad.SetMarkerSize(0.3)
	
	XaxisnameI = "Simulated current (#muA)"
	YaxisnameI = "Measured current (#muA)"
	XaxisnameT = "Simulated temperature (C)"
	YaxisnameT = "Measured temperature (C)"
	
	mgnI = TMultiGraph()
	mgnI.SetTitle("Simulated and measured data on "+QDate)
	mgnI.Add(I3n,"p")
	mgnI.Add(I1n,"p")
	mgnI.Add(I2n,"p")
	mgnI.Add(I4n,"p")
	if plotBadModules: mgnI.Add(Ibad,"p")
	
	mgnT = TMultiGraph()
	mgnT.SetTitle("Simulated and measured data on "+QDate)
	mgnT.Add(T3n,"p")
	mgnT.Add(T1n,"p")
	mgnT.Add(T2n,"p")
	mgnT.Add(T4n,"p")
	if plotBadModules: mgnT.Add(Tbad,"p")
	
	cI = TCanvas("cI","Cross Check Corrected Current",400,800)
	gStyle.SetFillColor(kWhite)
	cI.Divide(1,2)
	
	cI.cd(1).SetGrid()
	mgnI.Draw("AP")
	mgnI.GetXaxis().SetTitle(XaxisnameI)
	mgnI.GetYaxis().SetTitle(YaxisnameI)
	mgnI.GetXaxis().SetLimits(0.,IleakMax[q])
	mgnI.GetHistogram().SetMinimum(0.)
	mgnI.GetHistogram().SetMaximum(IleakMax[q])
	mgnI.GetYaxis().SetTitleOffset(1.5)
	x1=.7
	y1=0.15
	x2=x1+.15
	y2=y1+.225
	legI = TLegend(x1,y1,x2,y2)
	legI.AddEntry(I1n,"TIB","f")
	legI.AddEntry(I2n,"TOB","f")
	legI.AddEntry(I3n,"TID","f")
	legI.AddEntry(I4n,"TEC","f")
	if plotBadModules: legI.AddEntry(Ibad,"Outliers","f")
	legI.SetTextFont(10)
	legI.Draw()
	
	cI.cd(2).SetGrid()
# 	hi_all[QDate].Draw()
# 	hi_all[QDate].GetXaxis().SetTitle("(sim-data)/data")
# 	hi_all[QDate].GetYaxis().SetTitle("Entries")
# 	hi_all[QDate].GetYaxis().SetTitleOffset(1.5)
	hi_TIB[QDate].Draw()
	hi_TIB[QDate].GetXaxis().SetTitle("(sim-data)/data")
	hi_TIB[QDate].GetYaxis().SetTitle("Entries")
	hi_TIB[QDate].GetYaxis().SetTitleOffset(1.5)
	hi_TIB[QDate].SetMaximum(1.1*max(hi_TIB[QDate].GetMaximum(),hi_TID[QDate].GetMaximum(),hi_TOB[QDate].GetMaximum(),hi_TEC[QDate].GetMaximum()))
	hi_TIB[QDate].SetLineColor(kRed)
	cI.GetPad(1).Update()
	statsI1 = hi_TIB[QDate].GetListOfFunctions().FindObject("stats").Clone("statsI1")
	statsI1.SetY1NDC(.33)
	statsI1.SetY2NDC(.48)
	statsI1.SetTextColor(kRed)
	hi_TOB[QDate].Draw("SAMES")
	hi_TOB[QDate].SetLineColor(kBlue)
	cI.GetPad(1).Update()
	statsI2 = hi_TOB[QDate].GetListOfFunctions().FindObject("stats").Clone("statsI2")
	statsI2.SetY1NDC(.48)
	statsI2.SetY2NDC(.63)
	statsI2.SetTextColor(kBlue)
	hi_TID[QDate].Draw("SAMES")
	hi_TID[QDate].SetLineColor(kGreen)
	cI.GetPad(1).Update()
	statsI3 = hi_TID[QDate].GetListOfFunctions().FindObject("stats").Clone("statsI3")
	statsI3.SetY1NDC(.63)
	statsI3.SetY2NDC(.78)
	statsI3.SetTextColor(kGreen)
	hi_TEC[QDate].Draw("SAMES")
	hi_TEC[QDate].SetLineColor(kBlack)
	cI.GetPad(1).Update()
	statsI4 = hi_TEC[QDate].GetListOfFunctions().FindObject("stats").Clone("statsI4")
	statsI4.SetTextColor(kBlack)
	statsI1.Draw()
	statsI2.Draw()
	statsI3.Draw()
	statsI4.Draw()
	cI.Write()
	cI.cd(1).Write()
	cI.cd(2).Write()
	cI.SaveAs(saveNameI+".png")
	cI.SaveAs(saveNameI+".pdf")
	
	cT = TCanvas("cT","Cross Check Corrected Temperature",400,800)
	gStyle.SetFillColor(kWhite)
	cT.Divide(1,2)
	
	cT.cd(1).SetGrid()
	mgnT.Draw("AP")
	mgnT.GetXaxis().SetTitle(XaxisnameT)
	mgnT.GetYaxis().SetTitle(YaxisnameT)
	mgnT.GetXaxis().SetLimits(-15.,TempMax[q])
	mgnT.GetHistogram().SetMinimum(-15.)
	mgnT.GetHistogram().SetMaximum(TempMax[q])
	legT = TLegend(x1,y1,x2,y2)
	legT.AddEntry(T1n,"TIB","f")
	legT.AddEntry(T2n,"TOB","f")
	legT.AddEntry(T3n,"TID","f")
	legT.AddEntry(T4n,"TEC","f")
	if plotBadModules: legT.AddEntry(Tbad,"Outliers","f")
	legT.SetTextFont(10)
	legT.Draw()
	
	cT.cd(2).SetGrid()
# 	ht_all[QDate].Draw()
# 	ht_all[QDate].GetXaxis().SetTitle("(sim-data)/data")
# 	ht_all[QDate].GetYaxis().SetTitle("Entries")
# 	ht_all[QDate].GetYaxis().SetTitleOffset(1.5)
	ht_TIB[QDate].Draw()
	ht_TIB[QDate].GetXaxis().SetTitle("(sim-data)/data")
	ht_TIB[QDate].GetYaxis().SetTitle("Entries")
	ht_TIB[QDate].GetYaxis().SetTitleOffset(1.5)
	ht_TIB[QDate].SetMaximum(1.1*max(ht_TIB[QDate].GetMaximum(),ht_TID[QDate].GetMaximum(),ht_TOB[QDate].GetMaximum(),ht_TEC[QDate].GetMaximum()))
	ht_TIB[QDate].SetLineColor(kRed)
	cT.GetPad(1).Update()
	statsT1 = ht_TIB[QDate].GetListOfFunctions().FindObject("stats").Clone("statsT1")
	statsT1.SetY1NDC(.33)
	statsT1.SetY2NDC(.48)
	statsT1.SetTextColor(kRed)
	ht_TOB[QDate].Draw("SAMES")
	ht_TOB[QDate].SetLineColor(kBlue)
	cT.GetPad(1).Update()
	statsT2 = ht_TOB[QDate].GetListOfFunctions().FindObject("stats").Clone("statsT2")
	statsT2.SetY1NDC(.48)
	statsT2.SetY2NDC(.63)
	statsT2.SetTextColor(kBlue)
	ht_TID[QDate].Draw("SAMES")
	ht_TID[QDate].SetLineColor(kGreen)
	cT.GetPad(1).Update()
	statsT3 = ht_TID[QDate].GetListOfFunctions().FindObject("stats").Clone("statsT3")
	statsT3.SetY1NDC(.63)
	statsT3.SetY2NDC(.78)
	statsT3.SetTextColor(kGreen)
	ht_TEC[QDate].Draw("SAMES")
	ht_TEC[QDate].SetLineColor(kBlack)
	cT.GetPad(1).Update()
	statsT4 = ht_TEC[QDate].GetListOfFunctions().FindObject("stats").Clone("statsT4")
	statsT4.SetTextColor(kBlack)
	statsT1.Draw()
	statsT2.Draw()
	statsT3.Draw()
	cT.Write()
	cT.cd(1).Write()
	cT.cd(2).Write()
	cT.SaveAs(saveNameT+".png")
	cT.SaveAs(saveNameT+".pdf")
	hi_TOB[QDate].Write()
	hi_TIB[QDate].Write()
	hi_TID[QDate].Write()
	hi_TEC[QDate].Write()
	ht_TOB[QDate].Write()
	ht_TIB[QDate].Write()
	ht_TID[QDate].Write()
	ht_TEC[QDate].Write()
outRfile.Close()
simFile.Close()
	
print "***************************** DONE *********************************"
  
