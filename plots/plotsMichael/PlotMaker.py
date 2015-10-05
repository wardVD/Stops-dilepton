import ROOT
from ROOT import TTree, TFile, AddressOf, gROOT, TH1F, TString
from array import array
import numpy as n
from math import *
import string



dataset_name 		= ["T2ttS425N325", "T2ttS650N325", "TTJets", "WJets", "QCDMu", "DrellYan", "QCDMu", "singleTop", "DoubleElec", "DoubleMuon", "MuonElec"] 
#plot_name 			= ["mt2ll", "mt2bb", "mt2blbl"]

mt2ll = TH1F("mt2ll", "mt2ll", 50, 0, 1000) 

f = ROOT.TFile.Open("ntuples/"+dataset_name[2]+".root")

#for process in range(len(dataset_name)):

lumi = 0.204

for event in f.AnaTree :
		#print dataset_name[process] 

#	if event.isElecElec and abs(event.dileptonInvariantMass - 90.2) >15.:
	if event.isMuonMuon and abs(event.dileptonInvariantMass - 90.2) >15.:
  		mt2ll.Fill( event.mt2ll , event.eventWeight*lumi)
#	if event.isMuonMuon and abs(event.dileptonInvariantMass - 90.2) >15.:
#  		mt2ll.Fill( event.mt2ll , event.eventWeight*lumi)

c1 = ROOT.TCanvas()
mt2ll.Draw('')
c1.SetLogy()
c1.Print("~/www/php-plots/mt2bb_test.png")

print mt2ll.Integral()
