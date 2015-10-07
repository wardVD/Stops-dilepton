import ROOT
from ROOT import TTree, TFile, AddressOf, gROOT, TH1F, TString
from array import array
import numpy as n
from math import *
import string



dataset_name 		= ["T2ttS425N325", "T2ttS650N325", "TTJets", "WJets", "QCDMu", "DrellYan", "QCDMu", "singleTop", "DoubleElec", "DoubleMuon", "MuonElec"] 

plot = TH1F("plot", "plot", 50, 0, 1000) 

f = ROOT.TFile.Open("ntuples/"+dataset_name[2]+".root")

print dataset_name[2]
#for process in range(len(dataset_name)):

lumi = 0.2042


for event in f.AnaTree :

	#isSF=0

 #	if event.isElecElec or event.isMuonMuon:
	#	isSF=1

#	if event.MET > 80 and event.MET/sqrt(event.HT) > 5 and cos(event.METPhi - event.LeadingJet.Phi())<cos(0.25) and cos(event.METPhi - event.SubLeadingJet.Phi())<cos(0.25) and event.dileptonInvariantMass > 20 and event.nbjets >0 and event.nleptons>1 and event.njets > 1: 
#	if isSF==1 and abs(event.dileptonInvariantMass-90.2)>15 and event.MET > 40 and event.dileptonInvariantMass > 20 and event.nbjets >0 and event.nleptons==2 and event.njets > 1: 

	print event.eventWeight
	plot.Fill( event.MET , event.eventWeight*lumi)

	
#c1 = ROOT.TCanvas()
#mt2ll.Draw('')
#c1.SetLogy()
#c1.Print("~/www/php-plots/mt2bb_test.png")

print plot.Integral()
print plot.GetEntries()
