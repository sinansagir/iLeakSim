#!/usr/bin/python

from array import array
import os,sys,fnmatch
from ROOT import *

partition = 'TIB' # run for each partition; TIB, TOB, TECp, TECn

#Simulation start and end dates:
startYear,startMonth,startDay = 2011,1,4#2010,3,30
endYear,endMonth,endDay = 2015,12,14

startTDatime=TDatime(startYear,startMonth,startDay,1,0,0)
start=TDatime(startYear,startMonth,startDay,1,0,0).Convert()
endTDatime=TDatime(endYear,endMonth,endDay,1,0,0)
end=TDatime(endYear,endMonth,endDay,1,0,0).Convert()

#Reading PLC readings from silicon --> add more data from different PLCs
fPLC_TSil={}
PLClines_TSil={}
print "READING TSIL FILES ..."
fPLC_TSil[1] = open('PLC_LVandTemp/TEC_minus_1.2.4.2.3_PLC_TSil.csv', 'rU')
fPLC_TSil[2] = open('PLC_LVandTemp/TEC_minus_2.1.1.1.3_PLC_TSil.csv', 'rU')
fPLC_TSil[3] = open('PLC_LVandTemp/TEC_plus_3.1.2.2.3_TSil.csv', 'rU')
fPLC_TSil[4] = open('PLC_LVandTemp/TEC_plus_8.8.4.2.3_TSil.csv', 'rU')
for file in fPLC_TSil.keys(): 
	PLClines_TSil[file] = fPLC_TSil[file].readlines()
	fPLC_TSil[file].close()
	
#In order to cross-check and compare also read Pt1000 readings --> this is the air temperature
fPLC_TAir={}
PLClines_TAir={}
print "READING TAIR FILES ..."
fPLC_TAir[1] = open('PLC_LVandTemp/Monitor_PT1000_Minus_Bottom_Mid_TEC_TAir.csv', 'rU')
fPLC_TAir[2] = open('PLC_LVandTemp/Monitor_PT1000_Minus_Top_Mid_TEC_TAir.csv', 'rU')
fPLC_TAir[3] = open('PLC_LVandTemp/Monitor_PT1000_Plus_Bottom_Mid_TEC_TAir.csv', 'rU')
for file in fPLC_TAir.keys(): 
	PLClines_TAir[file] = fPLC_TAir[file].readlines()
	fPLC_TAir[file].close()

#Reading lumi file
print "READING LUMI ..."
fLumi = open('lumi/Lumi.txt', 'rU')
lumilines = fLumi.readlines()
fLumi.close()
dates = []
tdDatesLumi = []
lumi   = {}
states = {}
statetimes = {}
LVstates = {}
LVstatetimes = {}
PLCtempsTAir = {}
PLCtemptimesTAir = {}
PLCtempsTSil = {}
PLCtemptimesTSil = {}
isTrackerSD = {}
TrackerSDTempAvgTAir = {}
TrackerSDTempAvgTSil = {}
ONdur  = {}
OFFdur = {}
STBdur = {}
SDdur  = {}
for line in lumilines: #append lumi and initialize dictionaries for state and shut-down information
	data = line.strip().split()
	dates.append(TDatime(int(data[1])).GetDate())
	tdDatesLumi.append(int(data[1]))
	lumi[dates[-1]] = float(data[2])
	states[dates[-1]] = []
	statetimes[dates[-1]] = []
	LVstates[dates[-1]] = []
	LVstatetimes[dates[-1]] = []
	PLCtempsTAir[dates[-1]] = []
	PLCtemptimesTAir[dates[-1]] = []
	PLCtempsTSil[dates[-1]] = {}
	PLCtemptimesTSil[dates[-1]] = {}
	TrackerSDTempAvgTSil[dates[-1]] = {}
	for file in PLClines_TSil.keys():
		PLCtempsTSil[dates[-1]][file] = []
		PLCtemptimesTSil[dates[-1]][file] = []
	ONdur[dates[-1]]  = 0
	OFFdur[dates[-1]] = 0
	STBdur[dates[-1]] = 0
	SDdur[dates[-1]]  = 0
