#!/usr/bin/python

import os,sys,fnmatch,math,pickle
from bisect import bisect_left
import numpy as np
from ROOT import *
import CMS_lumi, tdrstyle
gROOT.SetBatch(1)

#set the tdr style
tdrstyle.setTDRStyle()

datesToPlot = ['2012_8_30','2016_10_11','2018_10_18']
datesToPlot+= ['2022_10_20','2023_4_25','2023_5_12','2023_6_6','2023_7_16','2023_9_1']

#change the CMS_lumi variables (see CMS_lumi.py)
CMS_lumi.lumi_7TeV = "6.1 fb^{-1}"
CMS_lumi.lumi_8TeV = "13.4 fb^{-1}"
CMS_lumi.lumi_13TeV= "2.3 fb^{-1}"
CMS_lumi.writeExtraText = 1
CMS_lumi.extraText = "Preliminary"
CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)

CMS_lumi.lumiTextSize     = 0.3
CMS_lumi.lumiTextOffset   = 0.1
CMS_lumi.cmsTextSize      = 0.55
CMS_lumi.cmsTextOffset    = 0.1

iPos = 10
if( iPos==0 ): CMS_lumi.relPosX = 0.12

H_ref = 600; 
W_ref = 800; 
W = W_ref
H  = H_ref

iPeriod = 3

# references for T, B, L, R
T = 0.12*H_ref
B = 0.12*H_ref
L = 0.14*W_ref
R = 0.05*W_ref

#******************************Input to edit******************************************************
simDate = "2023_9_4"
plotPath = "DarkSimAllModules_"+simDate+"/allModules_data_DCU_raw"
runDir=os.getcwd()

hi = {'TIB':{},'TID':{},'TOB':{},'TEC':{}}
ht = {'TIB':{},'TID':{},'TOB':{},'TEC':{}}
colors = {'TIB':kOrange,'TID':kGreen+1,'TOB':kBlue,'TEC':kBlack}
XaxisnameI = "Simulated Current (#muA)"
YaxisnameI = "Measured Current (#muA)"
XaxisnameT = "Simulated Temperature (#circC)"
YaxisnameT = "Measured Temperature (#circC)"
x1=.7 #for legs
y1=0.2
x2=x1+.15
y2=y1+.3

# Read Input Data for Lumi
lumiFile = "InputDataLocal/lumi/Lumi.txt"
infileLumi = open(lumiFile, 'r')
print "Reading Lumi File"
linesLumi = infileLumi.readlines()
infileLumi.close()
IntLum=0.
intLumis = {}
for i in range(len(linesLumi)):
	data = linesLumi[i].strip().split()
	try: 
		IntLum+=float(data[2])/1e6 # in INVFB
		for date in datesToPlot:
			year_=date.split('_')[0]
			month_=date.split('_')[1] if len(date.split('_')[1])==2 else '0'+date.split('_')[1]
			day_=date.split('_')[2] if len(date.split('_')[2])==2 else '0'+date.split('_')[2]
			if data[0]==day_+'/'+month_+'/'+year_: intLumis[date]=IntLum
	except: print "Warning! => Unknown data format: ",data,"in",lumiFile
print "Total Integrated Lumi:",IntLum
for date in datesToPlot:
	print "Total Integrated Lumi "+date+":",intLumis[date]

RFile = TFile(runDir+'/'+plotPath+'/outRfileAllModules.root')
if not os.path.exists(runDir+'/'+plotPath+'_esthetic'): os.system('mkdir '+runDir+'/'+plotPath+'_esthetic')

