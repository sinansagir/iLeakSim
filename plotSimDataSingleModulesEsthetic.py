#!/usr/bin/python

import os,sys,fnmatch,math,pickle
from bisect import bisect_left
import numpy as np
from ROOT import *
import CMS_lumi, tdrstyle
gROOT.SetBatch(1)

#set the tdr style
tdrstyle.setTDRStyle()

#change the CMS_lumi variables (see CMS_lumi.py)
CMS_lumi.lumi_7TeV = "6.1 fb^{-1}"
CMS_lumi.lumi_8TeV = "13.4 fb^{-1}"
CMS_lumi.lumi_13TeV= "2.3 fb^{-1}"
CMS_lumi.writeExtraText = 1
CMS_lumi.extraText = "Preliminary"
CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)

iPos = 10
if( iPos==0 ): CMS_lumi.relPosX = 0.12

H_ref = 600; 
W_ref = 900;
W = W_ref
H  = H_ref

iPeriod = 0

# references for T, B, L, R
T = 0.12*H_ref
B = 0.14*H_ref
L = 0.12*W_ref
R = 0.08*W_ref

#******************************Input to edit******************************************************
simDate = "2023_9_4"
plotPath = "DarkSimAllModules_"+simDate+"/singleModules_data_DCU_raw"
runDir=os.getcwd()
isCurrentScaled = False # Scale current to measured temperature (Check how this is done!!!! The default method assumes that the simulated current is at 20C)
plotRawData = False
drawTempData = True
#if plotRawData: plotPath+="_raw" 

XaxisnameI = ""
YaxisnameI = "Current (mA)"
XaxisnameT = ""
YaxisnameT = "Temperature (#circC)"
x1=.14#.72 #for legs
y1=.18#.65
x2=x1+.25
y2=y1+.2

RFile = TFile(runDir+'/'+plotPath+'/outRfileSingleModules.root')

modParts  = {369120486:'TIB',436262468:'TOB'}
modLayers = {369120486:'1',  436262468:'3'}
grs = {}
ileakMins = {369120486:0.00005,436262468:0.00005}
ileakMaxs = {369120486:3.99,436262468:3.199}
tempMins  = {369120486:-20.99,436262468:-20.99}
tempMaxs  = {369120486:24.99,436262468:24.99}
xMin = TDatime(2011,1,14,0,0,1).Convert()
xMax = TDatime(2023,9,3,0,0,1).Convert()

LS1start = TDatime(2013,1,1,0,0,1).Convert()
LS1end   = TDatime(2015,3,15,0,0,1).Convert()
LS2start = TDatime(2018,12,1,0,0,1).Convert()
LS2end   = TDatime(2022,5,23,0,0,1).Convert()

for mod in [369120486,436262468]:
	grs[str(mod)+'_ileak_sim'] = RFile.Get(str(mod)+'_ileak_sim').Clone()
	grs[str(mod)+'_ileak_mea'] = RFile.Get(str(mod)+'_ileak_mea').Clone()
	grs[str(mod)+'_ileak_mea_raw'] = RFile.Get(str(mod)+'_ileak_mea_raw').Clone()
	grs[str(mod)+'_temp_sim'] = RFile.Get(str(mod)+'_temp_sim').Clone()
	grs[str(mod)+'_temp_mea'] = RFile.Get(str(mod)+'_temp_mea').Clone()
	grs[str(mod)+'_temp_mea_raw'] = RFile.Get(str(mod)+'_temp_mea_raw').Clone()

def formatUpperHist(histogram):
	histogram.GetXaxis().SetLabelSize(0)
	
	histogram.GetYaxis().SetNdivisions(506)
	histogram.GetYaxis().SetLabelSize(0.08)
	histogram.GetYaxis().SetTitleSize(0.08)
	histogram.GetYaxis().SetTitleOffset(.51)
	histogram.GetYaxis().CenterTitle()
		
def formatLowerHist(histogram):
	histogram.GetXaxis().SetLabelSize(.1)

	histogram.GetYaxis().SetNdivisions(506)
	histogram.GetYaxis().SetLabelSize(0.1)
	histogram.GetYaxis().SetTitleSize(0.09)
	histogram.GetYaxis().SetTitleOffset(.41)
	histogram.GetYaxis().CenterTitle()