states[TDatime(start-86400).GetDate()] = ["ON"] #initialize!
statetimes[TDatime(start-86400).GetDate()] = [start] #initialize!

print "APPENDING TSIL READINGS FOR EACH DAY ..."
for file in PLClines_TSil.keys():
	for line in PLClines_TSil[file]: #append TSil readings for each day to average them later
		data = line.strip().split('"')
		try: TDatime(int(data[1].strip()[:-3])).GetDate(),data[3].strip()
		except: continue
		if TDatime(int(data[1].strip()[:-3])).GetDate() not in dates: continue
		PLCtempsTSil[TDatime(int(data[1].strip()[:-3])).GetDate()][file].append(float(data[3].strip()))
		PLCtemptimesTSil[TDatime(int(data[1].strip()[:-3])).GetDate()][file].append(int(data[1].strip()[:-3]))

print "APPENDING TAIR READINGS FOR EACH DAY ..."	
for file in PLClines_TAir.keys():
	for line in PLClines_TAir[file]: #append TAir readings for each day to average them later
		data = line.strip().split('"')
		try: TDatime(int(data[1].strip()[:-3])).GetDate(),data[3].strip()
		except: continue
		if TDatime(int(data[1].strip()[:-3])).GetDate() not in dates: continue
		PLCtempsTAir[TDatime(int(data[1].strip()[:-3])).GetDate()].append(float(data[3].strip()))
		PLCtemptimesTAir[TDatime(int(data[1].strip()[:-3])).GetDate()].append(int(data[1].strip()[:-3]))

#Read LV status to get the shut-down periods		
# fLV = open('TEC_minus_2.1.1.1.1_LV_Digital.csv', 'rU')
# LVlines = fLV.readlines()
# fLV.close()
# fLV_2 = open('TIB_minus_1.2.1.4_LV_Analog.csv', 'rU')
# LVlines_2 = fLV_2.readlines()
# fLV_2.close()
# fLV_3 = open('TIB_minus_2.2.1.1_LV_Analog.csv', 'rU')
# LVlines_3 = fLV_3.readlines()
# fLV_3.close()
# for line in LVlines:
# 	data = line.strip().split('"')
# 	try: TDatime(int(data[1].strip()[:-3])).GetDate(),data[3].strip()
# 	except: continue
# 	if TDatime(int(data[1].strip()[:-3])).GetDate() not in dates: continue
# 	LVstates[TDatime(int(data[1].strip()[:-3])).GetDate()].append(float(data[3].strip()))
# 	LVstatetimes[TDatime(int(data[1].strip()[:-3])).GetDate()].append(int(data[1].strip()[:-3]))
# for line in LVlines_2:
# 	data = line.strip().split('"')
# 	try: TDatime(int(data[1].strip()[:-3])).GetDate(),data[3].strip()
# 	except: continue
# 	if TDatime(int(data[1].strip()[:-3])).GetDate() not in dates: continue
# 	LVstates[TDatime(int(data[1].strip()[:-3])).GetDate()].append(float(data[3].strip()))
# 	LVstatetimes[TDatime(int(data[1].strip()[:-3])).GetDate()].append(int(data[1].strip()[:-3]))
# for line in LVlines_3:
# 	data = line.strip().split('"')
# 	try: TDatime(int(data[1].strip()[:-3])).GetDate(),data[3].strip()
# 	except: continue
# 	if TDatime(int(data[1].strip()[:-3])).GetDate() not in dates: continue
# 	LVstates[TDatime(int(data[1].strip()[:-3])).GetDate()].append(float(data[3].strip()))
# 	LVstatetimes[TDatime(int(data[1].strip()[:-3])).GetDate()].append(int(data[1].strip()[:-3]))

