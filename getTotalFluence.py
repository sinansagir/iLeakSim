#!/usr/bin/python

import os,sys,fnmatch,math,pickle
from bisect import bisect_left
import numpy as np
from ROOT import *
gROOT.SetBatch(1)

#******************************Input to edit******************************************************
simDate = "2023_9_4"

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
print "************************* READING TREE **************************"
dtime_t     = []
fluence_t = {}
nMod=0
for event in simTree:
	if event.DETID_T != 436262468 and event.DETID_T != 369120486: continue
	fluence_t[event.DETID_T] = []
	if len(dtime_t)==0: fillTime=True
	else: fillTime=False
	for i in range(len(event.dtime_t)):
		if fillTime: dtime_t.append(int(event.dtime_t[i]))
		fluence_t[event.DETID_T].append(event.fluence_t[i])
	print event.DETID_T,sum(fluence_t[event.DETID_T])
	nMod+=1
	if nMod%1000==0: print "Finished reading ", nMod, "/", simTree.GetEntries(), " modules!"
print "********************* FINISHED READING TREE *********************"

simFile.Close()
	
print "***************************** DONE *********************************"
  
