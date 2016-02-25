#!/usr/bin/python

import os,sys
import ROOT as R
from array import array
from leakCalcV1 import *

R.gROOT.SetStyle("Plain")

if len(sys.argv)>1: iteration=int(sys.argv[1])
else: iteration=0
if len(sys.argv)>2: Nmodules=int(sys.argv[2])
else: Nmodules=1
if len(sys.argv)>3: OutputTree=sys.argv[3]
else: OutputTree="treeout"+str(iteration)+".root"

inputDir = "" # placeholder if absolute path is needed!
Flumatch  = inputDir+"FluenceMatching.root"
TempinTOB = inputDir+"LumiPerDay_TOB.txt"
TempinTIB = inputDir+"LumiPerDay_TIB.txt"
TempinTECm= inputDir+"LumiPerDay_TECn.txt"
TempinTECp= inputDir+"LumiPerDay_TECp.txt"
InitTemp  = inputDir+"TempTree0.root"
TempChange= inputDir+"dPdT.root"
InitLeak  = inputDir+"IleakTree0.root"

#/////////////////////////////////////////////////////////////////////////////////////////
#*************************** Read in Data from Input Files *******************************
#/////////////////////////////////////////////////////////////////////////////////////////

# Read Fluencies
TFileFluence = R.TFile(Flumatch,'READ')
TTreeFluence = TFileFluence.Get("SimTree_old")
fluencedetid    = []
fluenceNew      = []
fluenceOld      = []
fluenceVolume   = []
fluencePartition= []
for module in TTreeFluence:
	fluencedetid.append(module.DETID_T)
	fluenceNew.append(module.FINFLU_T) # new algo
	fluenceOld.append(module.FINALFLUENCE_T) # old algo
	fluenceVolume.append(module.VOLUME_T) # in meters
	fluencePartition.append(module.PARTITON_T) # in integers (1-8  -> TIB, TOB, TID, TEC min plu)
fluentries = TTreeFluence.GetEntries()
TFileFluence.Close()

# Read Initial Temperature Snapshot
TFileIniTemp = R.TFile(InitTemp,'READ')
TTreeIniTemp = TFileIniTemp.Get("treetemp")
iniTempdetid = []
iniTemp      = []
for module in TTreeIniTemp:
	iniTempdetid.append(module.DETID)
	iniTemp.append(module.Temp)
tempentries = TTreeIniTemp.GetEntries()
TFileIniTemp.Close()

# Read Tree for Change of Temp with applied power
TFiledpdt = R.TFile(TempChange,'READ')
TTreedpdt = TFiledpdt.Get("tree")
dpdtdetid = []
dtdp      = []
for module in TTreedpdt:
	dpdtdetid.append(module.DETID)
	dtdp.append(module.DTDP)
dpdtentries = TTreedpdt.GetEntries()
TFiledpdt.Close()

# Read Initial Dark Current Snapshot
TFileInitLeak = R.TFile(InitLeak,'READ')
TTreeInitLeak = TFileInitLeak.Get("treeileak")
iniLeakdetid= []
iniLeak     = []
for module in TTreeInitLeak:
	iniLeakdetid.append(module.DETID)
	iniLeak.append(module.IniIleak)
ileakentries = TTreeInitLeak.GetEntries()
TFileInitLeak.Close()

