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
 
#binning
mllbinning = [25,25,275] 
mt2llbinning = [25,0,275]
metbinning = [25,25,575]
mt2bbbinning = [25,0,550]
mt2blblbinning = [25,0,550]
kinMetSigbinning = [25,0,25]
leadingjetptbinning = [25,25,575]
subleadingjetptbinning = [25,25,575]

#make plot in each sample:
plots = {\
  'mumu':{\
  'mll': {'title':'M_{ll} (GeV)', 'name':'mll', 'binning': mllbinning, 'histo':{}},
  'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
  'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'binning': metbinning, 'histo':{}},
  'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'mt2bb', 'binning': mt2bbbinning, 'histo':{}},
  'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'mt2blbl', 'binning': mt2blblbinning, 'histo':{}},
  'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2})', 'name':'kinMetSig', 'binning': kinMetSigbinning, 'histo':{}},
  'leadingjetpt': {'title':'leading jet p_{T} (GeV)', 'name':'leadingjetpt', 'binning': leadingjetptbinning, 'histo':{}},
  'subleadingjetpt': {'title':'subleading jet p_{T} (GeV)', 'name':'subleadingjetpt', 'binning': subleadingjetptbinning, 'histo':{}},
  },
  'ee':{\
  'mll': {'title':'M_{ll} (GeV)', 'name':'mll', 'binning': mllbinning, 'histo':{}},
  'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
  'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'binning': metbinning, 'histo':{}},
  'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'mt2bb', 'binning': mt2bbbinning, 'histo':{}},
  'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'mt2blbl', 'binning': mt2blblbinning, 'histo':{}},
  'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2})', 'name':'kinMetSig', 'binning': kinMetSigbinning, 'histo':{}},
  'leadingjetpt': {'title':'leading jet p_{T} (GeV)', 'name':'leadingjetpt', 'binning': leadingjetptbinning, 'histo':{}},
  'subleadingjetpt': {'title':'subleading jet p_{T} (GeV)', 'name':'subleadingjetpt', 'binning': subleadingjetptbinning, 'histo':{}},
  },
  'emu':{\
  'mll': {'title':'M_{ll} (GeV)', 'name':'mll', 'binning': mllbinning, 'histo':{}},
  'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
  'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'binning': metbinning, 'histo':{}},
  'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'mt2bb', 'binning': mt2bbbinning, 'histo':{}},
  'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'mt2blbl', 'binning': mt2blblbinning, 'histo':{}},
  'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2})', 'name':'kinMetSig', 'binning': kinMetSigbinning, 'histo':{}},
  'leadingjetpt': {'title':'leading jet p_{T} (GeV)', 'name':'leadingjetpt', 'binning': leadingjetptbinning, 'histo':{}},
  'subleadingjetpt': {'title':'subleading jet p_{T} (GeV)', 'name':'subleadingjetpt', 'binning': subleadingjetptbinning, 'histo':{}},
  },
}

#adding SF
plotsSF = {\
  'SF':{\
  'mll': {'title':'M_{ll} (GeV)', 'name':'mll', 'binning': mllbinning, 'histo':{}},
  'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
  'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'binning': metbinning, 'histo':{}},
  'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'mt2bb', 'binning': mt2bbbinning, 'histo':{}},
  'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'mt2blbl', 'binning': mt2blblbinning, 'histo':{}},
  'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2})', 'name':'kinMetSig', 'binning': kinMetSigbinning, 'histo':{}},
  'leadingjetpt': {'title':'leading jet p_{T} (GeV)', 'name':'leadingjetpt', 'binning': leadingjetptbinning, 'histo':{}},
  'subleadingjetpt': {'title':'subleading jet p_{T} (GeV)', 'name':'subleadingjetpt', 'binning': subleadingjetptbinning, 'histo':{}},
  },
}

