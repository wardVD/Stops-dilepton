import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()

from math import *
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()
from StopsDilepton.tools.helpers import getChain, getObjDict, getEList, getVarValue
from StopsDilepton.tools.objectSelection import getLeptons, looseMuID, looseEleID, getJets, ele_ID_eta
from StopsDilepton.tools.localInfo import *

#preselection: MET>50, HT>100, n_bjets>=2
#Once we decided in HT definition and b-tag WP we add those variables to the tuple.
#For now see here for the Sum$ syntax: https://root.cern.ch/root/html/TTree.html#TTree:Draw@2
preselection = 'met_pt>40&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.814)>0&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>2&&Sum$(LepGood_pt>20)>=2'

reduceStat = 1

#load all the samples
from StopsDilepton.plots.cmgTuplesPostProcessed_PHYS14 import *
backgrounds = [TTJets, WJetsHTToLNu, TTVH, singleTop, DY]#, QCD]
#backgrounds = [TTVH]
signals = [SMS_T2tt_2J_mStop425_mLSP325, SMS_T2tt_2J_mStop500_mLSP325, SMS_T2tt_2J_mStop650_mLSP325, SMS_T2tt_2J_mStop850_mLSP100]

#get the TChains for each sample
for s in backgrounds+signals:
  s['chain'] = getChain(s,histname="")

#binning of plot
#binning = [25,25,275]

#make plot in each sample: 

plots = {\
  'mumu':{\
  'mll': {'title':'M_{ll} (GeV)', 'name':'mll', 'binning': [25,25,275], 'histo':{}},
  'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': [25,0,275], 'histo':{}},
  'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'binning': [25,25,575], 'histo':{}},
  'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'mt2bb', 'binning': [25,0,550], 'histo':{}},
  'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'mt2blbl', 'binning': [25,0,550], 'histo':{}},
  'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2})', 'name':'kinMetSig', 'binning': [25,0,25], 'histo':{}},
  'leadingjetpt': {'title':'leading jet p_{T} (GeV)', 'name':'leadingjetpt', 'binning': [25,25,575], 'histo':{}},
  'subleadingjetpt': {'title':'subleading jet p_{T} (GeV)', 'name':'subleadingjetpt', 'binning': [25,25,575], 'histo':{}},
  },
  'elel':{\
  'mll': {'title':'M_{ll} (GeV)', 'name':'mll', 'binning': [25,25,275], 'histo':{}},
  'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': [25,0,275], 'histo':{}},
  'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'binning': [25,25,575], 'histo':{}},
  'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'mt2bb', 'binning': [25,0,550], 'histo':{}},
  'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'mt2blbl', 'binning': [25,0,550], 'histo':{}},
  'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2})', 'name':'kinMetSig', 'binning': [25,0,25], 'histo':{}},
  'leadingjetpt': {'title':'leading jet p_{T} (GeV)', 'name':'leadingjetpt', 'binning': [25,25,575], 'histo':{}},
  'subleadingjetpt': {'title':'subleading jet p_{T} (GeV)', 'name':'subleadingjetpt', 'binning': [25,25,575], 'histo':{}},
  },
  'elmu':{\
  'mll': {'title':'M_{ll} (GeV)', 'name':'mll', 'binning': [25,25,275], 'histo':{}},
  'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': [25,0,275], 'histo':{}},
  'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'binning': [25,25,575], 'histo':{}},
  'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'mt2bb', 'binning': [25,0,550], 'histo':{}},
  'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'mt2blbl', 'binning': [25,0,550], 'histo':{}},
  'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2})', 'name':'kinMetSig', 'binning': [25,0,25], 'histo':{}},
  'leadingjetpt': {'title':'leading jet p_{T} (GeV)', 'name':'leadingjetpt', 'binning': [25,25,575], 'histo':{}},
  'subleadingjetpt': {'title':'subleading jet p_{T} (GeV)', 'name':'subleadingjetpt', 'binning': [25,25,575], 'histo':{}},
  },
}

#adding SF
plotsSF = {\
  'SF':{\
  'mll': {'title':'M_{ll} (GeV)', 'name':'mll', 'binning': [25,25,275], 'histo':{}},
  'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': [25,0,275], 'histo':{}},
  'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'binning': [25,25,575], 'histo':{}},
  'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'mt2bb', 'binning': [25,0,550], 'histo':{}},
  'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'mt2blbl', 'binning': [25,0,550], 'histo':{}},
  'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2})', 'name':'kinMetSig', 'binning': [25,0,25], 'histo':{}},
  'leadingjetpt': {'title':'leading jet p_{T} (GeV)', 'name':'leadingjetpt', 'binning': [25,25,575], 'histo':{}},
  'subleadingjetpt': {'title':'subleading jet p_{T} (GeV)', 'name':'subleadingjetpt', 'binning': [25,25,575], 'histo':{}},
  },
}

