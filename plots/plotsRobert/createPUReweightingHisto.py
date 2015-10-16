import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()

from math import *
import array

from StopsDilepton.tools.mtautau import mtautau as mtautau_
from StopsDilepton.tools.helpers import getChain, getObjDict, getEList, getVarValue, getPlotFromChain
from StopsDilepton.tools.objectSelection import getLeptons, looseMuID, looseEleID, getJets 
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()
from StopsDilepton.tools.localInfo import *

#preselection = 'met_pt>40&&Sum$((Jet_pt)*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))>100&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.814)==2&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2&&Sum$(LepGood_pt>20)>=2'
preselection = 'isOS&&abs(dl_mass-90.2)<=15.&&isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0'
dataCut = "(HLT_mumuIso&&Flag_HBHENoiseFilterMinZeroPatched&&Flag_goodVertices&&Flag_CSCTightHaloFilter&&Flag_eeBadScFilter)"
prefix="doubleMu_onZ_isOS"

#load all the samples
from StopsDilepton.samples.cmgTuples_Spring15_50ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_Spring15_25ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data50ns_1l_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_postProcessed import *

backgrounds = [TTJets_25ns, DY_25ns, singleTop_25ns, WJetsToLNu_25ns, QCDMu_25ns]
#backgrounds = [TTJets_25ns, DY_25ns, singleTop_25ns, diBosons_25ns, WJetsHTToLNu_25ns]#, QCD]
for b in backgrounds:
  b['isData']=False

data = DoubleMuon_Run2015D
data['isData']=True

#get the TChains for each sample
for s in backgrounds+[data]:
  s['chain'] = getChain(s,histname="")

#plots
plots = {\
  'nVert': {'title':'nVert', 'name':'nVert', 'binning': [50,0,50], 'histo':{}},
}

#make plot in each sample: 
for s in backgrounds:
  for pk in plots.keys():
    plots[pk]['histo'][s['name']] = getPlotFromChain(s['chain'], plots[pk]['name'], plots[pk]['binning'], cutString = preselection)
for s in [data]:
  for pk in plots.keys():
    plots[pk]['histo'][s['name']] = getPlotFromChain(s['chain'], plots[pk]['name'], plots[pk]['binning'], cutString = preselection+"&&"+dataCut)

for pk in plots.keys():
  plots[pk]['sum'] =  plots[pk]['histo'][backgrounds[0]['name']].Clone() 
  for b in backgrounds[1:]:
    plots[pk]['sum'].Add(plots[pk]['histo'][b['name']]) 
    

#Some coloring
TTJets_50ns["color"]=ROOT.kRed
TTJets_25ns["color"]=ROOT.kRed
WJetsHTToLNu_25ns["color"]=ROOT.kGreen
WJetsToLNu_25ns["color"]=ROOT.kGreen
#TTVH["color"]=ROOT.kMagenta
diBosons_50ns["color"]=ROOT.kMagenta
diBosons_25ns["color"]=ROOT.kMagenta
#QCDMu_50ns["color"]=ROOT.kMagenta
QCDMu_25ns["color"]=ROOT.kMagenta
singleTop_50ns["color"]=ROOT.kOrange
singleTop_25ns["color"]=ROOT.kOrange
DY_50ns["color"]=ROOT.kBlue
DY_25ns["color"]=ROOT.kBlue

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

  plots[pk]['histo'][data['name']].Draw('hsame')
#  signal = "SMS_T2tt_2J_mStop650_mLSP325"#May chose different signal here
#  signalPlot = plots[pk]['histo'][signal].Clone()
#  signalPlot.Scale(100)
#  signalPlot.Draw("same")
#  l.AddEntry(signalPlot, signal+" x 100")
  l.Draw()
  c1.Print(plotDir+"/"+prefix+'_'+plots[pk]["name"]+".png")

  plots[pk]['sum'].Scale(1./plots[pk]['sum'].Integral())
  plots[pk]['histo'][data['name']].Scale(1./plots[pk]['histo'][data['name']].Integral())
  plots[pk]['histo'][data['name']].Divide(plots[pk]['sum'])
  plots[pk]['histo'][data['name']].Draw()
  plots[pk]['histo'][data['name']].SetName("nVtxReweight")
  plots[pk]['histo'][data['name']].SetTitle("nVtxReweight")
  c1.Print(plotDir+"/"+prefix+'_'+plots[pk]["name"]+"_reweight.png")
  f = ROOT.TFile(plotDir+"/"+prefix+'_'+plots[pk]["name"]+"_reweight.root", "recreate")
  plots[pk]['histo'][data['name']].Write()
  f.Close()
