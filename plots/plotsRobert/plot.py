import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()

from math import *
import array

from StopsDilepton.tools.mtautau import mtautau as mtautau_
from StopsDilepton.tools.helpers import getChain, getObjDict, getEList, getVarValue
from StopsDilepton.tools.objectSelection import getLeptons, looseMuID, looseEleID, getJets 
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()
from StopsDilepton.tools.localInfo import *

#preselection: MET>50, HT>100, n_bjets>=2
#Once we decided in HT definition and b-tag WP we add those variables to the tuple.
#For now see here for the Sum$ syntax: https://root.cern.ch/root/html/TTree.html#TTree:Draw@2


preselection = 'Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>2&&Sum$(LepGood_pt>20)>=2'
prefix="def"
#prefix="mt2ll-120"
reduceStat = 100
lumiScale = 42/4000.

#load all the samples
from StopsDilepton.samples.cmgTuples_Spring15_50ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_Spring15_25ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data50ns_1l_postProcessed import *

backgrounds = [diBosons_50ns,WJetsToLNu_50ns,singleTop_50ns,QCDMu_50ns,DYHT_50ns,TTJets_50ns]

for b in backgrounds:
  b['isData']=False

data = [DoubleEG_50ns,DoubleMuon_50ns,MuonEG_50ns]

for d in data:
  d['isData']=True

signals = [SMS_T2tt_2J_mStop425_mLSP325, SMS_T2tt_2J_mStop500_mLSP325, SMS_T2tt_2J_mStop650_mLSP325, SMS_T2tt_2J_mStop850_mLSP100]

for s in signals:
  s['isData']=False


#get the TChains for each sample
for s in backgrounds+signals+data:
  s['chain'] = getChain(s,histname="")

plots = {\
  'met': {'title':'#slash{E}_{T} (GeV)', 'name':'met', 'binning': [26,0,520], 'histo':{}},
  'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'mt2ll', 'binning': [26,0,520], 'histo':{}},
  'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'mt2bb', 'binning': [26,0,520], 'histo':{}},
  'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'mt2blbl', 'binning': [26,0,520], 'histo':{}},
  'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2})', 'name':'kinMetSig', 'binning': [35,0,35], 'histo':{}},
  'mtautau_zoomed': {'title':'M_{#tau#tau} (GeV)', 'name':'mtautau_zoomed', 'binning': [50,0,200], 'histo':{}},
  'mtautau': {'title':'M_{#tau#tau} (GeV)', 'name':'mtautau', 'binning': [50,0,2000], 'histo':{}},
  'alpha0': {'title':'#alpha_{0}', 'name':'alpha0', 'binning': [50,-10,10], 'histo':{}},
  'alpha1': {'title':'#alpha_{1}', 'name':'alpha1', 'binning': [50,-10,10], 'histo':{}},
}


#make plot in each sample: 
for s in backgrounds+signals+data:
  for pk in plots.keys():
    plots[pk]['histo'][s['name']] = ROOT.TH1F("met_"+s["name"], "met_"+s["name"], *(plots[pk]['binning']))

  chain = s["chain"]
  print "Looping over %s" % s["name"]
  eList = getEList(chain, preselection) 
  nEvents = eList.GetN()/reduceStat
  print "Found %i events in %s after preselection %s, looping over %i" % (eList.GetN(),s["name"],preselection,nEvents)
  for ev in range(nEvents):
    if ev%10000==0:print "At %i/%i"%(ev,nEvents)
    chain.GetEntry(eList.GetEntry(ev))
    mt2Calc.reset()
    weight = reduceStat*getVarValue(chain, "weight")*lumiScale if not s['isData'] else 1
    met = getVarValue(chain, "met_pt")
    plots['met']['histo'][s["name"]].Fill(met, weight)
    metPhi = getVarValue(chain, "met_phi")
    leptons = filter(lambda l: looseMuID(l) or looseEleID(l), getLeptons(chain))
    if len(leptons)==2 and leptons[0]['pdgId']*leptons[1]['pdgId']<0 and abs(leptons[0]['pdgId'])==abs(leptons[1]['pdgId']): #OSSF choice
      l0pt, l0eta, l0phi = leptons[0]['pt'],  leptons[0]['eta'],  leptons[0]['phi']
      l1pt, l1eta, l1phi = leptons[1]['pt'],  leptons[1]['eta'],  leptons[1]['phi']
      mll = sqrt(2.*l0pt*l1pt*(cosh(l0eta-l1eta)-cos(l0phi-l1phi)))
      if  mll>20 and abs(mll-90.2)<15:
        jets = filter(lambda j:j['pt']>30 and abs(j['eta'])<2.4 and j['id'], getJets(chain))
        bjets = filter(lambda j:j['btagCSV']>0.890, jets)
        if len(bjets)==2:
          mt2Calc.setMet(met,metPhi)
          mt2Calc.setLeptons(l0pt, l0eta, l0phi, l1pt, l1eta, l1phi)
          mt2ll = mt2Calc.mt2ll()