for s in backgrounds+signals:
  for pk in plots.keys():
    for plot in plots[pk].keys():
      plots[pk][plot]['histo'][s["name"]] = ROOT.TH1F(plots[pk][plot]['name']+"_"+s["name"]+"_"+pk, plots[pk][plot]['name']+"_"+s["name"]+"_"+pk, *plots[pk][plot]['binning'])
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
    #jetpt
    leadingjetpt = getVarValue(chain, "Jet_pt",0)
    subleadingjetpt = getVarValue(chain, "Jet_pt",1)
    #Leptons 
    allLeptons = getLeptons(chain) 
    muons = filter(looseMuID, allLeptons)    
    electrons = filter(looseEleID, allLeptons)

    leptons = {\
      'mu':   {'name': 'mumu', 'file': muons},
      'el':   {'name': 'elel', 'file': electrons},
      'elmu': {'name': 'elmu', 'file': [electrons,muons]},
      }
    for lep in leptons.keys():
      twoleptons = False
      #Same Flavor
      if lep != 'elmu':
        if len(leptons[lep]['file'])==2 and leptons[lep]['file'][0]['pdgId']*leptons[lep]['file'][1]['pdgId']<0:
          twoleptons = True
          l0pt, l0eta, l0phi = leptons[lep]['file'][0]['pt'],  leptons[lep]['file'][0]['eta'],  leptons[lep]['file'][0]['phi']
          l1pt, l1eta, l1phi = leptons[lep]['file'][1]['pt'],  leptons[lep]['file'][1]['eta'],  leptons[lep]['file'][1]['phi']
          mll = sqrt(2.*l0pt*l1pt*(cosh(l0eta-l1eta)-cos(l0phi-l1phi)))
          plots[leptons[lep]['name']]['mll']['histo'][s["name"]].Fill(mll,weight) #mll as n-1 plot without Z-mass cut
      #Opposite Flavor
      if lep == 'elmu':
        if len(leptons[lep]['file'][0])==1 and len(leptons[lep]['file'][1])==1 and leptons[lep]['file'][0][0]['pdgId']*leptons[lep]['file'][1][0]['pdgId']<0:
          twoleptons = True
          l0pt, l0eta, l0phi = leptons[lep]['file'][0][0]['pt'],  leptons[lep]['file'][0][0]['eta'],  leptons[lep]['file'][0][0]['phi']
          l1pt, l1eta, l1phi = leptons[lep]['file'][1][0]['pt'],  leptons[lep]['file'][1][0]['eta'],  leptons[lep]['file'][1][0]['phi']
          mll = sqrt(2.*l0pt*l1pt*(cosh(l0eta-l1eta)-cos(l0phi-l1phi)))
          plots[leptons[lep]['name']]['mll']['histo'][s["name"]].Fill(mll,weight) #mll as n-1 plot without Z-mass cut
      if twoleptons and mll>20 and abs(mll-90.2)>15:
        plots[leptons[lep]['name']]['leadingjetpt']['histo'][s["name"]].Fill(leadingjetpt, weight)
        plots[leptons[lep]['name']]['subleadingjetpt']['histo'][s["name"]].Fill(subleadingjetpt, weight)
        mt2Calc.setMet(met,metPhi)
        mt2Calc.setLeptons(l0pt, l0eta, l0phi, l1pt, l1eta, l1phi)
        
        mt2ll = mt2Calc.mt2ll()
        plots[leptons[lep]['name']]['mt2ll']['histo'][s["name"]].Fill(mt2ll, weight)
        jets = filter(lambda j:j['pt']>30 and abs(j['eta'])<2.4 and j['id'], getJets(chain))
        ht = sum([j['pt'] for j in jets])
        plots[leptons[lep]['name']]['kinMetSig']['histo'][s["name"]].Fill(met/sqrt(ht), weight)
        plots[leptons[lep]['name']]['met']['histo'][s["name"]].Fill(met, weight)
        bjets = filter(lambda j:j['btagCSV']>0.814, jets)
        if len(bjets)==2:
          mt2Calc.setBJets(bjets[0]['pt'], bjets[0]['eta'], bjets[0]['phi'], bjets[1]['pt'], bjets[1]['eta'], bjets[1]['phi'])
          mt2bb   = mt2Calc.mt2bb()
          mt2blbl = mt2Calc.mt2blbl()
          plots[leptons[lep]['name']]['mt2bb']['histo'][s["name"]].Fill(mt2bb, weight)
          plots[leptons[lep]['name']]['mt2blbl']['histo'][s["name"]].Fill(mt2blbl, weight)
          #else:
          #  print "Preselection and b-jet selection inconsistent"
  del eList