# Read Input Data for Lumi and Trackerstates of TOB
infileTOB = open(TempinTOB, 'r')
print "Reading TOB Lumi File"
linesTOB = infileTOB.readlines()
infileTOB.close()
tdtime =[]
Tstate =[]
TallTOB=[]
lumiAll=[]
Tsd    =[] # Tracker shut-down temperatures
IntLum=0.
ra=0
for line in linesTOB:
	data = line.strip().split()
	try: 
		tdtime.append(int(data[1]))
		tonTOB =float(data[3])
		toffTOB=float(data[4])
		tstbTOB=float(data[5])
		tsdTOB =float(data[6])
		if tonTOB >toffTOB and tonTOB >tstbTOB and tonTOB >tsdTOB: Tstate.append(1)
		if toffTOB>tonTOB  and toffTOB>tstbTOB and toffTOB>tsdTOB: Tstate.append(2)
		if tstbTOB>toffTOB and tstbTOB>tonTOB  and tstbTOB>tsdTOB: Tstate.append(3)
		if tsdTOB >tonTOB  and tsdTOB >tstbTOB and tsdTOB >toffTOB:Tstate.append(4)
		Tsd.append(float(data[7])+273.16) # Tracker shut-down temperatures in K
		TallTOB.append(tonTOB)
		TallTOB.append(toffTOB)
		TallTOB.append(tstbTOB)
		TallTOB.append(tsdTOB)
		isLumiFilled=False # Fill the fluence only for one state of the day
		if tonTOB>0 and not isLumiFilled: 
			lumiAll.append(float(data[2]))
			isLumiFilled=True
		else: lumiAll.append(0.)
		if toffTOB>0 and not isLumiFilled: 
			lumiAll.append(float(data[2]))
			isLumiFilled=True
		else: lumiAll.append(0.)
		if tstbTOB>0 and not isLumiFilled: 
			lumiAll.append(float(data[2]))
			isLumiFilled=True
		else: lumiAll.append(0.)
		if tsdTOB>0 and not isLumiFilled: 
			lumiAll.append(float(data[2]))
			isLumiFilled=True
		else: lumiAll.append(0.)
		if lumiAll[-1]+lumiAll[-2]+lumiAll[-3]+lumiAll[-4]!=float(data[2]):
			print "Lumi for",data[1],"is",float(data[2]),", but lumi for simulation is",lumiAll[-1]+lumiAll[-2]+lumiAll[-3]+lumiAll[-4]
		IntLum+=float(data[2])
		ra=0
	except: print "Warning! => Unknown data format: ",data,"in",TempinTOB

# Read Input Data for Trackerstates of TIB
infileTIB = open(TempinTIB, 'r')
print "Reading TIB Lumi File"
linesTIB = infileTIB.readlines()
infileTIB.close()
TallTIB=[]
for line in linesTIB:
	data = line.strip().split()
	try: 
		TallTIB.append(float(data[3]))
		TallTIB.append(float(data[4]))
		TallTIB.append(float(data[5]))
		TallTIB.append(float(data[6]))
	except: print "Warning! => Unknown data format: ",data,"in",TempinTIB

# Read Input Data for Trackerstates of TECm
infileTECm = open(TempinTECm, 'r')
print "Reading TECm Lumi File"
linesTECm = infileTECm.readlines()
infileTECm.close()
TallTECm=[]
for line in linesTECm:
	data = line.strip().split()
	try: 
		TallTECm.append(float(data[3]))
		TallTECm.append(float(data[4]))
		TallTECm.append(float(data[5]))
		TallTECm.append(float(data[6]))
	except: print "Warning! => Unknown data format: ",data,"in",TempinTECm

# Read Input Data for Trackerstates of TECp
infileTECp = open(TempinTECp, 'r')
print "Reading TECp Lumi File"
linesTECp = infileTECp.readlines()
infileTECp.close()
TallTECp=[]
for line in linesTECp:
	data = line.strip().split()
	try: 
		TallTECp.append(float(data[3]))
		TallTECp.append(float(data[4]))
		TallTECp.append(float(data[5]))
		TallTECp.append(float(data[6]))
	except: print "Warning! => Unknown data format: ",data,"in",TempinTECp
	
periodesAll=min(len(TallTIB),len(TallTOB),len(TallTECm),len(TallTECp))
periodes=periodesAll/4
print "# of days to simulate:",periodes
print "Integrated Lumi:",round(IntLum*1e-6,2),"fb^-1"

# Create Output TREE
outRfile = R.TFile(OutputTree, "RECREATE")
treeout  = R.TTree("tree","SimTree")
   