for s in backgrounds+signals:
  for pk in plots.keys():
    for plot in plots[pk].keys():
      plots[pk][plot]['histo'][s["name"]] = ROOT.TH1F(plots[pk][plot]['name']+"_"+s["name"]+"_"+pk, plots[pk][plot]['name']+"_"+s["name"]+"_"+pk, *plots[pk][plot]['binning'])
  chain = s["chain"]
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
    #jetpt
    leadingjetpt = getVarValue(chain, "Jet_pt",0)
    subleadingjetpt = getVarValue(chain, "Jet_pt",1)
    #Leptons 
    allLeptons = getLeptons(chain) 
    muons = filter(looseMuID, allLeptons)    
    electrons = filter(looseEleID, allLeptons)

    leptons = {\
      'mu':   {'name': 'mumu', 'file': muons},
      'e':   {'name': 'ee', 'file': electrons},
      'emu': {'name': 'emu', 'file': [electrons,muons]},
      }
    for lep in leptons.keys():
      twoleptons = False
      #Same Flavor
      if lep != 'emu':
        if len(leptons[lep]['file'])==2 and leptons[lep]['file'][0]['pdgId']*leptons[lep]['file'][1]['pdgId']<0:
          twoleptons = True
          l0pt, l0eta, l0phi = leptons[lep]['file'][0]['pt'],  leptons[lep]['file'][0]['eta'],  leptons[lep]['file'][0]['phi']
          l1pt, l1eta, l1phi = leptons[lep]['file'][1]['pt'],  leptons[lep]['file'][1]['eta'],  leptons[lep]['file'][1]['phi']
          mll = sqrt(2.*l0pt*l1pt*(cosh(l0eta-l1eta)-cos(l0phi-l1phi)))
          plots[leptons[lep]['name']]['mll']['histo'][s["name"]].Fill(mll,weight) #mll as n-1 plot without Z-mass cut
          zveto = True
      #Opposite Flavor
      if lep == 'emu':
        if len(leptons[lep]['file'][0])==1 and len(leptons[lep]['file'][1])==1 and leptons[lep]['file'][0][0]['pdgId']*leptons[lep]['file'][1][0]['pdgId']<0:
          twoleptons = True
          l0pt, l0eta, l0phi = leptons[lep]['file'][0][0]['pt'],  leptons[lep]['file'][0][0]['eta'],  leptons[lep]['file'][0][0]['phi']
          l1pt, l1eta, l1phi = leptons[lep]['file'][1][0]['pt'],  leptons[lep]['file'][1][0]['eta'],  leptons[lep]['file'][1][0]['phi']
          mll = sqrt(2.*l0pt*l1pt*(cosh(l0eta-l1eta)-cos(l0phi-l1phi)))
          plots[leptons[lep]['name']]['mll']['histo'][s["name"]].Fill(mll,weight) #mll as n-1 plot without Z-mass cut
          zveto = False
      if (twoleptons and mll>20 and not zveto) or (twoleptons and mll > 20 and zveto and abs(mll-90.2)>15):
        plots[leptons[lep]['name']]['leadingjetpt']['histo'][s["name"]].Fill(leadingjetpt, weight)
        plots[leptons[lep]['name']]['subleadingjetpt']['histo'][s["name"]].Fill(subleadingjetpt, weight)
        mt2Calc.setMet(met,metPhi)
        mt2Calc.setLeptons(l0pt, l0eta, l0phi, l1pt, l1eta, l1phi)
        
        mt2ll = mt2Calc.mt2ll()
        plots[leptons[lep]['name']]['mt2ll']['histo'][s["name"]].Fill(mt2ll, weight)
        jets = filter(lambda j:j['pt']>30 and abs(j['eta'])<2.4 and j['id'], getJets(chain))
        ht = sum([j['pt'] for j in jets])
        #if mt2ll > 120:
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

#Plotvariables
signal = {'path': ["SMS_T2tt_2J_mStop425_mLSP325","SMS_T2tt_2J_mStop650_mLSP325"], 'name': ["T2tt(425,325)","T2tt(650,325)"]} #May chose different signal here
yminimum = 10**-1.5
legendtextsize = 0.032
signalscaling = 100

for pk in plots.keys():
  for plot in plots[pk].keys():
