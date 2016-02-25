#!/usr/bin/python

import os,sys
import numpy as np
from ROOT import *
from pylab import *
import matplotlib.pyplot as plt

partition = 'TECp'
inFile1=partition+'_all2011-2014.txt'
inFile2=partition+'_all2014-2015.txt'
inFile3=partition+'_all2014-2015_part2.txt'
outFile=partition+'_all2011-2015.txt'

data1 = open(inFile1, 'r')
lines1 = data1.readlines()
data1.close()

data2 = open(inFile2, 'r')
lines2 = data2.readlines()
data2.close()

data3 = open(inFile3, 'r')
lines3 = data3.readlines()
data3.close()

with open(outFile,'w') as fout:
	for line in lines1:
		if line.startswith('************'): continue
		n=int(line.strip().split()[1])
		fout.write(line)
	fout.write('\n')
	print n
	for line in lines2:
		if line.startswith('************'): continue
		if line.startswith('*    Row   *'): continue
		if len(line.strip().split()[3])>10: print line
		lineList=line.strip().split()
		lineList[1]=str(n+1)
		for item in lineList:
			fout.write(item+'\t')
		fout.write('\n')
		n+=1	
	fout.write('\n')
	print n
	for line in lines3:
		if line.startswith('************'): continue
		if line.startswith('*    Row   *'): continue
		if len(line.strip().split()[3])>10: print line
		lineList=line.strip().split()
		lineList[1]=str(n+1)
		for item in lineList:
			fout.write(item+'\t')
		fout.write('\n')
		n+=1