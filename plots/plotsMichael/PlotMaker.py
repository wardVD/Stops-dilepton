import ROOT
from ROOT import TTree, TFile, AddressOf, gROOT, TH1F, TString
from array import array
import numpy as n
from math import *
import string

from StopsDilepton.tools.helpers import getChain, getObjDict, getEList, getVarValue, genmatching, latexmaker_1, piemaker, getWeight, deltaPhi



dataset_name 		= ["T2ttS425N325", "T2ttS650N325", "TTJets", "WJets", "QCDMu", "DrellYan", "QCDMu", "singleTop", "DoubleElec", "DoubleMuon", "MuonElec"] 




for process in range(len(dataset_name)):
	print dataset_name[process]

	lumi = 0.2042
	#lumi = 10.  

	f = ROOT.TFile.Open("ntuples2/"+dataset_name[process]+".root")
	plot = TH1F("plot", "plot", 50, 0, 1000) 

	for event in f.anaTree :

		isSF=0
		isOF=0

		ZVeto=abs(event.dileptonInvariantMass-90.2)>15

		if event.isElecElec or event.isMuonMuon:
			isSF=1
		if event.isMuonElec:
			isOF=1

	
		if event.HT > 0. and event.MET > 80 and event.minPhiMetJet12 > 0.25 and event.MET/sqrt(event.HT) > 5 and event.nbjets >0 and event.nleptons==2 and event.njets > 1 and isSF and ZVeto: 
		#if event.HT > 0. and event.MET > 80 and event.minPhiMetJet12 > 0.25 and event.MET/sqrt(event.HT) > 5 and event.nbjets >0 and event.nleptons==2 and event.njets > 1 and isOF: 

			if event.isMC: 
				plot.Fill( event.MET , event.xsecWeight*lumi)
			else:
				plot.Fill( event.MET)

	#c1 = ROOT.TCanvas()
	#mt2ll.Draw('')
	#c1.SetLogy()
	#c1.Print("~/www/php-plots/mt2bb_test.png")

	print "Scaled: \t %d " % plot.Integral()
	print "Raw: \t\t %i " % plot.GetEntries()
	print "***" 
