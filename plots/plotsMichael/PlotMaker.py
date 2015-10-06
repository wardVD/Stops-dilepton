import ROOT
from ROOT import TTree, TFile, AddressOf, gROOT, TH1F, TString
from array import array
import numpy as n
from math import *
import string



dataset_name 		= ["T2ttS425N325", "T2ttS650N325", "TTJets", "WJets", "QCDMu", "DrellYan", "QCDMu", "singleTop", "DoubleElec", "DoubleMuon", "MuonElec"] 

plot = TH1F("plot", "plot", 50, 0, 1000) 

f = ROOT.TFile.Open("ntuples/"+dataset_name[2]+".root")

#for process in range(len(dataset_name)):

lumi = 0.2042

for event in f.AnaTree :

	#if event.MET > 80 and event.MET/sqrt(event.HT) > 5 and cos(event.METPhi - event.LeadingJet.Phi())<cos(0.25) and cos(event.METPhi - event.SubLeadingJet.Phi())<cos(0.25): 
	if event.MET > 80 and event.MET/sqrt(event.HT) > 5: 

  		plot.Fill( event.MET , event.eventWeight*lumi)
  		print event.eventWeight
#c1 = ROOT.TCanvas()
#mt2ll.Draw('')
#c1.SetLogy()
#c1.Print("~/www/php-plots/mt2bb_test.png")

print plot.Integral()
print plot.GetEntries()
