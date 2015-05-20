import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/Stops-dilepton/simplePlot/scripts/tdrstyle.C")
ROOT.setTDRStyle()

from math import *

#preselection: MET>50, HT>100, n_bjets>=2
#Once we decided in HT definition and b-tag WP we add those variables to the tuple.
#For now see here for the Sum$ syntax: https://root.cern.ch/root/html/TTree.html#TTree:Draw@2
preselection = 'met_pt>50&&Sum$((Jet_pt)*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))>100&&(Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.814)>=2)'

#load all the samples
from Workspace.OSDLAnalysis.cmgTuplesPostProcessed_PHYS14 import *
backgrounds = [TTJets, WJetsHTToLNu, TTVH, singleTop, DY]#, QCD]
signals = [SMS_T2tt_2J_mStop425_mLSP325, SMS_T2tt_2J_mStop500_mLSP325, SMS_T2tt_2J_mStop650_mLSP325, SMS_T2tt_2J_mStop850_mLSP100]

#get the TChains for each sample
from Workspace.OSDLAnalysis.helpers import getChain
for s in backgrounds+signals:
  s['chain'] = getChain(s,histname="")

#make MET plot in each sample: 
from Workspace.OSDLAnalysis.helpers import getEList, getVarValue
metPlots={}
for s in backgrounds+signals:
  metPlots[s["name"]] = ROOT.TH1F("met_"+s["name"], "met_"+s["name"], 100,0,500)
  #Using Draw command
  print "Obtain MET plot from %s" % s["name"]
  s["chain"].Draw("met_pt>>met_"+s["name"], "weight*("+preselection+")","goff")
#  #Using Event loop
#  #get EList after preselection
#  print "Obtain MET plot from %s" % s["name"]
#  eList = getEList(s["chain"], preselection) 
#  print "Found %i events in %s after preselection %s" % (eList.GetN(),s["name"],preselection)
#  for ev in range(eList.GetN()):
#    if ev%1000==0:print "At %i/%i"%(ev,eList.GetN())
#    s["chain"].GetEntry(eList.GetEntry(ev))
#    met = getVarValue(s["chain"], "met_pt")
#    weight = getVarValue(s["chain"], "weight")
#    metPlots[s["name"]].Fill(met, weight)

#Some coloring
TTJets["color"]=ROOT.kRed
WJetsHTToLNu["color"]=ROOT.kGreen
TTVH["color"]=ROOT.kMagenta
singleTop["color"]=ROOT.kOrange
DY["color"]=ROOT.kBlue

#Make a stack for backgrounds
l=ROOT.TLegend(0.6,0.6,1.0,1.0)
bkg_stack = ROOT.THStack("bkgs","bkgs")
for b in [WJetsHTToLNu, TTVH, singleTop, TTJets, DY]:
  metPlots[b["name"]].SetFillColor(b["color"])
  bkg_stack.Add(metPlots[b["name"]],"h")
  l.Add(metPlots[b["name"]], b["name"])

#Plot!
signal = "SMS_T2tt_2J_mStop425_mLSP325"#May chose different signal here
c1 = ROOT.TCanvas()
bkg_stack.Draw()
c1.SetLogy()
metPlots[signal].Draw("same")
l.Add(metPlots[signal], signal)
l.Draw()
c1.Print("/afs/hephy.at/user/r/rschoefbeck/www/etc/plotForWard.png")
