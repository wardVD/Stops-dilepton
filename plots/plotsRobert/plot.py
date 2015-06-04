import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()

from math import *
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()

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
  'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'mt2ll', 'binning': [25,25,275], 'histo':{}},
  'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'mt2bb', 'binning': [22,25,575], 'histo':{}},
  'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'mt2blbl', 'binning': [22,25,575], 'histo':{}},
  'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2})', 'name':'kinMetSig', 'binning': [25,0,25], 'histo':{}},
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
    mt2Calc.reset()
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
        mt2Calc.setMet(met,metPhi)
        mt2Calc.setLeptons(l0pt, l0eta, l0phi, l1pt, l1eta, l1phi)
        
        mt2ll = mt2Calc.mt2ll()
        plots['mt2ll']['histo'][s["name"]].Fill(mt2ll, weight)
        jets = filter(lambda j:j['pt']>30 and abs(j['eta'])<2.4 and j['id'], getJets(chain))
        ht = sum([j['pt'] for j in jets])
        plots['kinMetSig']['histo'][s["name"]].Fill(met/sqrt(ht), weight)
        bjets = filter(lambda j:j['btagCSV']>0.814, jets)
        if len(bjets)==2:
          mt2Calc.setBJets(bjets[0]['pt'], bjets[0]['eta'], bjets[0]['phi'], bjets[1]['pt'], bjets[1]['eta'], bjets[1]['phi'])
          mt2bb   = mt2Calc.mt2bb()
          mt2blbl = mt2Calc.mt2blbl()
          plots['mt2bb']['histo'][s["name"]].Fill(mt2bb, weight)
          plots['mt2blbl']['histo'][s["name"]].Fill(mt2blbl, weight)
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
  bkg_stack.GetXaxis().SetTitle(plots[pk]['title'])
  binning = plots[pk]['binning']
  bkg_stack.GetYaxis().SetTitle("Events / %i GeV"%( (binning[2]-binning[1])/binning[0]) )
  c1.SetLogy()
  signalPlot = plots[pk]['histo'][signal].Clone()
  signalPlot.Scale(100)
  signalPlot.Draw("same")
  l.AddEntry(signalPlot, signal+" x 100")
  l.Draw()
  c1.Print(plotDir+"/"+plots[pk]["name"]+".png")
