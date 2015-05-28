import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/useNiceColorPalette.C")
ROOT.setTDRStyle()
if type(ROOT.tdrStyle)!=type(ROOT.gStyle):
  del ROOT.tdrStyle
  ROOT.setTDRStyle()
ROOT.useNiceColorPalette(255)
ROOT.tdrStyle.SetPadRightMargin(0.15)

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
  'mt2_vs_mt2b': {'name':'mt2_vs_mt2b', 'binning': [25,25,275,25,25,275], 'histo':{}},
}

#make plot in each sample: 
for s in backgrounds+signals:
  for pk in plots.keys():
    plots[pk]['histo'][s['name']] = ROOT.TH2F("met_"+s["name"], "met_"+s["name"], *(plots[pk]['binning']))
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
        jets = filter(lambda j:j['pt']>30 and abs(j['eta'])<2.4 and j['id'], getJets(chain))
        bjets = filter(lambda j:j['btagCSV']>0.814, jets)
        if len(bjets)==2:
          mx = met*cos(metPhi) + l0pt*cos(l0phi) + l1pt*cos(l1phi)
          my = met*cos(metPhi) + l0pt*cos(l0phi) + l1pt*cos(l1phi)
          mt  = sqrt(mx**2+my**2)
          mphi= atan2(my,mx)
          mt2b = calcMT2.mt2(mt, mphi, bjets[0]['pt'], bjets[0]['phi'],  bjets[1]['pt'], bjets[1]['phi'])
          plots['mt2_vs_mt2b']['histo'][s["name"]].Fill(mt2, mt2b, weight)
        else:
          print "Preselection and b-jet selection inconsistent"
        
  del eList

#Some coloring

for pk in plots.keys():
  #Make a stack for backgrounds
  for s in [WJetsHTToLNu, TTVH, DY, singleTop, TTJets]+signals:
    c1 = ROOT.TCanvas()
    plots[pk]['histo'][s['name']].Draw("COLZ")
    c1.Print(plotDir+"/"+s['name']+'_'+plots[pk]["name"]+".png")
