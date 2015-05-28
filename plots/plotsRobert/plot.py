import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()

from math import *
from StopsDilepton.tools import mt2 as calcMT2
from StopsDilepton.tools.helpers import getChain, getObjDict, getEList, getVarValue
from StopsDilepton.tools.objectSelection import getLeptons, looseMuID, getJets 
from StopsDilepton.tools.localInfo import *

#preselection: MET>50, HT>100, n_bjets>=2
#Once we decided in HT definition and b-tag WP we add those variables to the tuple.
#For now see here for the Sum$ syntax: https://root.cern.ch/root/html/TTree.html#TTree:Draw@2
preselection = 'met_pt>40&&Sum$((Jet_pt)*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))>100&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.814)==2&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2&&Sum$(LepGood_pt>15)>=2'

reduceStat = 1

#load all the samples
from StopsDilepton.plots.cmgTuplesPostProcessed_PHYS14 import *
backgrounds = [TTJets, WJetsHTToLNu, TTVH, singleTop, DY]#, QCD]
signals = [SMS_T2tt_2J_mStop425_mLSP325, SMS_T2tt_2J_mStop500_mLSP325, SMS_T2tt_2J_mStop650_mLSP325, SMS_T2tt_2J_mStop850_mLSP100]

#get the TChains for each sample
for s in backgrounds+signals:
  s['chain'] = getChain(s,histname="")

#plots
plots = {\
  'mt2': {'name':'mt2', 'binning': [25,25,275], 'histo':{}},
  'mt2b':{'name':'mt2b', 'binning': [25,25,275], 'histo':{}},
}

#make plot in each sample: 
for s in backgrounds+signals:
  for pk in plots.keys():
    plots[pk]['histo'][s['name']] = ROOT.TH1F("met_"+s["name"], "met_"+s["name"], *(plots[pk]['binning']))
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
        plots['mt2']['histo'][s["name"]].Fill(mt2, weight)
        jets = filter(lambda j:j['pt']>30 and abs(j['eta'])<2.4 and j['id'], getJets(chain))
        bjets = filter(lambda j:j['btagCSV']>0.814, jets)
        if len(bjets)==2:
          mx = met*cos(metPhi) + l0pt*cos(l0phi) + l1pt*cos(l1phi)
          my = met*cos(metPhi) + l0pt*cos(l0phi) + l1pt*cos(l1phi)
          mt  = sqrt(mx**2+my**2)
          mphi= atan2(my,mx)
          mt2b = calcMT2.mt2(mt, mphi, bjets[0]['pt'], bjets[0]['phi'],  bjets[1]['pt'], bjets[1]['phi'])
          plots['mt2b']['histo'][s["name"]].Fill(mt2b, weight)
        else:
          print "Preselection and b-jet selection inconsistent"
        
  del eList

#Some coloring
TTJets["color"]=ROOT.kRed
WJetsHTToLNu["color"]=ROOT.kGreen
TTVH["color"]=ROOT.kMagenta
singleTop["color"]=ROOT.kOrange
DY["color"]=ROOT.kBlue

for pk in plots.keys():
  #Make a stack for backgrounds
  l=ROOT.TLegend(0.6,0.6,1.0,1.0)
  l.SetFillColor(0)
  l.SetShadowColor(ROOT.kWhite)
  l.SetBorderSize(1)
  bkg_stack = ROOT.THStack("bkgs","bkgs")
  for b in [WJetsHTToLNu, TTVH, DY, singleTop, TTJets]:
    plots[pk]['histo'][b['name']].SetFillColor(b["color"])
    plots[pk]['histo'][b['name']].SetMarkerColor(b["color"])
    plots[pk]['histo'][b['name']].SetMarkerSize(0)
    bkg_stack.Add(plots[pk]['histo'][b['name']],"h")
    l.AddEntry(plots[pk]['histo'][b['name']], b["name"])
  #Plot!
  signal = "SMS_T2tt_2J_mStop650_mLSP325"#May chose different signal here
  c1 = ROOT.TCanvas()
  bkg_stack.Draw()
  #bkg_stack.GetXaxis().SetTitle('#slash{E}_{T} (GeV)')
  bkg_stack.GetXaxis().SetTitle('M_{T,2} (GeV)')
  binning = plots[pk]['binning']
  bkg_stack.GetYaxis().SetTitle("Events / %i GeV"%( (binning[2]-binning[1])/binning[0]) )
  c1.SetLogy()
  signalPlot = plots[pk]['histo'][signal].Clone()
  signalPlot.Scale(100)
  signalPlot.Draw("same")
  l.AddEntry(signalPlot, signal+" x 100")
  l.Draw()
  c1.Print(plotDir+"/"+plots[pk]["name"]+".png")