parts = ['TEC','TOB','TIB','TID']
hi,ht,gri,grt = {},{},{},{}
ileakMins = {'2012_8_30':0,   '2016_10_11':0,  '2018_10_18':0,  '2022_10_20':0,   '2023_4_25':0,   '2023_5_12':0,   '2023_6_6':0,   '2023_7_16':0,   '2023_9_1':0}
ileakMaxs = {'2012_8_30':1000,'2016_10_11':900,'2018_10_18':900,'2022_10_20':2500,'2023_4_25':2500,'2023_5_12':2500,'2023_6_6':2500,'2023_7_16':2500,'2023_9_1':2500}
tsilMins  = {'2012_8_30':0,   '2016_10_11':-25,'2018_10_18':-25,'2022_10_20':-25, '2023_4_25':-25, '2023_5_12':-25, '2023_6_6':-25, '2023_7_16':-25, '2023_9_1':-25}
tsilMaxs  = {'2012_8_30':50,  '2016_10_11':50, '2018_10_18':50, '2022_10_20':25,  '2023_4_25':25,  '2023_5_12':25,  '2023_6_6':25,  '2023_7_16':25,  '2023_9_1':25}

for par in parts:
	for date in datesToPlot:
		gri['gri_'+par+'_'+date] = RFile.Get('gri_'+par+'_'+date).Clone()
		grt['grt_'+par+'_'+date] = RFile.Get('grt_'+par+'_'+date).Clone()
		hi['hi_'+par+'_'+date]   = RFile.Get('hi_'+par+'_'+date).Clone()
		ht['ht_'+par+'_'+date]   = RFile.Get('ht_'+par+'_'+date).Clone()