#Make a stack for backgrounds
    l=ROOT.TLegend(0.6,0.6,1.0,1.0)
    l.SetFillColor(0)
    l.SetShadowColor(ROOT.kWhite)
    l.SetBorderSize(1)
    l.SetTextSize(legendtextsize)
    bkg_stack = ROOT.THStack("bkgs","bkgs")
    for b in [WJetsHTToLNu, TTVH, DY, singleTop, TTJets]:
    #for b in [TTVH]:
      plots[pk][plot]['histo'][b["name"]].SetFillColor(b["color"])
      plots[pk][plot]['histo'][b["name"]].SetMarkerColor(b["color"])
      plots[pk][plot]['histo'][b["name"]].SetMarkerSize(0)
      bkg_stack.Add(plots[pk][plot]['histo'][b["name"]],"h")
      l.AddEntry(plots[pk][plot]['histo'][b["name"]], b["name"])
    
    #Plot!
    c1 = ROOT.TCanvas()
    bkg_stack.SetMaximum(2*bkg_stack.GetMaximum())
    bkg_stack.SetMinimum(yminimum)
    bkg_stack.Draw()
    bkg_stack.GetXaxis().SetTitle(plots[pk][plot]['title'])
    bkg_stack.GetYaxis().SetTitle("Events / %i GeV"%( (plots[pk][plot]['binning'][2]-plots[pk][plot]['binning'][1])/plots[pk][plot]['binning'][0]) )
    c1.SetLogy()
    signalPlot_1 = plots[pk][plot]['histo'][signal['path'][0]].Clone()
    signalPlot_2 = plots[pk][plot]['histo'][signal['path'][1]].Clone()
    signalPlot_1.Scale(signalscaling)
    signalPlot_2.Scale(signalscaling)
    signalPlot_1.SetLineColor(ROOT.kBlack)
    signalPlot_2.SetLineColor(ROOT.kCyan)
    signalPlot_1.SetLineWidth(3)
    signalPlot_2.SetLineWidth(3)
    signalPlot_1.Draw("same")
    signalPlot_2.Draw("same")
    l.AddEntry(signalPlot_1, signal['name'][0]+" x " + str(signalscaling), "l")
    l.AddEntry(signalPlot_2, signal['name'][1]+" x " + str(signalscaling), "l")
    l.Draw()
    channeltag = ROOT.TPaveText(0.45,0.8,0.59,0.85,"NDC")
    firstlep, secondlep = pk[:len(pk)/2], pk[len(pk)/2:]
    if firstlep == 'mu':
      firstlep = '#' + firstlep
    if secondlep == 'mu':
      secondlep = '#' + secondlep
    channeltag.AddText(firstlep+secondlep)
    channeltag.SetFillColor(ROOT.kWhite)
    channeltag.SetShadowColor(ROOT.kWhite)
    channeltag.Draw()
    c1.Print(plotDir+"/test/"+plots[pk][plot]['name']+"_"+pk+".png")
    

for plot in plotsSF['SF'].keys():
  bkg_stack_SF = ROOT.THStack("bkgs_SF","bkgs_SF")
  l=ROOT.TLegend(0.6,0.6,1.0,1.0)
  l.SetFillColor(0)
  l.SetShadowColor(ROOT.kWhite)
  l.SetBorderSize(1)
  l.SetTextSize(legendtextsize)
  for b in [WJetsHTToLNu, TTVH, DY, singleTop, TTJets]:
  #for b in [TTVH]:
    bkgforstack = plots['ee'][plot]['histo'][b["name"]]
    bkgforstack.Add(plots['mumu'][plot]['histo'][b["name"]])
    bkg_stack_SF.Add(bkgforstack,"h")
    l.AddEntry(plots['ee'][plot]['histo'][b["name"]], b["name"])
  
  c1 = ROOT.TCanvas()
  bkg_stack_SF.SetMaximum(2*bkg_stack.GetMaximum())
  bkg_stack_SF.SetMinimum(yminimum)
  bkg_stack_SF.Draw()
  bkg_stack_SF.GetXaxis().SetTitle(plotsSF['SF'][plot]['title'])
  bkg_stack_SF.GetYaxis().SetTitle("Events / %i GeV"%( (plotsSF['SF'][plot]['binning'][2]-plotsSF['SF'][plot]['binning'][1])/plotsSF['SF'][plot]['binning'][0]) )
  c1.SetLogy()
  signalPlot_1 = plots['ee'][plot]['histo'][signal['path'][0]].Clone()
  signalPlot_1.Add(plots['mumu'][plot]['histo'][signal['path'][0]])
  signalPlot_2 = plots['ee'][plot]['histo'][signal['path'][1]].Clone()
  signalPlot_2.Add(plots['mumu'][plot]['histo'][signal['path'][1]])
  signalPlot_1.Scale(signalscaling)
  signalPlot_2.Scale(signalscaling)
  signalPlot_1.SetLineColor(ROOT.kBlack)
  signalPlot_2.SetLineColor(ROOT.kCyan)
  signalPlot_1.SetLineWidth(3)
  signalPlot_2.SetLineWidth(3)
  signalPlot_1.Draw("same")
  signalPlot_2.Draw("same")
  l.AddEntry(signalPlot_1, signal['name'][0]+" x " + str(signalscaling), "l")
  l.AddEntry(signalPlot_2, signal['name'][1]+" x " + str(signalscaling), "l")
  l.Draw()
  channeltag = ROOT.TPaveText(0.45,0.8,0.59,0.85,"NDC")
  channeltag.AddText("SF")
  channeltag.SetFillColor(ROOT.kWhite)
  channeltag.SetShadowColor(ROOT.kWhite)
  channeltag.Draw()
  c1.Print(plotDir+"/test/"+plotsSF['SF'][plot]['name']+"_SF.png")
    