#Read LV status from WBM CAEN readings		
fLV_WBM= open('PLC_LVandTemp/WBM_DCS_CAEN_LV.txt', 'rU')
LVlines_WBM = fLV_WBM.readlines()
fLV_WBM.close()
print "GETTING LV DATA ..."
for line in LVlines_WBM:
	data = line.strip().split('*')
	try: TDatime(int(data[2].strip())).GetDate(),data[3].strip()
	except: continue
	if TDatime(int(data[2].strip())).GetDate() not in dates: continue
	LVstates[TDatime(int(data[2].strip())).GetDate()].append(data[3].strip())
	LVstatetimes[TDatime(int(data[2].strip())).GetDate()].append(int(data[2].strip()))

#Tracker states (ON, OFF, and STAND-BY) from hours counter in WBM
fstates = open('TrackerStates/'+partition+'_all2011-2015.txt', 'rU')
statelines = fstates.readlines()
fstates.close()
print "GETTING TRACKER STATES ..."
for line in statelines:
	data = line.strip().split('*')
	states[TDatime(int(data[2].strip())).GetDate()].append(data[3].strip())
	statetimes[TDatime(int(data[2].strip())).GetDate()].append(int(data[2].strip()))

#get the shut-down states and average temperatures for each day
print "AVERAGING TEMPERATURE AND GETTING S-D DAYS ..."
timesChangedToSD = 0
for i in range(len(dates)):
	date = dates[i]
	isTrackerSD[date] = 0
	avgTempTAir = 0.
	counterTAir = 0
	for temp in PLCtempsTAir[date]:
		if temp<30. and temp>-20.:
			avgTempTAir+=temp
			counterTAir+=1
	if counterTAir!=0: TrackerSDTempAvgTAir[date]=avgTempTAir/counterTAir
	else: 
		try: TrackerSDTempAvgTAir[date]=TrackerSDTempAvgTAir[dates[i-1]]
		except: TrackerSDTempAvgTAir[date]=13
	avgTempTSil = {}
	counterTSil = {}
	diff = 1.e9
	for file in PLClines_TSil.keys():
		avgTempTSil[file] = 0.
		counterTSil[file] = 0
		for temp in PLCtempsTSil[date][file]:
			if temp<30. and temp>-20.: 
				avgTempTSil[file]+=temp
				counterTSil[file]+=1
		if counterTSil[file]!=0: TrackerSDTempAvgTSil[date][file]=avgTempTSil[file]/counterTSil[file]
		else: 
			try: TrackerSDTempAvgTSil[date][file]=TrackerSDTempAvgTSil[dates[i-1]][file]
			except: TrackerSDTempAvgTSil[date][file]=13
		if abs(TrackerSDTempAvgTAir[date]-TrackerSDTempAvgTSil[date][file])<diff:
			closestToAir=TrackerSDTempAvgTSil[date][file]
			diff=abs(TrackerSDTempAvgTAir[date]-TrackerSDTempAvgTSil[date][file])
	nFiles = 0
	TrackerSDTempAvgTSil[date]['average']=0.
	for file in PLClines_TSil.keys():
		if abs(closestToAir-TrackerSDTempAvgTSil[date][file])<10.: 
			TrackerSDTempAvgTSil[date]['average'] += TrackerSDTempAvgTSil[date][file]
			nFiles+=1
	TrackerSDTempAvgTSil[date]['average']=TrackerSDTempAvgTSil[date]['average']/nFiles
	if len(LVstatetimes[date])==0:
		print "TRACKER SHUT-DOWN:",date
		isTrackerSD[date] = 1
		if len(statetimes[date])!=0:
			doPrint=False
			if i==0:
				if not (len(LVstatetimes[dates[1]])==0 or len(LVstatetimes[dates[2]])==0): doPrint=True
			elif i==1:
				if not (len(LVstatetimes[dates[0]])==0 or len(LVstatetimes[dates[2]])==0 or len(LVstatetimes[dates[3]])==0): doPrint=True
			elif i==len(dates)-2:
				if not (len(LVstatetimes[dates[len(dates)-4]])==0 or len(LVstatetimes[dates[len(dates)-3]])==0 or len(LVstatetimes[dates[len(dates)-1]])==0): doPrint=True
			elif i==len(dates)-1:
				if not (len(LVstatetimes[dates[len(dates)-3]])==0 or len(LVstatetimes[dates[len(dates)-2]])==0): doPrint=True
			else:
				if not (len(LVstatetimes[dates[i-2]])==0 or len(LVstatetimes[dates[i-1]])==0 or len(LVstatetimes[dates[i+1]])==0 or len(LVstatetimes[dates[i+2]])==0): doPrint=True
			if doPrint:
				print "        WRONG SHUT_DOWN PERIOD"
				print "        STATES:", statetimes[date]
				print "        LVs   :", LVstatetimes[date]
				if len(LVstatetimes[dates[i-1]])!=0 or len(LVstatetimes[dates[i+1]])!=0:
					print "        REMOVING THIS S-D STATE SINCE DAYS BEFORE AND/OR AFTER NOT S-D"
					isTrackerSD[date] = 0
	if len(LVstatetimes[date])!=0 and len(statetimes[date])==0 and (len(LVstatetimes[dates[i-1]])==0 or len(LVstatetimes[dates[i-2]])==0) and (len(LVstatetimes[dates[i+1]])==0 or len(LVstatetimes[dates[i+2]])==0):
		print "TRACKER SHUT-DOWN:",date,"CHANGED TO S-D SINCE DAYS BEFORE AND/OR AFTER ARE S-D"
		isTrackerSD[date] = 1
		timesChangedToSD+=1
	if len(LVstatetimes[date])!=0 and len(statetimes[date])==0:
		print 'NO STATE INFORMATION AVAILABLE',date
		print "STATES:", statetimes[date]
		print "LVs   :", LVstatetimes[date]