for date in datesToPlot:	
	if date=='2012_8_30':
		CMS_lumi.lumi_8TeV = "13.4 fb^{-1}"
		iPeriod = 3
	else:
		CMS_lumi.lumi_8TeV = "23.3 fb^{-1}"
		CMS_lumi.lumi_13TeV= str(round(intLumis[date]-23.3-6.1,1))+" fb^{-1}"
		iPeriod = 7
			
	for par in parts: 
		gri['gri_'+par+'_'+date].SetMarkerColor(colors[par])
		gri['gri_'+par+'_'+date].SetFillColor(colors[par])
		gri['gri_'+par+'_'+date].SetMarkerStyle(8)
		gri['gri_'+par+'_'+date].SetMarkerSize(0.6)
		grt['grt_'+par+'_'+date].SetMarkerColor(colors[par])
		grt['grt_'+par+'_'+date].SetFillColor(colors[par])
		grt['grt_'+par+'_'+date].SetMarkerStyle(8)
		grt['grt_'+par+'_'+date].SetMarkerSize(0.6)
	
	mgnI = TMultiGraph()
	mgnI.SetTitle("")#Simulated and measured data on "+QDate)
	for par in parts: mgnI.Add(gri['gri_'+par+'_'+date],"p")

	mgnT = TMultiGraph()
	mgnT.SetTitle("")#Simulated and measured data on "+QDate)
	for par in parts: mgnT.Add(grt['grt_'+par+'_'+date],"p")

	canv1 = TCanvas(date+'_1',date+'_1',50,50,W,H)
	canv1.SetFillColor(0)
	canv1.SetBorderMode(0)
	canv1.SetFrameFillStyle(0)
	canv1.SetFrameBorderMode(0)
	canv1.SetTickx(0)
	canv1.SetTicky(0)
	canv1.SetLeftMargin( L/W )
	canv1.SetRightMargin( R/W )
	canv1.SetTopMargin( T/H )
	canv1.SetBottomMargin( B/H )
	gStyle.SetFillColor(kWhite)

	canv1.SetGrid()
	mgnI.Draw("AP")
	mgnI.GetYaxis().CenterTitle()
	mgnI.GetXaxis().SetTitle(XaxisnameI)
	mgnI.GetYaxis().SetTitle(YaxisnameI)
	mgnI.GetXaxis().SetLimits(ileakMins[date],ileakMaxs[date])
	mgnI.GetHistogram().SetMinimum(ileakMins[date])
	mgnI.GetHistogram().SetMaximum(ileakMaxs[date])
	mgnI.GetYaxis().SetTitleOffset(1.1)

	legDummy = TLegend(0.15,0.70,0.40,0.90)
	legDummy.SetShadowColor(0)
	#legDummy.SetFillColor(0)
	#legDummy.SetFillStyle(0)
	legDummy.SetLineColor(0)
	legDummy.SetLineStyle(0)
	legDummy.SetBorderSize(0) 
	legDummy.SetTextFont(42)
	#for par in parts: legDummy.AddEntry(gri['gri_'+par+'_'+date],par,"f")
	legDummy.Draw()

	#draw the lumi text on the canvas
	CMS_lumi.CMS_lumi(canv1, iPeriod, iPos)
	
	canv1.cd()
	canv1.Update()
	canv1.RedrawAxis()
	frame = canv1.GetFrame()
	frame.Draw()

	legI = TLegend(x1,y1,x2,y2)
	legI.SetShadowColor(0)
	#legI.SetFillColor(0)
	#legI.SetFillStyle(0)
	legI.SetLineColor(0)
	legI.SetLineStyle(0)
	legI.SetBorderSize(0) 
	legI.SetTextFont(42)
	for par in parts: legI.AddEntry(gri['gri_'+par+'_'+date],par,"f")
	legI.Draw()

	canv1.SaveAs(plotPath+'_esthetic/Ileak_'+date+".pdf")
	canv1.SaveAs(plotPath+'_esthetic/Ileak_'+date+".eps")
	canv1.SaveAs(plotPath+'_esthetic/Ileak_'+date+".png")
	canv1.SaveAs(plotPath+'_esthetic/Ileak_'+date+".root")

	canv2 = TCanvas(date+'_2',date+'_2',50,50,W,H)
	canv2.SetFillColor(0)
	canv2.SetBorderMode(0)
	canv2.SetFrameFillStyle(0)
	canv2.SetFrameBorderMode(0)
	canv2.SetTickx(0)
	canv2.SetTicky(0)
	canv2.SetLeftMargin( L/W )
	canv2.SetRightMargin( R/W )
	canv2.SetTopMargin( T/H )
	canv2.SetBottomMargin( B/H )
	gStyle.SetFillColor(kWhite)

	canv2.SetGrid()
	mgnT.Draw("AP")
	mgnT.GetYaxis().CenterTitle()
	mgnT.GetXaxis().SetTitle(XaxisnameT)
	mgnT.GetYaxis().SetTitle(YaxisnameT)
	mgnT.GetXaxis().SetLimits(tsilMins[date],tsilMaxs[date])
	mgnT.GetHistogram().SetMinimum(tsilMins[date])
	mgnT.GetHistogram().SetMaximum(tsilMaxs[date])
	mgnT.GetYaxis().SetTitleOffset(1.1)

	legDummy = TLegend(0.15,0.70,0.40,0.90)
	legDummy.SetShadowColor(0)
	#legDummy.SetFillColor(0)
	#legDummy.SetFillStyle(0)
	legDummy.SetLineColor(0)
	legDummy.SetLineStyle(0)
	legDummy.SetBorderSize(0) 
	legDummy.SetTextFont(42)
	#for par in parts: legDummy.AddEntry(gri['gri_'+par+'_'+date],par,"f")
	legDummy.Draw()
		
	#draw the lumi text on the canvas
	CMS_lumi.CMS_lumi(canv2, iPeriod, iPos)

	canv2.cd()
	canv2.Update()
	canv2.RedrawAxis()
	frame = canv2.GetFrame()
	frame.Draw()

	legT = TLegend(x1,y1,x2,y2)
	legT.SetShadowColor(0)
	#legT.SetFillColor(0)
	#legT.SetFillStyle(0)
	legT.SetLineColor(0)
	legT.SetLineStyle(0)
	legT.SetBorderSize(0) 
	legT.SetTextFont(42)
	for par in parts: legT.AddEntry(grt['grt_'+par+'_'+date],par,"f")
	legT.Draw()

	canv2.SaveAs(plotPath+'_esthetic/Temp_'+date+".pdf")
	canv2.SaveAs(plotPath+'_esthetic/Temp_'+date+".eps")
	canv2.SaveAs(plotPath+'_esthetic/Temp_'+date+".png")
	canv2.SaveAs(plotPath+'_esthetic/Temp_'+date+".root")

