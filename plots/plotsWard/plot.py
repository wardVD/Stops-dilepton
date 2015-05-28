import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()

from math import *
from StopsDilepton.tools import mt2 as calcMT2
from StopsDilepton.tools.helpers import getChain, getObjDict, getEList, getVarValue
from StopsDilepton.tools.objectSelection import getLeptons, looseMuID 
from StopsDilepton.tools.localInfo import *

#preselection: MET>50, HT>100, n_bjets>=2
#Once we decided in HT definition and b-tag WP we add those variables to the tuple.
#For now see here for the Sum$ syntax: https://root.cern.ch/root/html/TTree.html#TTree:Draw@2
preselection = 'met_pt>40&&Sum$((Jet_pt)*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))>100&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.814)>=1&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2&&Sum$(LepGood_pt>15)>=2'

reduceStat = 1

#load all the samples
from StopsDilepton.plots.cmgTuplesPostProcessed_PHYS14 import *
backgrounds = [TTJets, WJetsHTToLNu, TTVH, singleTop, DY]#, QCD]
signals = [SMS_T2tt_2J_mStop425_mLSP325, SMS_T2tt_2J_mStop500_mLSP325, SMS_T2tt_2J_mStop650_mLSP325, SMS_T2tt_2J_mStop850_mLSP100]

#get the TChains for each sample
for s in backgrounds+signals:
  s['chain'] = getChain(s,histname="")

#binning of plot
binning = [25,25,275]

#make plot in each sample: 
mt2Plots={}
for s in backgrounds+signals:
  mt2Plots[s["name"]] = ROOT.TH1F("met_"+s["name"], "met_"+s["name"], *binning)
  chain = s["chain"]
#  #Using Draw command
#  print "Obtain MET plot from %s" % s["name"]
#  chain.Draw("met_pt>>met_"+s["name"], "weight*("+preselection+")","goff")
  #Using Event loop
  #get EList after preselection
  print "Looping over %s" % s["name"]
  eList = getEList(chain, preselection) 
  nEvents = eList.GetN()/reduceStat
  print "Found %i events in %s after preselection %s, looping over %i" % (eList.GetN(),s["name"],preselection,nEvents)
  for ev in range(nEvents):
    if ev%10000==0:print "At %i/%i"%(ev,nEvents)
    chain.GetEntry(eList.GetEntry(ev))
    #event weight (L= 4fb^-1)
    weight = reduceStat*getVarValue(chain, "weight")
    #MET
    met = getVarValue(chain, "met_pt")
    metPhi = getVarValue(chain, "met_phi")
    #Leptons 
    leptons = getLeptons(chain) 
    muons = filter(looseMuID, leptons)    
    if len(muons)==2 and muons[0]['pdgId']*muons[1]['pdgId']<0:
      l0pt, l0eta, l0phi = muons[0]['pt'],  muons[0]['eta'],  muons[0]['phi']
      l1pt, l1eta, l1phi = muons[1]['pt'],  muons[1]['eta'],  muons[1]['phi']
      mll = sqrt(2.*l0pt*l1pt*(cosh(l0eta-l1eta)-cos(l0phi-l1phi)))
      if mll>20 and abs(mll-90.2)>15:
        mt2 = calcMT2.mt2(met, metPhi, l0pt, l0phi, l1pt, l1phi)
        mt2Plots[s["name"]].Fill(mt2, weight)
  del eList

#Some coloring
TTJets["color"]=ROOT.kRed
WJetsHTToLNu["color"]=ROOT.kGreen
TTVH["color"]=ROOT.kMagenta
singleTop["color"]=ROOT.kOrange
DY["color"]=ROOT.kBlue

#Make a stack for backgrounds
l=ROOT.TLegend(0.6,0.6,1.0,1.0)
l.SetFillColor(0)
l.SetShadowColor(ROOT.kWhite)
l.SetBorderSize(1)
bkg_stack = ROOT.THStack("bkgs","bkgs")
for b in [WJetsHTToLNu, TTVH, DY, singleTop, TTJets]:
  mt2Plots[b["name"]].SetFillColor(b["color"])
  mt2Plots[b["name"]].SetMarkerColor(b["color"])
  mt2Plots[b["name"]].SetMarkerSize(0)
  bkg_stack.Add(mt2Plots[b["name"]],"h")
  l.AddEntry(mt2Plots[b["name"]], b["name"])

#Plot!
signal = "SMS_T2tt_2J_mStop650_mLSP325"#May chose different signal here
c1 = ROOT.TCanvas()
bkg_stack.Draw()
#bkg_stack.GetXaxis().SetTitle('#slash{E}_{T} (GeV)')
bkg_stack.GetXaxis().SetTitle('M_{T,2} (GeV)')
bkg_stack.GetYaxis().SetTitle("Events / %i GeV"%( (binning[2]-binning[1])/binning[0]) )
c1.SetLogy()
signalPlot = mt2Plots[signal].Clone()
signalPlot.Scale(100)
signalPlot.Draw("same")
l.AddEntry(signalPlot, signal+" x 100")
l.Draw()
c1.Print(plotDir+"/mt2.png")