#sys.exit() 
# gr1 = TGraph(len(PLCtime),array('d',PLCtime),array('d',PLCtemp))
# gr1.SetMarkerColor(kBlue)
# gr1.SetLineColor(kBlue)
# gr1.SetMarkerStyle(1)
# gr2 = TGraph(len(LVtime),array('d',LVtime),array('d',LVtemp))
# gr2.SetMarkerColor(kRed)
# gr2.SetLineColor(kRed)
# gr2.SetMarkerStyle(1)
# gr3 = TGraph(len(STtime),array('d',STtime),array('d',STtemp))
# gr3.SetMarkerColor(kGreen)
# gr3.SetLineColor(kGreen)
# gr3.SetMarkerStyle(1)
# 
# mgn = TMultiGraph()
# mgn.SetTitle("Graph")
# mgn.Add(gr1,"p")
# mgn.Add(gr2,"p")
# mgn.Add(gr3,"p")
# 
# XaxisnameI = "Date"
# YaxisnameI = "Current (mA)"
# XaxisnameT = "Date"
# YaxisnameT = "Temperature (C)"
# 
# canv = TCanvas("Canvas","Canvas",800,400)
# gStyle.SetFillColor(kWhite)
# 
# canv.SetGrid()
# mgn.Draw("AP")
# mgn.GetXaxis().SetTimeDisplay(1)
# mgn.GetXaxis().SetNdivisions(-503)
# mgn.GetXaxis().SetTimeFormat("%Y-%m-%d")
# mgn.GetXaxis().SetTimeOffset(0,"gmt")
# mgn.GetXaxis().SetTitle(XaxisnameI)
# mgn.GetYaxis().SetTitle(YaxisnameI)
# mgn.GetXaxis().SetLimits(min(PLCtime[:]),max(PLCtime[:len(PLCtime)/2]))
# #mgn.GetXaxis().SetLimits(min(PLCtime[len(PLCtime)/2:]),max(PLCtime[len(PLCtime)/2:]))
# mgn.GetHistogram().SetMinimum(-50)
# mgn.GetHistogram().SetMaximum(30)
# mgn.GetYaxis().SetTitleOffset(1.5)
# x1=.7
# y1=.7
# x2=x1+.2
# y2=y1+.175
# leg = TLegend(x1,y1,x2,y2)
# leg.AddEntry(gr1,"data 1","pl")
# leg.AddEntry(gr2,"data 2","pl")
# leg.AddEntry(gr3,"data 3","pl")
# leg.SetTextFont(10)
# leg.Draw()
# 
# canv.SaveAs("TEC_minus_1.2.4.2.3_PLC_TSil.png")


