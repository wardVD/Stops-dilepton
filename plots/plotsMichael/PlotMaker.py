import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()

from ROOT import TTree, TFile, AddressOf, gROOT, TH1F, TH2F, TString, TColor
from array import array
import numpy as n
from math import *
import string

from StopsDilepton.tools.helpers import getChain, getObjDict, getEList, getVarValue, genmatching, latexmaker_1, piemaker, getWeight, deltaPhi



#dataset_name 		= ["T2ttS425N325", "T2ttS650N325", "TTJets", "WJets", "QCDMu", "DrellYan", "QCDMu", "singleTop", "DoubleElec", "DoubleMuon", "MuonElec"] 
dataset_name 		= ["T2ttS425N325"] 



for process in range(len(dataset_name)):
	print dataset_name[process]

	#lumi = 0.2042
	lumi = 10.  

	f = ROOT.TFile.Open("ntuples/"+dataset_name[process]+".root")
	plot = TH1F("plot", "plot", 50, 0, 10000) 

	for event in f.anaTree :

		isSF=0
		isOF=0

		ZVeto=abs(event.dileptonInvariantMass-90.2)>15

		if event.isElecElec or event.isMuonMuon:
			isSF=1
		if event.isMuonElec:
			isOF=1

#		if event.HT > 0. and event.MET > 80 and event.mindPhiMetJet12 > 0.25 and event.MET/sqrt(event.HT) > 5 and event.nbjets >0 and event.nleptons==2 and event.njets > 1 and isSF and ZVeto: 
		if event.HT > 0. and event.MET > 80 and event.mindPhiMetJet12 > 0.25 and event.MET/sqrt(event.HT) > 5 and event.nbjets >0 and event.nleptons==2 and event.njets > 1 and isOF: 

			if event.isMC: 
				plot.Fill( event.MET, event.xsecWeight*lumi)
			else:
				plot.Fill( event.MET)



#	print event.xsecWeight*lumi
#	print plot.GetEntries()
	print plot.Integral()



c1 = ROOT.TCanvas("c1","example",650,700)
pad1 = ROOT.TPad("pad1","pad1",0,0.29,1,0.97)
pad1.SetBottomMargin(0)
pad1.Draw()
pad1.cd()
plot.GetXaxis().SetLabelSize(0.)
plot.SetMaximum(2*plot.GetMaximum())
plot.SetMinimum(10**-1.5)
plot.Draw()
plot.GetXaxis().SetTitle("Title")
plot.GetYaxis().SetTitle("Events")
c1.SetLogy()
pad1.RedrawAxis()
c1.cd()
l1 = ROOT.TLatex()
l1.SetTextAlign(12)
l1.SetTextSize(0.043)
l1.SetNDC()
l1.DrawLatex(0.18, 0.98, "CMS preliminary, L = 0.2 fb^{-1}")
l1.DrawLatex(0.7, 0.98, "#sqrt{s} = 13 TeV")

h_plot = plot.Clone();
pad2 = ROOT.TPad("pad2","pad2",0,0.07,1,0.26)
xmax = h_plot.GetXaxis().GetXmax()
xmin = h_plot.GetXaxis().GetXmin()
line = ROOT.TLine(xmin,1.,xmax,1.)
pad2.SetTopMargin(0)
pad2.Draw()
pad2.cd()
pad2.SetGrid()
h_plot.Sumw2()
h_plot.GetYaxis().SetRangeUser(0., 2.)
h_plot.GetYaxis().SetNdivisions(4)
h_plot.GetXaxis().SetTitleSize(0.23)
h_plot.GetXaxis().SetLabelSize(0.20)
h_plot.GetYaxis().SetLabelSize(0.20)
h_plot.GetYaxis().SetTitleSize(0.20)
h_plot.GetYaxis().SetTitleOffset(0.4)
h_plot.GetXaxis().SetTitleOffset(0.9)
h_plot.GetYaxis().SetTitle("Data / MC")
h_plot.SetMarkerColor(ROOT.kBlack)
h_plot.SetMarkerStyle(20)
h_plot.SetMarkerSize(1.1)
h_plot.Sumw2()
h_plot.Divide(h_plot)
line.SetLineWidth(2)
line.SetLineColor(ROOT.kRed)
h_plot.Draw("ep")
line.Draw("same")
h_plot.Draw("epsame")
pad2.RedrawAxis()

c1.cd()
c1.Print("~/www/php-plots/2LeptonStops13TeV/dataMC/test.png")