for QuerrMod in [369120486,436262468]:	
	modPart = modParts[QuerrMod]
	#CMS_lumi.lumi_sqrtS = "Detector ID: "+str(QuerrMod)+" ["+modPart+"]"
	CMS_lumi.lumi_sqrtS = modPart+" module layer "+modLayers[QuerrMod]
	
	for meas in ['ileak','temp']:
		grs[str(QuerrMod)+'_'+meas+'_sim'].SetMarkerColor(kBlue)
		grs[str(QuerrMod)+'_'+meas+'_sim'].SetFillColor(kBlue)
		grs[str(QuerrMod)+'_'+meas+'_sim'].SetMarkerStyle(8)
		grs[str(QuerrMod)+'_'+meas+'_sim'].SetMarkerSize(0.6)
	
		grs[str(QuerrMod)+'_'+meas+'_mea'].SetMarkerColor(kRed)
		grs[str(QuerrMod)+'_'+meas+'_mea'].SetFillColor(kRed)
		grs[str(QuerrMod)+'_'+meas+'_mea'].SetMarkerStyle(8)
		grs[str(QuerrMod)+'_'+meas+'_mea'].SetMarkerSize(0.6)

		grs[str(QuerrMod)+'_'+meas+'_mea_raw'].SetMarkerColor(kRed)
		grs[str(QuerrMod)+'_'+meas+'_mea_raw'].SetFillColor(kRed)
		grs[str(QuerrMod)+'_'+meas+'_mea_raw'].SetMarkerStyle(8)
		grs[str(QuerrMod)+'_'+meas+'_mea_raw'].SetMarkerSize(0.6)
	
	mgnI = TMultiGraph()
	mgnI.SetTitle(modPart+" Module detector ID: "+str(QuerrMod))
	mgnI.Add(grs[str(QuerrMod)+'_ileak_sim'],"p")
	if plotRawData: mgnI.Add(grs[str(QuerrMod)+'_ileak_mea_raw'],"p")
	mgnI.Add(grs[str(QuerrMod)+'_ileak_mea'],"p")
	
	mgnT = TMultiGraph()
	mgnT.SetTitle("")
	mgnT.Add(grs[str(QuerrMod)+'_temp_sim'],"p")
	if drawTempData: 
		if plotRawData: mgnT.Add(grs[str(QuerrMod)+'_temp_mea_raw'],"p")
		mgnT.Add(grs[str(QuerrMod)+'_temp_mea'],"p")
		
	uline1 = TLine(LS1start,ileakMins[QuerrMod],LS1start,ileakMaxs[QuerrMod])
	uline1.SetLineColor(kBlack)
	uline1.SetLineWidth(3)
	uline1.SetLineStyle(2)
	uline2 = TLine(LS1end,ileakMins[QuerrMod],LS1end,ileakMaxs[QuerrMod])
	uline2.SetLineColor(kBlack)
	uline2.SetLineWidth(3)
	uline2.SetLineStyle(2)
	uline3 = TLine(LS2start,ileakMins[QuerrMod],LS2start,ileakMaxs[QuerrMod])
	uline3.SetLineColor(kBlack)
	uline3.SetLineWidth(3)
	uline3.SetLineStyle(2)
	uline4 = TLine(LS2end,ileakMins[QuerrMod],LS2end,ileakMaxs[QuerrMod])
	uline4.SetLineColor(kBlack)
	uline4.SetLineWidth(3)
	uline4.SetLineStyle(2)
	lline1 = TLine(LS1start,tempMins[QuerrMod],LS1start,tempMaxs[QuerrMod])
	lline1.SetLineColor(kBlack)
	lline1.SetLineWidth(3)
	lline1.SetLineStyle(2)
 	lline2 = TLine(LS1end,tempMins[QuerrMod],LS1end,tempMaxs[QuerrMod])
	lline2.SetLineColor(kBlack)
	lline2.SetLineWidth(3)
	lline2.SetLineStyle(2)
	lline3 = TLine(LS2start,tempMins[QuerrMod],LS2start,tempMaxs[QuerrMod])
	lline3.SetLineColor(kBlack)
	lline3.SetLineWidth(3)
	lline3.SetLineStyle(2)
 	lline4 = TLine(LS2end,tempMins[QuerrMod],LS2end,tempMaxs[QuerrMod])
	lline4.SetLineColor(kBlack)
	lline4.SetLineWidth(3)
	lline4.SetLineStyle(2)
 	
	cIT = TCanvas("Module_"+str(QuerrMod),"Module_"+str(QuerrMod),50,50,W,H)
	cIT.SetFillColor(0)
	cIT.SetBorderMode(0)
	cIT.SetFrameFillStyle(0)
	cIT.SetFrameBorderMode(0)
	cIT.SetTickx(0)
	cIT.SetTicky(0)
	
	yDiv=0.45
	uPad=TPad("uPad","",0,yDiv,1,1) #for actual plots
	
	uPad.SetLeftMargin( L/W )
	uPad.SetRightMargin( R/W )
	uPad.SetTopMargin( T/H )
	uPad.SetBottomMargin( 0 )	
	uPad.SetFillColor(0)
	uPad.SetBorderMode(0)
	uPad.SetFrameFillStyle(0)
	uPad.SetFrameBorderMode(0)
	uPad.SetTickx(0)
	uPad.SetTicky(0)
	#uPad.SetGrid()
	uPad.Draw()

	lPad=TPad("lPad","",0,0,1,yDiv) #for sigma runner
	lPad.SetLeftMargin( L/W )
	lPad.SetRightMargin( R/W )
	lPad.SetTopMargin( 0 )
	lPad.SetBottomMargin( B/H )
	lPad.SetFillColor(0)
	lPad.SetBorderMode(0)
	lPad.SetFrameFillStyle(0)
	lPad.SetFrameBorderMode(0)
	lPad.SetTickx(0)
	lPad.SetTicky(0)
	#lPad.SetGrid()
	lPad.Draw()
	
	uPad.cd()
	mgnI.Draw("AP")
	mgnI.GetXaxis().SetTimeDisplay(1)
	mgnI.GetXaxis().SetNdivisions(-503)
	mgnI.GetXaxis().SetTimeFormat("%Y-%m-%d")
	mgnI.GetXaxis().SetTimeOffset(0,"gmt")
	mgnI.GetXaxis().SetTitle(XaxisnameI)
	mgnI.GetYaxis().SetTitle(YaxisnameI)
	mgnI.GetXaxis().SetLimits(xMin,xMax)
	mgnI.GetHistogram().SetMinimum(ileakMins[QuerrMod])
	mgnI.GetHistogram().SetMaximum(ileakMaxs[QuerrMod])
	#mgnI.GetYaxis().SetTitleOffset(1.5)
	formatUpperHist(mgnI)
	
	uline1.Draw()
	uline2.Draw()
	uline3.Draw()
	uline4.Draw()
	
	#legI = TLegend(x1,y1,x2,y2)
	legI = TLegend(0.41,0.60,0.66,0.85)
	legI.SetShadowColor(0)
	legI.SetFillColor(0)
	legI.SetFillStyle(0)
	legI.SetLineColor(0)
	legI.SetLineStyle(0)
	legI.SetBorderSize(0) 
	legI.SetTextFont(42)
	legI.AddEntry(grs[str(QuerrMod)+'_ileak_sim'],"Simulated","p")
	legI.AddEntry(grs[str(QuerrMod)+'_ileak_mea'],"Measured","p")
	if plotRawData: legI.AddEntry(grs[str(QuerrMod)+'_ileak_mea_raw'],"Measured","p")
	legI.Draw()
	
	ttext = TLatex()
	ttext.SetNDC()
	ttext.SetTextSize(0.08)
	ttext.SetTextAlign(21) # align right
	ttext.DrawLatex(0.19, 0.5, "#color[4]{Run-I}")
	ttext.DrawLatex(0.32, 0.5, "#color[2]{LS-I}")
	ttext.DrawLatex(0.50, 0.5, "#color[4]{Run-II}")
	ttext.DrawLatex(0.73, 0.5, "#color[2]{LS-II}")
	ttext.DrawLatex(0.88, 0.5, "#color[4]{Run-III}")
	
	lPad.cd()
	mgnT.Draw("AP")
	mgnT.GetXaxis().SetTimeDisplay(1)
	mgnT.GetXaxis().SetNdivisions(-503)
	mgnT.GetXaxis().SetTimeFormat("%Y-%m-%d")
	mgnT.GetXaxis().SetTimeOffset(0,"gmt")
	mgnT.GetXaxis().SetTitle(XaxisnameT)
	mgnT.GetYaxis().SetTitle(YaxisnameT)
	mgnT.GetXaxis().SetLimits(xMin,xMax)
	mgnT.GetHistogram().SetMinimum(tempMins[QuerrMod])
	mgnT.GetHistogram().SetMaximum(tempMaxs[QuerrMod])
	formatLowerHist(mgnT)
	
	lline1.Draw()
	lline2.Draw()
	lline3.Draw()
	lline4.Draw()
	
	legT = TLegend(x1+0.00,y1+0.07,x2+0.00,y2+0.12)
	legT.SetShadowColor(0)
	legT.SetFillColor(0)
	legT.SetFillStyle(0)
	legT.SetLineColor(0)
	legT.SetLineStyle(0)
	legT.SetBorderSize(0) 
	legT.SetTextFont(42)
	legT.AddEntry(grs[str(QuerrMod)+'_temp_sim'],"Simulated","p")
	legT.AddEntry(grs[str(QuerrMod)+'_temp_mea'],"Measured","p")
	if plotRawData: legT.AddEntry(grs[str(QuerrMod)+'_temp_mea_raw'],"Measured","p")
	#legT.Draw()
	
	#draw the lumi text on the canvas
	CMS_lumi.CMS_lumi(uPad, iPeriod, 10)
	
	uPad.Update()
	uPad.RedrawAxis()
	frame = uPad.GetFrame()
	uPad.Draw()

	if not os.path.exists(runDir+'/'+plotPath+'_esthetic'): os.system('mkdir '+runDir+'/'+plotPath+'_esthetic')
	saveNameIT = plotPath+"_esthetic/IleakT_"+str(QuerrMod)
	if plotRawData: saveNameIT+="_raw"
	cIT.SaveAs(saveNameIT+".pdf")
	cIT.SaveAs(saveNameIT+".eps")
	cIT.SaveAs(saveNameIT+".png")
	cIT.SaveAs(saveNameIT+".root")

RFile.Close()