print "GETTING TRACKER STATES"
for i in range((end-start)/86400+1): #(start,end,86400)
	timenow=start+i*86400
	timeyest=start+(i-1)*86400
	timenowTDatime=TDatime(timenow)
	timeyestTDatime=TDatime(timeyest)
	today=timenowTDatime.GetDate()
	yesterday=timeyestTDatime.GetDate()
	if len(states[today])==0:
		states[today].append(states[yesterday][-1])
		statetimes[today].append(timenow)

#prepare the simulation input files
totDays = 0
sdDays  = 0
print "WRITING INPUT FILE ..."
with open('LumiPerDay_'+partition+'.txt','w') as fout:
	for i in range((end-start)/86400+1): #(start,end,86400)
		timenow =start+i*86400
		nHours  =TDatime(timenow).GetTime()/10000
		timeyest=start+(i-1)*86400
		timetmr =start+(i+1)*86400
		if timetmr>end-86400: timetmr = timetmr-2*86400
		timenowTDatime=TDatime(timenow)
		timeyestTDatime=TDatime(timeyest)
		timetmrTDatime=TDatime(timetmr)
		today=timenowTDatime.GetDate()
		yesterday=timeyestTDatime.GetDate()
		tomorrow=timetmrTDatime.GetDate()
		strToWrite = str(today)+'\t'+str(timenow)+'\t'+str(lumi[today])
		totDays+=1
		
		if len(states[today])==0: 
			print "========>>>>>>>>>>THERE IS NO STATES FOR", today
			continue
		
		if states[yesterday][-1]=='ON': 
			ONdur[today]+=statetimes[today][0]-timenow+3600*nHours
		if states[yesterday][-1]=='OFF' or states[yesterday][-1]=='ERROR' or states[yesterday][-1]=='DEAD' or states[yesterday][-1]=='OFF-LOCKED': 
			OFFdur[today]+=statetimes[today][0]-timenow+3600*nHours
		if states[yesterday][-1]=='STANDBY': 
			STBdur[today]+=statetimes[today][0]-timenow+3600*nHours
		if states[yesterday][-1]=='HVMIXED' or states[yesterday][-1]=='LVMIXED': 
			ONdur[today]+=(statetimes[today][0]-timenow+3600*nHours)/2
			OFFdur[today]+=(statetimes[today][0]-timenow+3600*nHours)/2
		if states[yesterday][-1]=='ON_CTRL' or states[yesterday][-1]=='CTRLMIXED': 
			STBdur[today]+=(statetimes[today][0]-timenow+3600*nHours)/2
			OFFdur[today]+=(statetimes[today][0]-timenow+3600*nHours)/2
			
		for i in range(1,len(states[today])):
			if len(states[today])==1: continue
			if states[today][i-1]=='ON': 
				ONdur[today]+=statetimes[today][i]-statetimes[today][i-1]
			if states[today][i-1]=='OFF' or states[today][i-1]=='ERROR' or states[today][i-1]=='DEAD' or states[today][i-1]=='OFF-LOCKED': 
				OFFdur[today]+=statetimes[today][i]-statetimes[today][i-1]
			if states[today][i-1]=='STANDBY': 
				STBdur[today]+=statetimes[today][i]-statetimes[today][i-1]
			if states[today][i-1]=='HVMIXED' or states[today][i-1]=='LVMIXED': 
				ONdur[today]+=(statetimes[today][i]-statetimes[today][i-1])/2
				OFFdur[today]+=(statetimes[today][i]-statetimes[today][i-1])/2
			if states[today][i-1]=='ON_CTRL' or states[today][i-1]=='CTRLMIXED': 
				STBdur[today]+=(statetimes[today][i]-statetimes[today][i-1])/2
				OFFdur[today]+=(statetimes[today][i]-statetimes[today][i-1])/2
				
		if states[today][-1]=='ON': 
			ONdur[today]+=timenow+86400-3600*nHours-statetimes[today][-1]
		if states[today][-1]=='OFF' or states[today][-1]=='ERROR' or states[today][-1]=='DEAD' or states[today][-1]=='OFF-LOCKED': 
			OFFdur[today]+=timenow+86400-3600*nHours-statetimes[today][-1]
		if states[today][-1]=='STANDBY': 
			STBdur[today]+=timenow+86400-3600*nHours-statetimes[today][-1]
		if states[today][-1]=='HVMIXED' or states[today][-1]=='LVMIXED': 
			ONdur[today]+=(timenow+86400-3600*nHours-statetimes[today][-1])/2
			OFFdur[today]+=(timenow+86400-3600*nHours-statetimes[today][-1])/2
		if states[today][-1]=='ON_CTRL' or states[today][-1]=='CTRLMIXED': 
			STBdur[today]+=(timenow+86400-3600*nHours-statetimes[today][-1])/2
			OFFdur[today]+=(timenow+86400-3600*nHours-statetimes[today][-1])/2

		onpercent  = float(ONdur[today])/86400
		offpercent = float(OFFdur[today])/86400
		stbpercent = float(STBdur[today])/86400
		sdpercent  = float(SDdur[today])/86400
		if onpercent<0 or offpercent<0 or stbpercent<0 or sdpercent<0:
			print "==========>>>>>> NEGATIVE STATE DURATION <<<<<<<<==========="
			print "ON:",onpercent,"OFF:",offpercent,"S-B:",stbpercent,"S-D:",sdpercent
		if not isTrackerSD[today] and (isTrackerSD[tomorrow] and isTrackerSD[yesterday]): 
			print "        CHANGING TRACKER STATE TO S-D SINCE DAYS BEFORE AND AFTER ARE S-D"
			isTrackerSD[today]=1
			timesChangedToSD+=1
		if isTrackerSD[today]:
			sdDays+=1
			onpercent  = 0
			offpercent = 0
			stbpercent = 0
			sdpercent  = 1
			print "TRACKER WAS SHUT-DOWN ON",today,"WITH AVERAGE TEMP:",TrackerSDTempAvgTAir[today],TrackerSDTempAvgTSil[today]['average'],
			#for file in PLClines_TSil.keys(): print TrackerSDTempAvgTSil[today][file],
			print
			if TrackerSDTempAvgTSil[today]['average']<-100: # for debugging
				print PLCtempsTSil[today]['average']
				#print PLCtemptimesTSil[today]
		if offpercent>onpercent and offpercent>stbpercent and offpercent>sdpercent: # for debugging
			print "TRACKER WAS OFF ON",today,"WITH AVERAGE TEMP:",TrackerSDTempAvgTAir[today],TrackerSDTempAvgTSil[today]['average'],
			#for file in PLClines_TSil.keys(): print TrackerSDTempAvgTSil[today][file],
			print
		strToWrite += '\t'+str(onpercent)+'\t'+str(offpercent)+'\t'+str(stbpercent)+'\t'+str(sdpercent)+'\t'+str(TrackerSDTempAvgTSil[today]['average'])
		strToWrite += '\t'+str(onpercent+offpercent+stbpercent+sdpercent)+'\t'+str(1)+'\n'
		fout.write(strToWrite)
print "        ",sdDays,"days were shut-down out of",totDays,"days"
print "        ",timesChangedToSD,"times state changed to S-D"