#Some coloring
TTJets["color"]=ROOT.kRed
WJetsHTToLNu["color"]=ROOT.kGreen
TTVH["color"]=ROOT.kMagenta
singleTop["color"]=ROOT.kOrange
DY["color"]=ROOT.kBlue


for pk in plots.keys():
  for plot in plots[pk].keys():
#Make a stack for backgrounds
    l=ROOT.TLegend(0.6,0.6,1.0,1.0)
    l.SetFillColor(0)
    l.SetShadowColor(ROOT.kWhite)
    l.SetBorderSize(1)
    l.SetTextSize(0.03)
    bkg_stack = ROOT.THStack("bkgs","bkgs")
    for b in [WJetsHTToLNu, TTVH, DY, singleTop, TTJets]:
    #for b in [TTVH]:
      plots[pk][plot]['histo'][b["name"]].SetFillColor(b["color"])
      plots[pk][plot]['histo'][b["name"]].SetMarkerColor(b["color"])
      plots[pk][plot]['histo'][b["name"]].SetMarkerSize(0)
      bkg_stack.Add(plots[pk][plot]['histo'][b["name"]],"h")
      l.AddEntry(plots[pk][plot]['histo'][b["name"]], b["name"])
    
    #Plot!
    signal = {'path': "SMS_T2tt_2J_mStop650_mLSP325", 'name': "T2tt (St: 650, LSP: 325)"} #May chose different signal here
    c1 = ROOT.TCanvas()
    bkg_stack.SetMaximum(2*bkg_stack.GetMaximum())
    bkg_stack.SetMinimum(10**-1.5)
    bkg_stack.Draw()
    bkg_stack.GetXaxis().SetTitle(plots[pk][plot]['title'])
    bkg_stack.GetYaxis().SetTitle("Events / %i GeV"%( (plots[pk][plot]['binning'][2]-plots[pk][plot]['binning'][1])/plots[pk][plot]['binning'][0]) )
    c1.SetLogy()
    signalPlot = plots[pk][plot]['histo'][signal['path']].Clone()
    signalPlot.Scale(100)
    signalPlot.Draw("same")
    l.AddEntry(signalPlot, signal['name']+" x 100")
    l.Draw()
    if (pk == 'mumu'):
      c1.Print(plotDir+"/"+plots[pk][plot]['name']+"_mumu.png")
    if (pk =='elel'):
      c1.Print(plotDir+"/"+plots[pk][plot]['name']+"_elel.png")
    if (pk =='elmu'):
      c1.Print(plotDir+"/"+plots[pk][plot]['name']+"_elmu.png")


for plot in plotsSF['SF'].keys():
  bkg_stack_SF = ROOT.THStack("bkgs_SF","bkgs_SF")
  l=ROOT.TLegend(0.6,0.6,1.0,1.0)
  l.SetFillColor(0)
  l.SetShadowColor(ROOT.kWhite)
  l.SetBorderSize(1)
  l.SetTextSize(0.03)
  for b in [WJetsHTToLNu, TTVH, DY, singleTop, TTJets]:
  #for b in [TTVH]:
    bkgforstack = plots['elel'][plot]['histo'][b["name"]]
    bkgforstack.Add(plots['mumu'][plot]['histo'][b["name"]])
    bkg_stack_SF.Add(bkgforstack,"h")
    l.AddEntry(plots['elel'][plot]['histo'][b["name"]], b["name"])
  
  signal = {'path': "SMS_T2tt_2J_mStop650_mLSP325", 'name': "T2tt (St: 650, LSP: 325)"} #May chose different signal here
  c1 = ROOT.TCanvas()
  bkg_stack_SF.SetMaximum(2*bkg_stack.GetMaximum())
  bkg_stack_SF.SetMinimum(10**-1.5)
  bkg_stack_SF.Draw()
  bkg_stack_SF.GetXaxis().SetTitle(plotsSF['SF'][plot]['title'])
  bkg_stack_SF.GetYaxis().SetTitle("Events / %i GeV"%( (plotsSF['SF'][plot]['binning'][2]-plotsSF['SF'][plot]['binning'][1])/plotsSF['SF'][plot]['binning'][0]) )
  c1.SetLogy()
  signalPlot = plots['elel'][plot]['histo'][signal['path']].Clone()
  signalPlot.Add(plots['mumu'][plot]['histo'][signal['path']])
  signalPlot.Scale(100)
  signalPlot.Draw("same")
  l.AddEntry(signalPlot, signal['name']+" x 100")
  l.Draw()
  c1.Print(plotDir+"/"+plotsSF['SF'][plot]['name']+"_SF.png")
    
