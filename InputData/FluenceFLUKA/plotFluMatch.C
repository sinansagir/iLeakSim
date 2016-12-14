#include "TF1.h"
#include "TMath.h"
#include "TROOT.h"
#include "TFile.h"
#include "TMultiGraph.h"
#include "TTree.h"
#include "TH1D.h"
#include "TStyle.h"
#include "TCanvas.h"
#include <iostream>
#include <fstream>
using namespace std;

Double_t k_B = 8.617343183775136189e-05; // eV/K
Double_t q_el = 1.60217653e-19; // C
Double_t eps0 = 8.854187817e-14; // As/Vcm
Double_t eps = 11.9;
Double_t ga = 1.54E-2;  // cm-1 //TDR p96 : 1.54e-2  //dierl : 1.81e-2
Double_t gY = 4.6E-2;  // cm-1 //        : 4.6e-2   //     :5.16e-2
Double_t a10 =  1.23e-17; // A/cm
int debug=0;            //
Double_t stb = 3.;


void plotFluMatch()
{
//Fluencies**************************************************************
  const Int_t n=16000;
  Int_t a,b,c,d,e,f,g,h,i;
  Double_t finflu_1[n],finflu_2[n], finflu_3[n], finflu_4[n], finflu_5[n], finflu_6[n], finflu_7[n], finflu_8[n],finflu_9[n],finalfluence_1[n],finalfluence_2[n],finalfluence_3[n],finalfluence_4[n],finalfluence_5[n],finalfluence_6[n],finalfluence_7[n],finalfluence_8[n];

TFile *f1 = new TFile("/Users/sinansagir/Research/Silicon_Research/RadiationMonitoring/Summary_RadMon_WT/InputData/FluenceMatching.root"); //open Tree Tracker
TTree *ileak = (TTree*)f1->Get("SimTree_old");
Int_t detid,partition;                    //Init Variables
Float_t finflu,volume,finalfluence;                  //position and geometric variables
ileak->SetBranchAddress("DETID_T",&detid);   //read in Branches
ileak->SetBranchAddress("FINFLU_T",&finflu); //new algo
ileak->SetBranchAddress("FINALFLUENCE_T",&finalfluence);  //old algo
ileak->SetBranchAddress("VOLUME_T",&volume); //in meter
ileak->SetBranchAddress("PARTITON_T",&partition); //in intager (1-8  -> TIB, TOB, TID, TEC min plu)
Int_t fluentries = (Int_t)ileak->GetEntries();   //assign tree data to variables

 for(Int_t jt =0; jt<fluentries; jt++)
   {
     ileak->GetEntry(jt);   i++;finflu_9[i]=finflu;                      //FluencematchTree
     if(partition==1) {finflu_1[a]=finflu;finalfluence_1[a]=finalfluence;a++;} //TIBm
     if(partition==2) {finflu_2[b]=finflu;finalfluence_2[b]=finalfluence;b++;} //TIBp
     if(partition==3) {finflu_3[c]=finflu;finalfluence_3[c]=finalfluence;c++;} //TOBm
     if(partition==4) {finflu_4[d]=finflu;finalfluence_4[d]=finalfluence;d++;} //TOBp
     if(partition==5) {finflu_5[e]=finflu;finalfluence_5[e]=finalfluence;e++;} //TIDm
     if(partition==6) {finflu_6[f]=finflu;finalfluence_6[f]=finalfluence;f++;} //TIDp
     if(partition==7) {finflu_7[g]=finflu;finalfluence_7[g]=finalfluence;g++;} //TECm
     if(partition==8) {finflu_8[h]=finflu;finalfluence_8[h]=finalfluence;h++;} //TECp
   }
 TCanvas *c1 = new TCanvas("c1","Compare Flumatchign",800,600);//Width, Height
 TMultiGraph *mg = new TMultiGraph();
 TGraph *g1 = new TGraph(a,finflu_1,finalfluence_1); //Data per day
 TGraph *g2 = new TGraph(b,finflu_2,finalfluence_2);
 TGraph *g3 = new TGraph(c,finflu_3,finalfluence_3);
 TGraph *g4 = new TGraph(d,finflu_4,finalfluence_4);
 TGraph *g5 = new TGraph(e,finflu_5,finalfluence_5);
 TGraph *g6 = new TGraph(f,finflu_6,finalfluence_6);
 TGraph *g7 = new TGraph(g,finflu_7,finalfluence_7);
 TGraph *g8 = new TGraph(h,finflu_8,finalfluence_8);
 TGraph *g9 = new TGraph(i,finflu_9,finflu_9);

 g1->SetMarkerColor(kRed); g2->SetMarkerColor(kRed); g3->SetMarkerColor(kBlue); g4->SetMarkerColor(kBlue);
 g5->SetMarkerColor(kGreen); g6->SetMarkerColor(kGreen); g7->SetMarkerColor(kYellow); g8->SetMarkerColor(kYellow);
 
 mg->Add(g1);mg->Add(g2);mg->Add(g3);mg->Add(g4);mg->Add(g5);mg->Add(g6);mg->Add(g7);mg->Add(g8);mg->Add(g9);
 c1->cd(1); mg->Draw("AP");

}
