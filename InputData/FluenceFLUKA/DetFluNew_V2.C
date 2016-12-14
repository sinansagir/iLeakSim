#include "TF1.h"
#include "TMath.h"
#include "TROOT.h"
#include "TFile.h"
#include "TTree.h"
#include "TH1D.h"
#include "TStyle.h"
#include "TCanvas.h"
#include "TGraph.h"
#include "TProfile.h"
#include <vector>
#include <fstream>
#include <string>
#include <iostream>
using namespace std;

Float_t Abs(Float_t x)   // Annealing Fraction one*******************************
{
  return TMath::Sqrt(x*x);
}

void DetFluNew_V2()
{
  //  FILE * log;
  //log = fopen("/home/users/wtreb/RadMonitoring/Fluenc/BasicFiles/DetermineFluence/DetFlu_New_Old.dat","w");//Ausgabefile all in, log is handler, w+ if not overwrite 

  //***********************************Output Tree************************************************
  Float_t volume_t, finflu_t,finalfluence_t;
  Int_t detid_t, partition_t;

  TFile file("FluenceMatching14TeVcom.root", "RECREATE");
  TTree *Treeout_old = new TTree("SimTree_old","SimTree_old");
  Treeout_old->Branch("DETID_T",&detid_t,"DETID_T/I");
  Treeout_old->Branch("VOLUME_T",&volume_t,"VOLUME_T/F");
  Treeout_old->Branch("FINFLU_T",&finflu_t,"FINFLU_T/F");
  Treeout_old->Branch("FINALFLUENCE_T",&finalfluence_t,"FINALFLUENCE_T/F");   //periodes filled in by hand!!!!!!!![442]-> ileka is array
  Treeout_old->Branch("PARTITON_T",&partition_t,"PARTITION_T/I");

  //***********************************Tracker Map*************************************************
  TFile *f1 = new TFile("../TrackMap.root"); //open Tree Trackermap
  TTree *treemap = (TTree*)f1->Get("treemap");
  Int_t found, par,detid,structpos;                    //Init Variables
  Float_t x,y,z,l,w1,w2,d;                  //position and geometric variables in meter!!!
  Char_t partition[4],struc[5];
  treemap->SetBranchAddress("DETID",&detid);   //read in Branches
  treemap->SetBranchAddress("X",&x);       //x position of senosor all in Meter
  treemap->SetBranchAddress("Y",&y);       //y position of senosor
  treemap->SetBranchAddress("Z",&z);       //z position of sensor
  treemap->SetBranchAddress("L",&l);
  treemap->SetBranchAddress("W1",&w1);
  treemap->SetBranchAddress("D",&d);
  treemap->SetBranchAddress("W2",&w2);
  treemap->SetBranchAddress("Partition",&partition);
  treemap->SetBranchAddress("Struct",&struc);
  treemap->SetBranchAddress("StructPos",&structpos);
  Int_t mapentries = (Int_t)treemap->GetEntries();   //assign tree data to variables
  //Fluence from FLUKA********************************************************
  std::ifstream infilefluka("1MeVneq_7TeVbeam_2p5cm.dat");
  Float_t zpos[100000],rpos[100000],zpostemp,rpostemp; //Position in cylindric coordinates and in cm!!!
  Double_t fluence[100000],fluenceerror[100000],fluencetemp,fluenceerrortemp;
  Int_t nFLUKA=0;
  string line;
  if ( infilefluka ) 
    {
      while ( getline( infilefluka , line ) ) 
      	{if(nFLUKA==1)std::cout<<"Opend FLUKA File"<<endl;
  	  std::istringstream(line) >> zpostemp >> rpostemp >> fluencetemp >> fluenceerrortemp;
	  zpos[nFLUKA]=zpostemp;rpos[nFLUKA]=rpostemp;fluence[nFLUKA]=fluencetemp;fluenceerror[nFLUKA]=fluenceerrortemp; nFLUKA++;
	}
    }
  infilefluka.close( );
  
  Int_t desdetid=402672289;

  Float_t n1, n2, n3, X1, Y1, Z1, X4, Y4, Z4, R1, R4, k14,finalfluence, finflu, volume;
  TString TIBp("TIB+"), TIBm("TIB-"), TOBp("TOB+"), TOBm("TOB-"), TIDp("TID+"), TIDm("TID-"), TECp("TEC+"), TECm("TEC-"); 
  Float_t area=0;
  for(Int_t k =0; k<mapentries; k++)    //1. data matching till mapentries***********************************************+
  {                                     //k goes from 0 through all mapentries (entries of trackermap tree)
    Double_t fin=finflu/area;//had to divide though it afterwards calculates just one cm^2 and than multiplies with volume...
    std::cout<<"  loop nr.:"<<k<<"  of 15100, at:"<<detid<<"  fluence values found:"<<found <<" New:"<<fin<<" Old:"<<finalfluence<<endl; //" Fac:"<<finflu/(finalfluence)<<" app. Area:"<<area<<std::endl;
    treemap->GetEntry(k);
    //if(detid!=desdetid)continue;     
    found=0;
    x=100*x; y=100*y; z=100*z; w1=100*w1; w2=100*w2; l=100*l;   //rescale from m to cm of FLUKA grid
    volume= d*(w1+w2)*(l/2);        //for current generation in Simulation File, Volume later used in cm^3
    if(partition==TIBm){par=1;} if(partition==TIBp){par=2;} if(partition==TOBm){par=3;} if(partition==TOBp){par=4;} 
    if(partition==TIDm){par=5;} if(partition==TIDp){par=6;} if(partition==TECm){par=7;} if(partition==TECp){par=8;}
    n1=1/(TMath::Sqrt((x*x+y*y)*z*z));  //perp. to radius and z -> (xy0)x(00z)
    n2=1/(TMath::Sqrt(z*z));            //z coord does not change
    n3=1/(TMath::Sqrt(x*x+y*y));       //perp. to
   
    if(partition==TIBm || partition==TIBp || partition==TOBm || partition==TOBp) // || to z and |_ to r; w1=w2
     {
       X1=x-z*y*n1*w1/2;//inside (dir. z=0; -l/2), looking to center (z=0) left
       Y1=y+z*x*n1*w1/2; //n is norm to length of 1 cm
       Z1=z-z*n2*l/2;  //valid for all sides as (-z)-(-z) is same as z-z (both to center)
   
       X4=x+z*y*n1*w1/2;//outside (z), looking to center right
       Y4=y-z*x*n1*w1/2;
       Z4=z+z*n2*l/2;
     }
    else if(partition==TIDm || partition==TIDp || partition==TECm || partition==TECp)  // || to r and |_ to z; w1>w2
     {     
       X1=x-x*n3*l/2-z*y*n1*w2/2;//inside (dir r=0; -l/2)->w2, looking to center (r=0) left
       Y1=y-y*n3*l/2+z*x*n1*w2/2;
       Z1=z;
       
       X4=x+x*n3*l/2+z*y*n1*w1/2;//outside (r=0)->w1, looking to center right
       Y4=y+y*n3*l/2-z*x*n1*w1/2;
       Z4=z;
     }
    
    R1=TMath::Sqrt(X1*X1+Y1*Y1);
    R4=TMath::Sqrt(X4*X4+Y4*Y4);
    k14=((R4-R1)/(Z4-Z1));//slope of sensor in R Z Plane
    //std::cout<<"X1:"<<X1<<"Z1:"<<Z1<<"Y1:"<<Y1<<"X4:"<<X4<<"Z4:"<<Z4<<"Y4:"<<Y4<<"x"<<x<<"y"<<y<<"z"<<z<<std::endl; 
    finflu=0; finalfluence=0; area=0;   //initialize, sum up for each module starting witt 0
   
    for(Int_t n =0; n<nFLUKA; n++)             //n goes from 0 through all entries og fluence tree (Fluka)  
     {
      if(partition==TIBm || partition==TIBp || partition==TOBm || partition==TOBp)              //partition || to z !allways w1=w2
       {
        if(rpos[n]<k14*zpos[n]+(R1-k14*Z1) && rpos[n]+2.5>k14*zpos[n]+(R1-k14*Z1))                               //all r values beneath line
	 { 
	  if(z>0)               //positive z side 
	   {
	   if (zpos[n]>Z1-2.5 && zpos[n]<Z4)                   //All values inside range of z start and end of line incl 1st (-2.5) and last value 
	    { 
	    if(zpos[n]>Z1-2.5 && zpos[n]<Z1){finflu+=fluence[n]*w1*(2.5-(Z1-zpos[n]));found++;area+=w1*(2.5-(Z1-zpos[n]));}//first Value,
	    else if(zpos[n]<Z4 && zpos[n]+2.5>Z4){finflu+=fluence[n]*w1*(Z4-zpos[n]); found++;area+=w1*(Z4-zpos[n]);}       //last Value
	    else {finflu+=fluence[n]*w1*2.5; found++;area+=w1*2.5;}                                     //Values in between
	    } 
	   }    //end positive side
	  else if (z<0)  //neg z side
	   {
	   if (zpos[n]>Z4-2.5 && zpos[n]<Z1)   //incl 1st and last (-2.5) value
	    {
	      if(zpos[n]<Z1 && zpos[n]+2.5>Z1){finflu+=fluence[n]*w1*(Z1-zpos[n]); found++;area+=w1*(Z1-zpos[n]);}//std::cout<<area<<"  ";}//first Value, 
	    else if(zpos[n]>Z4-2.5 && zpos[n]<Z4){finflu+=fluence[n]*w1*(2.5-(Z4-zpos[n]));found++;area+=w1*(2.5-(Z4-zpos[n]));}//std::cout<<area<<"  ";}
	    else {finflu+=fluence[n]*w1*2.5; found++;area+=w1*2.5;}//std::cout<<area<<endl;}                                  //Values in between
	    }  //end of matching points
           }   //end neg side
         } //end position benath line
       }  //end partition TIB TOB
    
      else if(partition==TIDm || partition==TIDp || partition==TECm || partition==TECp)//partition |_ to z w1>w2
       {
	if(zpos[n]<Z1 && zpos[n]+2.5>Z1 && rpos[n]>R1-2.5 && rpos[n]<R4)   //all values including first and last one 
	 {
	 if(rpos[n]>R1-2.5 && rpos[n]<R1){finflu+=fluence[n]*(0.5*(2*w2+((2.5-R1+rpos[n])*(w1-w2))/l)*(2.5-R1+rpos[n]));found++;area+=0.5*(2*w2+((2.5-R1+rpos[n])*(w1-w2))/l)*(2.5-R1+rpos[n]);}  //first value
	 else if(rpos[n]<R4 && rpos[n]+2.5>R4){finflu+=fluence[n]*(0.5*(w2+w1+((l-R4+rpos[n])*(w1-w2))/l)*(R4-rpos[n]));found++;area+=0.5*(w2+w1+((l-R4+rpos[n])*(w1-w2))/l)*(R4-rpos[n]);}	//last value 
	 else {finflu+=fluence[n]*((2.5/l)*((w1-w2)*(rpos[n]-R1+(2.5/2))+w2*l));found++;area+=(2.5/l)*((w1-w2)*(rpos[n]-R1+(2.5/2))+w2*l);} //in between
	 }//end of matching points
       }//end all partition and new matching
      else break;
     }//close Fluka Tree again
   //****************************start of "old fluence matching"************************************************
    Float_t delta=1.2499, tempr, dislocate,flu1, flu2, searchpos;
    Int_t sumcase,f=1;
    if(f==1)
      {
	for(Int_t n =0; n<nFLUKA; n++)
	  {
	    if((zpos[n]>z)&&(zpos[n]<(z+2*delta)))  //calculates position due to flueunce, linear approximation for flu1, flu2
	      {      
		tempr=(TMath::Sqrt(x*x+y*y)); //zpos: position of fluence, z: module position, delta:?half lenght of module?resolution of fluence determin 
		if(tempr-rpos[n]>2.5) continue;            //case1: tempr:radius position, dislocation too large not used, 2.5 ~= 2*delta
		dislocate= tempr-rpos[n];                  //
		if((dislocate>=delta) && (dislocate<=2*delta))//case2: dislocation between delta and 2delta
		  {
		    flu2=fluence[n];
		    searchpos=rpos[n]+2.5;
		    sumcase =1;
		  }
		else if(dislocate>=0 && dislocate<=delta)//case3: dislocate between 0 and delta
		  {
		    flu2=fluence[n];
		    searchpos=rpos[n]-2.5;
		    sumcase =0;
		  }
		for(Int_t ni2=0; ni2<nFLUKA; ni2++) //going though all entries again to assign zpos, rpos and fluence to one module
		  {
		    if((zpos[ni2]>z-delta) && (zpos[ni2]<z+delta)) //-> find z pos
		      {
			if(rpos[ni2]==searchpos)   //serachpos before defined at different cases -> find rpos
			  {
			    flu1= fluence[ni2];  //-> find fluence, detid still valid from "higher tree"
			    break;
			  }
		      }
		  }
		finalfluence=((1-2*sumcase-dislocate/delta+2*dislocate/delta*sumcase)*flu1 + (1+2*sumcase + dislocate/delta-2*dislocate/delta*sumcase)*flu2)/2;
		f+=1;
		break;
	      }
	  }//end of new Fluka tree run
      } //end of if(f) and of old matching
    //x std::cout<< " detid:   " <<detid<< " flu1:   " << finflu*dPhi << " flu2:   " << finalfluence<<std::endl;
    //fprintf(log,"%d %f %f %f %i\n",detid,finflu,finalfluence,volume,par); //writes to file
    //std::cout<<detid<<"  "<<finalfluence<<endl;
    detid_t=detid;finflu_t=finflu/area;finalfluence_t=finalfluence;volume_t=volume;partition_t=par;
    Treeout_old->Fill();
   }//end of Trackermap
  Treeout_old->Print();
  file.cd();
  Treeout_old->Write();

}//end of Program
 