#          if mt2ll>120:
          if True:
            plots['mt2ll']['histo'][s["name"]].Fill(mt2ll, weight)
            ht = sum([j['pt'] for j in jets])
            plots['kinMetSig']['histo'][s["name"]].Fill(met/sqrt(ht), weight)
            mt2Calc.setBJets(bjets[0]['pt'], bjets[0]['eta'], bjets[0]['phi'], bjets[1]['pt'], bjets[1]['eta'], bjets[1]['phi'])
            mt2bb   = mt2Calc.mt2bb()
            mt2blbl = mt2Calc.mt2blbl()
            plots['mt2bb']['histo'][s["name"]].Fill(mt2bb, weight)
            plots['mt2blbl']['histo'][s["name"]].Fill(mt2blbl, weight)
            mtautau, alpha_0, alpha_1 = mtautau_(met,metPhi, l0pt, l0eta, l0phi, l1pt, l1eta, l1phi, retAll=True)
            plots['mtautau']['histo'][s["name"]].Fill(mtautau, weight)
            plots['mtautau_zoomed']['histo'][s["name"]].Fill(mtautau, weight)
            plots['alpha0']['histo'][s["name"]].Fill(alpha_0, weight)
            plots['alpha1']['histo'][s["name"]].Fill(alpha_1, weight)
#
#        else:
#          print "Preselection and b-jet selection inconsistent"
        
  del eList

#Some coloring
TTJets_50ns["color"]=7
DYHT_50ns["color"]=8
QCDMu_50ns["color"]=46
singleTop_50ns["color"]=40
diBosons_50ns["color"]=42
WJetsToLNu_50ns['color']=40


signal = {'path': ["SMS_T2tt_2J_mStop425_mLSP325","SMS_T2tt_2J_mStop500_mLSP325","SMS_T2tt_2J_mStop650_mLSP325","SMS_T2tt_2J_mStop850_mLSP100"], 
		  'name': ["T2tt(425,325)","T2tt(500,325)","T2tt(650,325)","T2tt(850,100)"]}

for pk in plots.keys():
  #Make a stack for backgrounds
  l=ROOT.TLegend(0.6,0.6,1.0,1.0)
  l.SetFillColor(0)
  l.SetShadowColor(ROOT.kWhite)
  l.SetBorderSize(1)


  bkg_stack = ROOT.THStack("bkgs","bkgs")
  for b in reversed(backgrounds):
    plots[pk]['histo'][b['name']].SetFillColor(b["color"])
    plots[pk]['histo'][b['name']].SetMarkerColor(b["color"])
    plots[pk]['histo'][b['name']].SetMarkerSize(0)
    plots[pk]['histo'][b['name']].SetLineWidth(0)
#    plots[pk]['histo'][b['name']].GetYaxis().SetRangeUser(10**-2.5, 2*plots[pk]['histo'][b['name']].GetMaximum())
    bkg_stack.Add(plots[pk]['histo'][b['name']],"h")
    l.AddEntry(plots[pk]['histo'][b['name']], b["name"])

  #Plot!
  c1 = ROOT.TCanvas()


  bkg_stack.SetMaximum(2*bkg_stack.GetMaximum())
  bkg_stack.SetMinimum(10**-1.5)
  bkg_stack.Draw('e')
  bkg_stack.GetXaxis().SetTitle(plots[pk]['title'])
  binning = plots[pk]['binning']
  bkg_stack.GetYaxis().SetTitle("Events / %i GeV"%( (binning[2]-binning[1])/binning[0]) )
  c1.SetLogy()

  data_stack = ROOT.THStack("data","data")
  for d in reversed(data):
    data_stack.Add(plots[pk]['histo'][d['name']],"h")
    data_stack.Draw('pesame')

  signalPlot_1 = plots[pk]['histo'][signal['path'][0]].Clone()
  signalPlot_2 = plots[pk]['histo'][signal['path'][2]].Clone()
  signalPlot_1.Scale(100)
  signalPlot_2.Scale(100)
  signalPlot_1.SetLineColor(ROOT.kRed)
  signalPlot_2.SetLineColor(ROOT.kBlue)
  signalPlot_1.SetLineWidth(3)
  signalPlot_2.SetLineWidth(3)
  signalPlot_1.Draw("HISTsame")
  signalPlot_2.Draw("HISTsame")
  data_stack.Draw("HISTesame")

  #plots[pk]['histo'][d['name']].Draw('hsame')

  #data_stack.Draw('pesame')
  l.AddEntry(signalPlot_1, signal['path'][0]+" x 100" ,"l")
  l.AddEntry(signalPlot_2, signal['path'][2]+" x 100", "l")
  #l.AddEntry(, "p")
  l.Draw()
  c1.Print(plotDir+"/"+prefix+'_'+plots[pk]["name"]+".png")
