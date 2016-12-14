#!/usr/bin/python

import math as pmath

alpha10  = 1.23e-17 # A/cm
k_B  = 8.617343183775136189e-05 # eV/K

#Definition of functions (Moll Parameters as Input)
#Exact definition from CB's thesis: Eqns 2.60 and 2.61

# Annealing part: alpha0
def f_alpha0(T,a01,a02):
	if a01==0: a01 = -8.9e-17 # A/cm
	if a02==0: a02 = 4.6e-14 # AK/cm
	return a01+(a02/T) # A/cm

# Annealing part: alpha1
def f_alpha1(T,k0,E,t):
	if k0==0: k0 = 1.2e13 # 1/s
	if E==0: E = 1.11 # eV
	invt =  k0*pmath.exp(-E/(k_B*T))*86400.*t # where t is in days (fraction of a day can be used; e.g., t is 0.5 for 12 hours...)
	return pmath.exp(-invt)

# Annealing part: beta
def f_beta(t,b):
	if b==0: b = 3.07e-18 # A/cm
	return -b*pmath.log(t*1440.) # log(t/t0), where t0 is taken to be 1min and t is in days

# Leakage current scaling to a reference temperature "Tref" from measurement temperature "T"
def LeakCorrection(Tref,T):
	E = 1.21 # formerly 1.12 eV
	return (Tref/T)*(Tref/T)*pmath.exp(-E/(2.*k_B)*(1./Tref-1./T))

#*******************************Definition of MAIN Simulation Function**************************************************
def LeakCalculation(periode,Tallf,temperature,Feqf,Ileakf,volumef,dtdpf,paramf):
	maxTime=4*periode # 4* since there are 4 tracker states for each day	
	darkCurrent = []
	fluence     = []
	for i in range(maxTime):
		darkCurrent.append(Ileakf)
		fluence.append(Feqf[i])
	
	IleakSim={}
	IleakSim['fluence']=[]
	IleakSim['iLeakON']=[]
	IleakSim['iLeakOF']=[]
	IleakSim['iLeakSB']=[]
	IleakSim['iLeakSD']=[]
	IleakSim['tempON']=[]
	IleakSim['tempOF']=[]
	IleakSim['tempSB']=[]
	IleakSim['tempSD']=[]
	OneDaySum=0
	RestDaySum=maxTime/4
	for j in range(1,maxTime): #simulate leakage current per day
		if j%4==0: # j=4,8,12,...
			IleakSim['tempON'].append(temperature[j-4])  # append values corresponding to tracker ON state of the day
			IleakSim['tempOF'].append(temperature[j-3])  # append values corresponding to tracker OFF state of the day
			IleakSim['tempSB'].append(temperature[j-2])  # append values corresponding to tracker STAND-BY state of the day
			IleakSim['tempSD'].append(temperature[j-1])  # append values corresponding to tracker SHUT-DOWN state of the day
			IleakSim['iLeakON'].append(darkCurrent[j-4]) # append values corresponding to tracker ON state of the day
			IleakSim['iLeakOF'].append(darkCurrent[j-3]) # append values corresponding to tracker OFF state of the day
			IleakSim['iLeakSB'].append(darkCurrent[j-2]) # append values corresponding to tracker STAND-BY state of the day
			IleakSim['iLeakSD'].append(darkCurrent[j-1]) # append values corresponding to tracker SHUT-DOWN state of the day
			IleakSim['fluence'].append(max(fluence[j-4],fluence[j-3],fluence[j-2],fluence[j-1])) # Fluence of the day
			OneDaySum=0 # resets values for each Day
			if int(RestDaySum-Tallf[j-5])%100==0:
				print "Remaining days to simulate =",int(RestDaySum-Tallf[j-5])
		if Tallf[j-1]==0: continue # continue if a specific tracker state didn't take place during the day
		OneDaySum+=Tallf[j-1] # OneDaySum needs to be initialized everyday
		if paramf[5]==0: alpha1 = alpha10 # value of alpha1 at t==0
		else: alpha1=paramf[5] # value of alpha1 at t==0
		alpha0 = f_alpha0(temperature[j-1],paramf[2],paramf[3]) # calculate all different alpha0 values for each day at different temperature
		RestDaySum=OneDaySum
		for k in range(j,maxTime): #starts always only at days which are left to add the additional current to the one caused by previous days
			alpha1 *= f_alpha1(temperature[k-1],paramf[0],paramf[1],Tallf[k-1]) # * is + in exponent where time increment Tallf[k] is added in the exponent
			if f_alpha0(temperature[k-1],paramf[2],paramf[3])<alpha0: alpha0 = f_alpha0(temperature[k-1],paramf[2],paramf[3]) # can only decrease
			beta = f_beta(RestDaySum,paramf[4])
			darkCurrent[k]+=(alpha0+alpha1+beta)*fluence[j-1]*volumef*1000. # in mA per module 
			temperature[k]+=(alpha0+alpha1+beta)*fluence[j-1]*volumef*300.*dtdpf*LeakCorrection(temperature[k-1],293.16) # temperature correction
			RestDaySum+=Tallf[k]
	#append also the last day:
	IleakSim['tempON'].append(temperature[-4])
	IleakSim['tempOF'].append(temperature[-3])
	IleakSim['tempSB'].append(temperature[-2])
	IleakSim['tempSD'].append(temperature[-1])
	IleakSim['iLeakON'].append(darkCurrent[-4])
	IleakSim['iLeakOF'].append(darkCurrent[-3])
	IleakSim['iLeakSB'].append(darkCurrent[-2])
	IleakSim['iLeakSD'].append(darkCurrent[-1])
	IleakSim['fluence'].append(max(fluence[-4],fluence[-3],fluence[-2],fluence[-1]))
			
	#for i in range(periode): #scale leakage current back to original temperature --> this can also be done during comparison to measurements
	#	IleakSim['iLeakON'][i]*=LeakCorrection(IleakSim['tempON'][i],293.16)
	#	IleakSim['iLeakOF'][i]*=LeakCorrection(IleakSim['tempOF'][i],293.16)
	#	IleakSim['iLeakSB'][i]*=LeakCorrection(IleakSim['tempSB'][i],293.16)
	#	IleakSim['iLeakSD'][i]*=LeakCorrection(IleakSim['tempSD'][i],293.16)
	
	return IleakSim

