#!/usr/bin/python

import os,sys
import ROOT as R
from array import array
from leakCalcV1 import *

R.gROOT.SetBatch(1)
R.gROOT.SetStyle("Plain")

if len(sys.argv)>1: iteration=int(sys.argv[1])
else: iteration=0
if len(sys.argv)>2: Nmodules=int(sys.argv[2])
else: Nmodules=1
if len(sys.argv)>3: OutputTree=sys.argv[3]
else: OutputTree="treeout"+str(iteration)+".root"

inputDir = "" # placeholder if absolute path is needed!
Flumatch7  = inputDir+"InputDataLocal/FluenceMatching7TeVcom.root"
Flumatch14 = inputDir+"InputDataLocal/FluenceMatching14TeVcom.root"
TempinTOB  = inputDir+"InputDataLocal/LumiPerDay_TOB.txt"
TempinTIB  = inputDir+"InputDataLocal/LumiPerDay_TIB.txt"
TempinTECm = inputDir+"InputDataLocal/LumiPerDay_TECn.txt"
TempinTECp = inputDir+"InputDataLocal/LumiPerDay_TECp.txt"
InitTemp   = inputDir+"InputDataLocal/TempTree0.root"
TempChange = inputDir+"InputDataLocal/dPdT.root"
InitLeak   = inputDir+"InputDataLocal/IleakTree0.root"

#/////////////////////////////////////////////////////////////////////////////////////////
#*************************** Read in Data from Input Files *******************************
#/////////////////////////////////////////////////////////////////////////////////////////

# Read Fluencies
## E_com = 7TeV -- used for 7 and 8 TeV runs
TFileFluence7 = R.TFile(Flumatch7,'READ')
TTreeFluence7 = TFileFluence7.Get("SimTree_old")
fluence7detid    = []
fluence7New      = []
fluence7Old      = []
fluence7Volume   = []
fluence7Partition= []
for module in TTreeFluence7:
	fluence7detid.append(module.DETID_T)
	fluence7New.append(module.FINFLU_T) # new algo
	fluence7Old.append(module.FINALFLUENCE_T) # old algo
	fluence7Volume.append(module.VOLUME_T) # in meters
	fluence7Partition.append(module.PARTITON_T) # in integers (1-8  -> TIB, TOB, TID, TEC min plu)
fluentries7 = TTreeFluence7.GetEntries()
TFileFluence7.Close()

## E_com = 14TeV -- used for 13TeV run
TFileFluence14 = R.TFile(Flumatch14,'READ')
TTreeFluence14 = TFileFluence14.Get("SimTree_old")
fluence14detid = []
fluence14New   = []
fluence14Old   = []
for module in TTreeFluence14:
	fluence14detid.append(module.DETID_T)
	fluence14New.append(module.FINFLU_T) # new algo
	fluence14Old.append(module.FINALFLUENCE_T) # old algo
fluentries14 = TTreeFluence14.GetEntries()
TFileFluence14.Close()

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
		isLumiFilled=False # Fill the lumi only for one state of the day
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

# Read Input Data for Trackerstates of TIB (also includes TID)
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