for date in datesToPlot:	
	if date=='2012_8_30':
		CMS_lumi.lumi_8TeV = "13.4 fb^{-1}"
		iPeriod = 3
	else:
		CMS_lumi.lumi_8TeV = "23.3 fb^{-1}"
		CMS_lumi.lumi_13TeV= str(round(intLumis[date]-23.3-6.1,1))+" fb^{-1}"
		iPeriod = 7
			
	for par in parts: 
		hi['hi_'+par+'_'+date].SetLineColor(colors[par])
		hi['hi_'+par+'_'+date].SetLineWidth(3)
		ht['ht_'+par+'_'+date].SetLineColor(colors[par])
		ht['ht_'+par+'_'+date].SetLineWidth(3)

	canv3 = TCanvas(date+'_3',date+'_3',50,50,W,H)
	canv3.SetFillColor(0)
	canv3.SetBorderMode(0)
	canv3.SetFrameFillStyle(0)
	canv3.SetFrameBorderMode(0)
	canv3.SetTickx(0)
	canv3.SetTicky(0)
	canv3.SetLeftMargin( L/W )
	canv3.SetRightMargin( R/W )
	canv3.SetTopMargin( T/H )
	canv3.SetBottomMargin( B/H )
	gStyle.SetFillColor(kWhite)

	#canv3.SetGrid()
	gStyle.SetOptStat(1)
	histMax = 1.1*max(hi['hi_TIB_'+date].GetMaximum(),hi['hi_TID_'+date].GetMaximum(),hi['hi_TOB_'+date].GetMaximum(),hi['hi_TEC_'+date].GetMaximum())
	hi['hi_TID_'+date].Draw("HIST")
	hi['hi_TID_'+date].GetYaxis().CenterTitle()
	hi['hi_TID_'+date].GetXaxis().SetTitle("(Simulated - Measured)/Measured [Current]")
	hi['hi_TID_'+date].GetYaxis().SetTitle("Modules")
	hi['hi_TID_'+date].GetXaxis().SetTitleSize(0.05)
	hi['hi_TID_'+date].GetYaxis().SetTitleSize(0.05)
	hi['hi_TID_'+date].GetYaxis().SetTitleOffset(1.1)
	hi['hi_TID_'+date].GetXaxis().SetTitleOffset(0.95)
	hi['hi_TID_'+date].SetMaximum(histMax)
	gPad.Update()
	sBoxH = 0.15
	sBoxW = 0.20
	sBoxX0 = 0.72
	sBoxY0 = 0.26
	statsI1 = hi['hi_TID_'+date].FindObject("stats").Clone("statsI1")
	tconst1 = statsI1.GetLineWith("hi_")
	tconst2 = statsI1.GetLineWith("Entries")
	tconst3 = statsI1.GetLineWith("Mean")
	tconst4 = statsI1.GetLineWith("Std")
	listOfLines1 = statsI1.GetListOfLines()
	listOfLines1.Remove(tconst1)
	listOfLines1.Remove(tconst2)
	listOfLines1.Remove(tconst3)
	listOfLines1.Remove(tconst4)
	myt = TLatex(0,0,"TID")
	myt.SetTextFont(42)
	myt.SetTextSize(0.04)
	myt.SetTextColor(colors['TID'])
	listOfLines1.Add(myt)
	listOfLines1.Add(tconst2)
	listOfLines1.Add(tconst3)
	listOfLines1.Add(tconst4)

	statsI1.SetY1NDC(sBoxY0)
	statsI1.SetY2NDC(sBoxY0+sBoxH)
	statsI1.SetX1NDC(sBoxX0)
	statsI1.SetX2NDC(sBoxX0+sBoxW)
	statsI1.SetTextColor(colors['TID'])
	hi['hi_TIB_'+date].Draw("SAME HIST")
	gPad.Update()
	statsI2 = hi['hi_TIB_'+date].GetListOfFunctions().FindObject("stats").Clone("statsI2")
	tconst1 = statsI2.GetLineWith("hi_")
	tconst2 = statsI2.GetLineWith("Entries")
	tconst3 = statsI2.GetLineWith("Mean")
	tconst4 = statsI2.GetLineWith("Std")
	listOfLines2 = statsI2.GetListOfLines()
	listOfLines2.Remove(tconst1)
	listOfLines2.Remove(tconst2)
	listOfLines2.Remove(tconst3)
	listOfLines2.Remove(tconst4)
	myt = TLatex(0,0,"TIB")
	myt.SetTextFont(42)
	myt.SetTextSize(0.04)
	myt.SetTextColor(colors['TIB'])
	listOfLines2.Add(myt)
	listOfLines2.Add(tconst2)
	listOfLines2.Add(tconst3)
	listOfLines2.Add(tconst4)

	statsI2.SetY1NDC(sBoxY0+sBoxH)
	statsI2.SetY2NDC(sBoxY0+2*sBoxH)
	statsI2.SetX1NDC(sBoxX0)
	statsI2.SetX2NDC(sBoxX0+sBoxW)
	statsI2.SetTextColor(colors['TIB'])
	#statsI2.SetTitle('TIB')
	hi['hi_TOB_'+date].Draw("SAME HIST")
	gPad.Update()
	statsI3 = hi['hi_TOB_'+date].GetListOfFunctions().FindObject("stats").Clone("statsI3")
	tconst1 = statsI3.GetLineWith("hi_")
	tconst2 = statsI3.GetLineWith("Entries")
	tconst3 = statsI3.GetLineWith("Mean")
	tconst4 = statsI3.GetLineWith("Std")
	listOfLines3 = statsI3.GetListOfLines()
	listOfLines3.Remove(tconst1)
	listOfLines3.Remove(tconst2)
	listOfLines3.Remove(tconst3)
	listOfLines3.Remove(tconst4)
	myt = TLatex(0,0,"TOB")
	myt.SetTextFont(42)
	myt.SetTextSize(0.04)
	myt.SetTextColor(colors['TOB'])
	listOfLines3.Add(myt)
	listOfLines3.Add(tconst2)
	listOfLines3.Add(tconst3)
	listOfLines3.Add(tconst4)

	statsI3.SetY1NDC(sBoxY0+2*sBoxH)
	statsI3.SetY2NDC(sBoxY0+3*sBoxH)
	statsI3.SetX1NDC(sBoxX0)
	statsI3.SetX2NDC(sBoxX0+sBoxW)
	statsI3.SetTextColor(colors['TOB'])
	hi['hi_TEC_'+date].Draw("SAME HIST")
	gPad.Update()
	statsI4 = hi['hi_TEC_'+date].GetListOfFunctions().FindObject("stats").Clone("statsI4")
	tconst1 = statsI4.GetLineWith("hi_")
	tconst2 = statsI4.GetLineWith("Entries")
	tconst3 = statsI4.GetLineWith("Mean")
	tconst4 = statsI4.GetLineWith("Std")
	listOfLines4 = statsI4.GetListOfLines()
	listOfLines4.Remove(tconst1)
	listOfLines4.Remove(tconst2)
	listOfLines4.Remove(tconst3)
	listOfLines4.Remove(tconst4)
	myt = TLatex(0,0,"TEC")
	myt.SetTextFont(42)
	myt.SetTextSize(0.04)
	myt.SetTextColor(colors['TEC'])
	listOfLines4.Add(myt)
	listOfLines4.Add(tconst2)
	listOfLines4.Add(tconst3)
	listOfLines4.Add(tconst4)

	statsI4.SetY1NDC(sBoxY0+3*sBoxH)
	statsI4.SetY2NDC(sBoxY0+4*sBoxH)
	statsI4.SetX1NDC(sBoxX0)
	statsI4.SetX2NDC(sBoxX0+sBoxW)
	statsI4.SetTextColor(colors['TEC'])
	gStyle.SetOptStat(0)

	hi['hi_TID_'+date].GetXaxis().SetTitleColor(1)
	hi['hi_TID_'+date].GetXaxis().SetTitleFont(42)
	hi['hi_TID_'+date].GetXaxis().SetTitleSize(0.06)
	hi['hi_TID_'+date].GetYaxis().SetTitleColor(1)
	hi['hi_TID_'+date].GetYaxis().SetTitleFont(42)
	hi['hi_TID_'+date].GetYaxis().SetTitleSize(0.06)
	hi['hi_TID_'+date].SetLabelColor(1, "XYZ")
	hi['hi_TID_'+date].SetLabelFont(42, "XYZ")
	hi['hi_TID_'+date].SetLabelOffset(0.007, "XYZ")
	hi['hi_TID_'+date].SetLabelSize(0.05, "XYZ")

	hi['hi_TID_'+date].Draw("HIST")
	hi['hi_TIB_'+date].Draw("SAME HIST")
	hi['hi_TOB_'+date].Draw("SAME HIST")
	hi['hi_TEC_'+date].Draw("SAME HIST")
	statsI1.Draw()
	statsI2.Draw()
	statsI3.Draw()
	statsI4.Draw()

	#draw the lumi text on the canvas
	CMS_lumi.CMS_lumi(canv3, iPeriod, iPos)

	canv3.cd()
	canv3.Update()
	canv3.RedrawAxis()
	frame = canv3.GetFrame()
	frame.Draw()
	
	canv3.SaveAs(plotPath+'_esthetic/Ileak_'+date+"_pull.pdf")
	canv3.SaveAs(plotPath+'_esthetic/Ileak_'+date+"_pull.eps")
	canv3.SaveAs(plotPath+'_esthetic/Ileak_'+date+"_pull.png")
	canv3.SaveAs(plotPath+'_esthetic/Ileak_'+date+"_pull.root")

	if date=='2023_7_16' or date=='2023_9_1': sBoxX0 = 0.42
	canv4 = TCanvas(date+'_4',date+'_4',50,50,W,H)
	canv4.SetFillColor(0)
	canv4.SetBorderMode(0)
	canv4.SetFrameFillStyle(0)
	canv4.SetFrameBorderMode(0)
	canv4.SetTickx(0)
	canv4.SetTicky(0)
	canv4.SetLeftMargin( L/W )
	canv4.SetRightMargin( R/W )
	canv4.SetTopMargin( T/H )
	canv4.SetBottomMargin( B/H )
	gStyle.SetFillColor(kWhite)

	#canv4.SetGrid()
	gStyle.SetOptStat(101010)
	#gStyle.SetOptStat("rm")
	#gStyle.SetStatFormat("6.2g")
	histMax = 1.1*max(ht['ht_TIB_'+date].GetMaximum(),ht['ht_TID_'+date].GetMaximum(),ht['ht_TOB_'+date].GetMaximum(),ht['ht_TEC_'+date].GetMaximum())
	ht['ht_TID_'+date].Draw("HIST")
	ht['ht_TID_'+date].GetYaxis().CenterTitle()
	ht['ht_TID_'+date].GetXaxis().SetTitle("(Simulated - Measured)/Measured [Temperature]")
	ht['ht_TID_'+date].GetYaxis().SetTitle("Modules")
	ht['ht_TID_'+date].GetXaxis().SetTitleSize(0.05)
	ht['ht_TID_'+date].GetYaxis().SetTitleSize(0.05)
	ht['ht_TID_'+date].GetYaxis().SetTitleOffset(1.1)
	ht['ht_TID_'+date].GetXaxis().SetTitleOffset(0.95)
	ht['ht_TID_'+date].SetMaximum(histMax)
	gPad.Update()
	statsI1 = ht['ht_TID_'+date].FindObject("stats").Clone("statsI1")
	tconst1 = statsI1.GetLineWith("ht_")
	tconst2 = statsI1.GetLineWith("Entries")
	tconst3 = statsI1.GetLineWith("Mean")
	tconst4 = statsI1.GetLineWith("Std")
	listOfLines1 = statsI1.GetListOfLines()
	listOfLines1.Remove(tconst1)
	listOfLines1.Remove(tconst2)
	listOfLines1.Remove(tconst3)
	listOfLines1.Remove(tconst4)
	myt = TLatex(0,0,"TID")
	myt.SetTextFont(42)
	myt.SetTextSize(0.04)
	myt.SetTextColor(colors['TID'])
	listOfLines1.Add(myt)
	listOfLines1.Add(tconst2)
	listOfLines1.Add(tconst3)
	listOfLines1.Add(tconst4)

	statsI1.SetY1NDC(sBoxY0)
	statsI1.SetY2NDC(sBoxY0+sBoxH)
	statsI1.SetX1NDC(sBoxX0)
	statsI1.SetX2NDC(sBoxX0+sBoxW)
	statsI1.SetTextColor(colors['TID'])
	ht['ht_TIB_'+date].Draw("SAME HIST")
	gPad.Update()
	statsI2 = ht['ht_TIB_'+date].GetListOfFunctions().FindObject("stats").Clone("statsI2")
	tconst1 = statsI2.GetLineWith("ht_")
	tconst2 = statsI2.GetLineWith("Entries")
	tconst3 = statsI2.GetLineWith("Mean")
	tconst4 = statsI2.GetLineWith("Std")
	listOfLines2 = statsI2.GetListOfLines()
	listOfLines2.Remove(tconst1)
	listOfLines2.Remove(tconst2)
	listOfLines2.Remove(tconst3)
	listOfLines2.Remove(tconst4)
	myt = TLatex(0,0,"TIB")
	myt.SetTextFont(42)
	myt.SetTextSize(0.04)
	myt.SetTextColor(colors['TIB'])
	listOfLines2.Add(myt)
	listOfLines2.Add(tconst2)
	listOfLines2.Add(tconst3)
	listOfLines2.Add(tconst4)

	statsI2.SetY1NDC(sBoxY0+sBoxH)
	statsI2.SetY2NDC(sBoxY0+2*sBoxH)
	statsI2.SetX1NDC(sBoxX0)
	statsI2.SetX2NDC(sBoxX0+sBoxW)
	statsI2.SetTextColor(colors['TIB'])
	#statsI2.SetTitle('TIB')
	ht['ht_TOB_'+date].Draw("SAME HIST")
	gPad.Update()
	statsI3 = ht['ht_TOB_'+date].GetListOfFunctions().FindObject("stats").Clone("statsI3")
	tconst1 = statsI3.GetLineWith("ht_")
	tconst2 = statsI3.GetLineWith("Entries")
	tconst3 = statsI3.GetLineWith("Mean")
	tconst4 = statsI3.GetLineWith("Std")
	listOfLines3 = statsI3.GetListOfLines()
	listOfLines3.Remove(tconst1)
	listOfLines3.Remove(tconst2)
	listOfLines3.Remove(tconst3)
	listOfLines3.Remove(tconst4)
	myt = TLatex(0,0,"TOB")
	myt.SetTextFont(42)
	myt.SetTextSize(0.04)
	myt.SetTextColor(colors['TOB'])
	listOfLines3.Add(myt)
	listOfLines3.Add(tconst2)
	listOfLines3.Add(tconst3)
	listOfLines3.Add(tconst4)

	statsI3.SetY1NDC(sBoxY0+2*sBoxH)
	statsI3.SetY2NDC(sBoxY0+3*sBoxH)
	statsI3.SetX1NDC(sBoxX0)
	statsI3.SetX2NDC(sBoxX0+sBoxW)
	statsI3.SetTextColor(colors['TOB'])
	ht['ht_TEC_'+date].Draw("SAME HIST")
	gPad.Update()
	statsI4 = ht['ht_TEC_'+date].GetListOfFunctions().FindObject("stats").Clone("statsI4")
	tconst1 = statsI4.GetLineWith("ht_")
	tconst2 = statsI4.GetLineWith("Entries")
	tconst3 = statsI4.GetLineWith("Mean")
	tconst4 = statsI4.GetLineWith("Std")
	listOfLines4 = statsI4.GetListOfLines()
	listOfLines4.Remove(tconst1)
	listOfLines4.Remove(tconst2)
	listOfLines4.Remove(tconst3)
	listOfLines4.Remove(tconst4)
	myt = TLatex(0,0,"TEC")
	myt.SetTextFont(42)
	myt.SetTextSize(0.04)
	myt.SetTextColor(colors['TEC'])
	listOfLines4.Add(myt)
	listOfLines4.Add(tconst2)
	listOfLines4.Add(tconst3)
	listOfLines4.Add(tconst4)

	statsI4.SetY1NDC(sBoxY0+3*sBoxH)
	statsI4.SetY2NDC(sBoxY0+4*sBoxH)
	statsI4.SetX1NDC(sBoxX0)
	statsI4.SetX2NDC(sBoxX0+sBoxW)
	statsI4.SetTextColor(colors['TEC'])
	gStyle.SetOptStat(0)

	ht['ht_TID_'+date].GetXaxis().SetTitleColor(1)
	ht['ht_TID_'+date].GetXaxis().SetTitleFont(42)
	ht['ht_TID_'+date].GetXaxis().SetTitleSize(0.057)
	ht['ht_TID_'+date].GetYaxis().SetTitleColor(1)
	ht['ht_TID_'+date].GetYaxis().SetTitleFont(42)
	ht['ht_TID_'+date].GetYaxis().SetTitleSize(0.06)
	ht['ht_TID_'+date].SetLabelColor(1, "XYZ")
	ht['ht_TID_'+date].SetLabelFont(42, "XYZ")
	ht['ht_TID_'+date].SetLabelOffset(0.007, "XYZ")
	ht['ht_TID_'+date].SetLabelSize(0.05, "XYZ")
	
	ht['ht_TID_'+date].Draw("HIST")
	ht['ht_TIB_'+date].Draw("SAME HIST")
	ht['ht_TOB_'+date].Draw("SAME HIST")
	ht['ht_TEC_'+date].Draw("SAME HIST")
	statsI1.Draw()
	statsI2.Draw()
	statsI3.Draw()
	statsI4.Draw()

	#draw the lumi text on the canvas
	CMS_lumi.CMS_lumi(canv4, iPeriod, iPos)

	canv4.cd()
	canv4.Update()
	canv4.RedrawAxis()
	frame = canv4.GetFrame()
	frame.Draw()

	canv4.SaveAs(plotPath+'_esthetic/Temp_'+date+"_pull.pdf")
	canv4.SaveAs(plotPath+'_esthetic/Temp_'+date+"_pull.eps")
	canv4.SaveAs(plotPath+'_esthetic/Temp_'+date+"_pull.png")
	canv4.SaveAs(plotPath+'_esthetic/Temp_'+date+"_pull.root")

RFile.Close()