detid_t     = array('i', [0])
partition_t = array('i', [0])
ileaki_t    = array('f', [0])
tempi_t     = array('f', [0])
volume_t    = array('f', [0])
ileakc_t_on = array('f', periodes*[0])
ileakc_t_of = array('f', periodes*[0])
ileakc_t_sb = array('f', periodes*[0])
ileakc_t_sd = array('f', periodes*[0])
temp_t_on   = array('f', periodes*[0])
temp_t_of   = array('f', periodes*[0])
temp_t_sb   = array('f', periodes*[0])
temp_t_sd   = array('f', periodes*[0])
fluence_t   = array('f', periodes*[0])
dtimes_t    = array('f', periodes*[0])

treeout.Branch('DETID_T',detid_t,'DETID_T/I')
treeout.Branch('PARTITION_T',partition_t,'PARTITION_T/I')
treeout.Branch('ILEAKI_T',ileaki_t,'ILEAKI_T/F')
treeout.Branch('TEMPI_T',tempi_t,'TEMPI_T/F')
treeout.Branch('VOLUME_T',volume_t,'VOLUME_T/F')
treeout.Branch('ileakc_t_on',ileakc_t_on,'ileakc_t_on['+str(periodes)+']/F')
treeout.Branch('ileakc_t_of',ileakc_t_of,'ileakc_t_of['+str(periodes)+']/F')
treeout.Branch('ileakc_t_sb',ileakc_t_sb,'ileakc_t_sb['+str(periodes)+']/F')
treeout.Branch('ileakc_t_sd',ileakc_t_sd,'ileakc_t_sd['+str(periodes)+']/F')
treeout.Branch('temp_t_on',temp_t_on,'temp_t_on['+str(periodes)+']/F')
treeout.Branch('temp_t_of',temp_t_of,'temp_t_of['+str(periodes)+']/F')
treeout.Branch('temp_t_sb',temp_t_sb,'temp_t_sb['+str(periodes)+']/F')
treeout.Branch('temp_t_sd',temp_t_sd,'temp_t_sd['+str(periodes)+']/F')
treeout.Branch('fluence_t',fluence_t,'fluence_t['+str(periodes)+']/F')
treeout.Branch('dtime_t',dtimes_t,'dtime_t['+str(periodes)+']/F')

#***********************************************************************************************************
#**************************************Start of Loops*******************************************************
#***********************************************************************************************************