for imod in range(iteration*Nmodules,(iteration+1)*Nmodules): #This for loop runs for each module!  
	if imod>=dpdtentries: 
		print "Index out of dpdtentries range! Exiting loop ..."
		break
	#if dpdtdetid!=470426026: continue
	print "Entry  Number :",imod
	print "Module Number :",dpdtdetid[imod]
	
	#Make sure that the module exists in all the input files, else simulation cannot be performed!
	modInFlutree = False
	modInTemptree = False
	modInIleaktree = False
	for ind in range(fluentries7): #Check if module exists in 7TeV fluence tree!
		if fluence7detid[ind]==dpdtdetid[imod]: 
			flutreeind7 = ind
			modInFlutree = True
			break
	if not modInFlutree:
		print "Module",dpdtdetid[imod],"does not exist in 7TeV fluence tree! Continuing to next module ..."
		continue
	modInFlutree = False
	for ind in range(fluentries14): #Check if module exists in 14TeV fluence tree!
		if fluence14detid[ind]==dpdtdetid[imod]: 
			flutreeind14 = ind
			modInFlutree = True
			break
	if not modInFlutree:
		print "Module",dpdtdetid[imod],"does not exist in 14TeV fluence tree! Continuing to next module ..."
		continue
		
	for ind in range(tempentries): #Check if module exists in initial temperature snapshot tree!
		if iniTempdetid[ind]==dpdtdetid[imod]: 
			modInTemptree = True
			temptreeind = ind
			break
	if not modInTemptree:
		print "Module",dpdtdetid[imod],"does not exist in initial temperature snapshot tree! Continuing to next module ..."
		continue
	if iniTemp[temptreeind]>50. or iniTemp[temptreeind]<-20.: #skip outliers
		print "Module",dpdtdetid[imod],"initial temperature reading is corrupted! No point at simulating. Continuing to next module ..."
		continue
		
	for ind in range(ileakentries): #Check if module exists in initial leakage current snapshot tree!
		if iniLeakdetid[ind]==dpdtdetid[imod]:
			if dtdp[imod]>0 and dtdp[imod]<30: #module shouldn't be an outlier in dpdt tree
				modInIleaktree = True
				ileaktreeind = ind
				break
			else: break
	if not modInIleaktree:
		print "Module",dpdtdetid[imod],"does not exist in initial leakage current snapshot tree! Continuing to next module ..."
		continue

	#Get the lumi history of module using its partition info:
	if fluence7Partition[flutreeind7]==1 or fluence7Partition[flutreeind7]==2 or fluence7Partition[flutreeind7]==5 or fluence7Partition[flutreeind7]==6: Tall = TallTIB[:]
	elif fluence7Partition[flutreeind7]==3 or fluence7Partition[flutreeind7]==4: Tall = TallTOB[:]
	elif fluence7Partition[flutreeind7]==7: Tall = TallTECm[:]
	elif fluence7Partition[flutreeind7]==8: Tall = TallTECp[:]
	else:
		print "Module",dpdtdetid[imod],"does not have a known partition number! Continuing to next module ..."
		continue
		
	Ton=iniTemp[temptreeind]+273.16 #module temperature in K when tracker is ON
	Tst=Ton-3. #module temperature in K when tracker is STAND-BY
	modIniIleak =iniLeak[ileaktreeind]/1000*LeakCorrection(293.16,Ton) # scale initial leak to 20C, and convert from mA to A

	xsec_7tev  = 7.35e7 #nb
	xsec_8tev  = 7.47e7 #nb
	xsec_13tev = 7.91e7 #nb
	xsec_14tev = 7.99e7 #nb
	FeqOld = [] #fluencies from old algo
	FeqNew = [] #fluencies from new algo
	modThist = [] #module temperature history
	for i in range(periodesAll):
		if i/4<382: #8TeV runs start on 04/04/12. Number of days from the simulation start date -> 04/04/12-19/03/11=382 days
			xsec=xsec_7tev
			fluenceOld = fluence7Old[flutreeind7]
			fluenceNew = fluence7New[flutreeind7]
		elif i/4<1391: # Transition from Run1 to Run2 on 08/01/15 (?) according to Sasha tools (approximate date). Number of days from the simulation start date -> 08/01/15-19/03/11=1391 days. Taking this as the starting date of the 13 TeV Run 2!!!!!
			xsec=xsec_8tev
			fluenceOld = fluence7Old[flutreeind7]
			fluenceNew = fluence7New[flutreeind7]
		else: #Run2 at 13TeV
			xsec=xsec_13tev
			fluenceOld = fluence14Old[flutreeind14] #Using the closest existing FLUKA fluence!
			fluenceNew = fluence14New[flutreeind14]
		FeqOld.append(lumiAll[i]*fluenceOld*xsec)
		FeqNew.append(lumiAll[i]*fluenceNew*xsec) # two different fluence matchings to calculate 1MeV equivalent fluence per day with Luminosity
		if i%4==0:
			if i/4>=1391: T=Ton-19. # Tracker started to be cooled down to -15C (from 4C in Run 1) on 08/01/15 (?) according to Sasha tools. Number of days from the simulation start date -> 08/01/15-19/03/11=1391 days
			else: T=Ton
		if i%4==1: T=Tsd[(i-1)/4]#T=Toff
		if i%4==2:
			if i/4>=1391: T=Tst-19. # Tracker started to be cooled down to -15C (from 4C in Run 1) on 08/01/15 (?) according to Sasha tools. Number of days from the simulation start date -> 08/01/15-19/03/11=1391 days
			else: T=Tst
		if i%4==3: T=Tsd[(i-3)/4]
		modThist.append(T)
		
	param=[0,0,0,0,0,0] # Moll Parameters (minimum) (0 == use default values in leakCalc.py)
	modVolume=fluence7Volume[flutreeind7]*100
	#0->k0I; 1->EI; 2->alph01; 3->alph02; 4->beta; 5->alph1
	param[0],param[1],param[2],param[3],param[4],param[5]=0,0,0,0,0,0 #initialize Parameters (min Value) -- enter 0 to use the default values in "leakCalcV1.py"
	moddtdp = dtdp[imod]
	DarkCurrent=LeakCalculation(periodes,Tall,modThist,FeqNew,modIniIleak,modVolume,moddtdp,param)
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
	detid_t[0]    = dpdtdetid[imod]
	ileaki_t[0]   = iniLeak[ileaktreeind]
	tempi_t[0]    = iniTemp[temptreeind]
	volume_t[0]   = fluence7Volume[flutreeind7]
	partition_t[0]= fluence7Partition[flutreeind7]
	treeout.Fill()
	print "Finished simulating module:",dpdtdetid[imod]

treeout.Print()
outRfile.cd()
treeout.Write()
outRfile.Close()
