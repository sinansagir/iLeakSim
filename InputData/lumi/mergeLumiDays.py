#!/usr/bin/python

import os,sys,fnmatch
from ROOT import *

lumiDir = 'lumi/'
whichLumi = 'Delivered' # "Delivered" or "Recorded"
startYear,startMonth,startDay = 2010,3,30
endYear,endMonth,endDay = 2015,12,14

startTDatime=TDatime(startYear,startMonth,startDay,1,0,0)
start=TDatime(startYear,startMonth,startDay,1,0,0).Convert()
endTDatime=TDatime(endYear,endMonth,endDay,1,0,0)
end=TDatime(endYear,endMonth,endDay,1,0,0).Convert()

with open('Lumi.txt','w') as fout:
	for i in range((end-start)/86400+1):
		timeglob=start+i*86400
		timeglobTDatime=TDatime(timeglob)
		date=str(timeglobTDatime.GetDate())
		time=str(timeglobTDatime.GetTime())
		year=date[:4]
		month=date[4:6]
		day=date[6:8]
		lumiFile=lumiDir+year+'-'+month+'-'+day+'_lumi.txt'
		f = open(lumiFile, 'rU')
		lines = f.readlines()
		f.close()
		lumiFileType1=[(whichLumi in line) for line in lines]
		lumiFileType2=[('tot'+whichLumi.lower() in line) for line in lines]
		if any(lumiFileType1): lumiStr=whichLumi+'(/'
		elif any(lumiFileType2): lumiStr='tot'+whichLumi.lower()+'(/'
		else: lumiStr='zero'
		if lumiStr=='zero': lumiOfDay=0.
		else:
			lumiLineInd = lines.index([line for line in lines if lumiStr in line][0])
			lumiColInd = lines[lumiLineInd].split('|').index([col for col in lines[lumiLineInd].split('|') if lumiStr in col][0])
			lumiCoeff = 1.
			if 'mb' in lines[lumiLineInd].split('|')[lumiColInd]: lumiCoeff = 1./1.e6 # conversion coefficient from /mb to /nb
			if 'ub' in lines[lumiLineInd].split('|')[lumiColInd]: lumiCoeff = 1./1.e3
			if 'nb' in lines[lumiLineInd].split('|')[lumiColInd]: lumiCoeff = 1.
			if 'pb' in lines[lumiLineInd].split('|')[lumiColInd]: lumiCoeff = 1.e3
			if 'fb' in lines[lumiLineInd].split('|')[lumiColInd]: lumiCoeff = 1.e6
			lumiOfDay = float(lines[lumiLineInd+2].split('|')[lumiColInd])*lumiCoeff # in /nb
		strToWrite = day+'/'+month+'/'+year+'\t'+str(timeglob)+'\t'+str(lumiOfDay)+'\n'
		fout.write(strToWrite)

lumiInFile = "Lumi.txt"
infileLumi = open(lumiInFile, 'r')
linesLumi = infileLumi.readlines()
infileLumi.close()
IntLum=0.
IntLumR1=0.
for i in range(len(linesLumi)):
	data = linesLumi[i].strip().split()
	IntLum+=float(data[2])/1.e6
	if data[0]=='03/06/2015':IntLumR1=IntLum
print "Total Integrated Lumi:",IntLum
print "Total Integrated Lumi Run1:",IntLumR1
print "Total Integrated Lumi Run2:",IntLum-IntLumR1