for it in range(iteration*Nmodules,(iteration+1)*Nmodules): #This for loop runs for each module!  
	if it>=dpdtentries: 
		print "Index out of dpdtentries range! Exiting loop ..."
		break
	#if dpdtdetid!=470426026: continue
	print "Entry  Number :",it
	print "Module Number :",dpdtdetid[it]
	
	#Make sure that the module exists in all the input files
	modInFlutree = False
	modInTemptree = False
	modInIleaktree = False
	for ind1 in range(fluentries): #Check if module exists in fluence tree!
		Tall=[]
		if fluencedetid[ind1]==dpdtdetid[it]:
			if fluencePartition[ind1]==1 or fluencePartition[ind1]==2 or fluencePartition[ind1]==5 or fluencePartition[ind1]==6:
				for i4 in range(periodesAll): Tall.append(TallTIB[i4])
			if fluencePartition[ind1]==3 or fluencePartition[ind1]==4:
				for i4 in range(periodesAll): Tall.append(TallTOB[i4])
			if fluencePartition[ind1]==7:
				for i4 in range(periodesAll): Tall.append(TallTECm[i4])
			if fluencePartition[ind1]==8:
				for i4 in range(periodesAll): Tall.append(TallTECp[i4]) 
			modInFlutree = True
			flutreeind = ind1
			break
	if not modInFlutree:
		print "Module",dpdtdetid[it],"does not exist in fluence tree! Continuing to next module ..."
		continue
		
	for ind2 in range(tempentries): #Check if module exists in initial temperature snapshot tree!
		if iniTempdetid[ind2]==dpdtdetid[it]: 
			modInTemptree = True
			temptreeind = ind2
			break
	if not modInTemptree:
		print "Module",dpdtdetid[it],"does not exist in initial temperature snapshot tree! Continuing to next module ..."
		continue
	if iniTemp[temptreeind]>50. or iniTemp[temptreeind]<-20.:
		print "Module",dpdtdetid[it],"initial temperature reading is corrupted! No point at simulating. Continuing to next module ..."
		continue
		
	for ind3 in range(ileakentries): #Check if module exists in initial leakage current snapshot tree!
		if iniLeakdetid[ind3]==dpdtdetid[it]:
			if dtdp[it]>0 and dtdp[it]<30: #control if same detid in leak tree and dpdt tree
				modInIleaktree = True
				ileaktreeind = ind3
				break
			else: break
	if not modInIleaktree:
		print "Module",dpdtdetid[it],"does not exist in initial leakage current snapshot tree! Continuing to next module ..."
		continue
		
	Temp = [-9999.,-9999.,-9999.,-9999.]
	Temp[0],Temp[1],Temp[2],Temp[3]=iniTemp[temptreeind]+273.16,5.5+273.16,iniTemp[temptreeind]-3.+273.16,13.+273.16 #definition of Temperatures in K: on->[0], off->[1],on-stb->[2],sd->[3]
	modIniIleak =iniLeak[ileaktreeind]/1000*LeakCorrection(293.16,Temp[0]) # scale initial leak to 20C, and convert from mA to A

	xsec_7tev  = 7.35e7 #nb
	xsec_13tev = 7.91e7 #nb
	xsec_14tev = 7.99e7 #nb
	FeqOld = []
	FeqNew = []
	for i in range(periodesAll):
		if i/4>=1391: xsec=xsec_13tev # Tracker started to be cooled down to -15C (from 4C in Run 1) on 08/01/15 (?) according to Sasha tools. Number of days from the simulation start date -> 08/01/15-19/03/11=1391 days. Taking this as the starting date of the 13 TeV Run 2!!!!!
		else: xsec=xsec_7tev
		FeqOld.append(lumiAll[i]*fluenceOld[flutreeind]*xsec)
		FeqNew.append(lumiAll[i]*fluenceNew[flutreeind]*xsec) # two different fluence matchings to calculate 1MeV equivalent fluence per day with Luminosity
		
	#******************************Using data for filling of histogramms*******************************
	param,error=[0,0,0,0,0,0],[0,0,0,0,0,0] # Moll Parameters (minimum) and expected Error
	modVolume=fluenceVolume[flutreeind]*100
	#0->k0I; 1->EI; 2->alph01; 3->alph02; 4->beta; 5->alph1
	param[0],param[1],param[2],param[3],param[4],param[5]=0,0,0,0,0,0 #initialize Parameters (min Value) -- enter 0 to use the default values in "leakCalcV1.py"
	moddtdp = dtdp[it]
	DarkCurrent=LeakCalculation(periodes,Tall,Temp,Tsd,FeqNew,modIniIleak,modVolume,moddtdp,param)
	for day in range(periodes):
		ileakc_t_on[day]= DarkCurrent['iLeakON'][day]
		ileakc_t_of[day]= DarkCurrent['iLeakOF'][day]
		ileakc_t_sb[day]= DarkCurrent['iLeakSB'][day]
		ileakc_t_sd[day]= DarkCurrent['iLeakSD'][day]
		temp_t_on[day]  = DarkCurrent['tempON'][day]
		temp_t_of[day]  = DarkCurrent['tempOF'][day]
		temp_t_sb[day]  = DarkCurrent['tempSB'][day]
		temp_t_sd[day]  = DarkCurrent['tempSD'][day]
		fluence_t[day]  = DarkCurrent['fluence'][day]
		dtimes_t[day]   = tdtime[day]
	detid_t[0]    = dpdtdetid[it]
	ileaki_t[0]   = iniLeak[ileaktreeind]
	tempi_t[0]    = iniTemp[temptreeind]
	volume_t[0]   = fluenceVolume[flutreeind]
	partition_t[0]= fluencePartition[flutreeind]
	treeout.Fill()
	print "Finished simulating module:",dpdtdetid[it]

treeout.Print()
outRfile.cd()
treeout.Write()
outRfile.Close()
