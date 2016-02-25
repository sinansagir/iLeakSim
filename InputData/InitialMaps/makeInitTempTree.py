#!/usr/bin/python

import os,sys
import ROOT as R
from array import array

R.gROOT.SetStyle("Plain")

# Create Output TREE
OutputTree="TempTree0_mixed.root"
outRfile = R.TFile(OutputTree, "RECREATE")
treeout  = R.TTree("treetemp","treetemp")

# Read tracker map
TFileMap = R.TFile('../TrackMap.root','READ')
TTreeMap = TFileMap.Get("treemap")
partition = {}
for module in TTreeMap:
	partition[module.DETID]=module.Partition # in integers (1-8  -> TIB, TOB, TID, TEC min plu)
TFileMap.Close()
   
detid_t = array('i', [0])
temp_t  = array('f', [0])
treeout.Branch('DETID',detid_t,'DETID/I')
treeout.Branch('Temp',temp_t,'Temp/F')

infile2 = open('TempTree0_250411.txt', 'r')
lines2 = infile2.readlines()
infile2.close()
temp2 = {}
for line in lines2:
	data = line.strip().split()
	try: 
		temp2[int(data[0])] = float(data[1])
	except: print "Warning! => Unknown data format: ",data

# Read Input Temperature Data
infile = open('TempTree0_190311.txt', 'r')
lines = infile.readlines()
infile.close()
temp = {}
for line in lines:
	data = line.strip().split()
	try: 
		if 'TID' in partition[int(data[0])]:
			detid_t[0] = int(data[0])
			temp_t[0]  = temp2[int(data[0])]
			treeout.Fill()
		else:
			detid_t[0] = int(data[0])
			temp_t[0]  = float(data[1])
			treeout.Fill()
		temp[int(data[0])] = float(data[1])
	except: print "Warning! => Unknown data format: ",data

outRfile.cd()
treeout.Write()
outRfile.Close()

 
