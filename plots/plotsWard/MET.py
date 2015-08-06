import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()
import numpy

from math import *
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()
from StopsDilepton.tools.helpers import getChain, getObjDict, getEList, getVarValue, genmatching, latexmaker, piemaker, getWeight
from StopsDilepton.tools.objectSelection import getLeptons, looseMuID, looseEleID, getJets, ele_ID_eta, getGenParts
from StopsDilepton.tools.localInfo import *

#preselection: MET>40, njets>=2, n_bjets>=1, n_lep>=2
#For now see here for the Sum$ syntax: https://root.cern.ch/root/html/TTree.html#TTree:Draw@2
#preselection = 'met_pt>40&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.814)>=1&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2&&Sum$(LepGood_pt>20)>=2'
preselection = 'met_pt>40&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2&&Sum$(LepGood_pt>20)>=2'

#######################################################
#        SELECT WHAT YOU WANT TO DO HERE              #
#######################################################
reduceStat = 1 #recude the statistics, i.e. 10 is ten times less samples to look at

#######################################################
#                 load all the samples                #
#######################################################
from StopsDilepton.plots.cmgTuplesPostProcessed_PHYS14 import *
from StopsDilepton.plots.cmgTuples_SPRING15 import *
#backgrounds = [WJetsHTToLNu, TTH, TTW, TTZ, DYWARD, singleTop, TTJets]#, QCD]
backgrounds = [DY_15,DY]
#signals = [SMS_T2tt_2J_mStop425_mLSP325, SMS_T2tt_2J_mStop500_mLSP325, SMS_T2tt_2J_mStop650_mLSP325, SMS_T2tt_2J_mStop850_mLSP100]
signals = []


#######################################################
#            get the TChains for each sample          #
#######################################################
for s in backgrounds+signals:
  if s.has_key('totalweight'): s['chain'] = getChain(s,histname="",treeName="tree")
  else:                        s['chain'] = getChain(s,histname="")

metbinning = [25,20,520]
dphibinning = [50,-1.1,1.1]

plots = {\
  'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'binning': metbinning, 'histo':{}},
  'dPhi_1':{'title':'cos(dPhi(MET,jet_1))', 'name':'leadingdPhi', 'binning':dphibinning, 'histo':{}},
  'dPhi_2':{'title':'cos(dPhi(MET,jet_2))', 'name':'subleadingdPhi', 'binning':dphibinning, 'histo':{}},
}


#######################################################
#            Start filling in the histograms          #
#######################################################
for s in backgrounds+signals:
  #1D
  for plot in plots.keys():
    plots[plot]['histo'][s["name"]] = ROOT.TH1F(plots[plot]['name']+"_"+s["name"], plots[plot]['name']+"_"+s["name"], *plots[plot]['binning'])
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
    #event weight (L= 4fb^-1)
    if s.has_key('totalweight'): weight = getWeight(chain,s, 4000) #this method for SPRING15 samples
    else:                        weight = reduceStat*getVarValue(chain, "weight") #this method for PHYS14 samples
    #MET
    met = getVarValue(chain, "met_pt")
    metPhi = getVarValue(chain, "met_phi")
    #jets
    leadingjetPhi = getVarValue(chain, "Jet_phi",0)
    subleadingjetPhi = getVarValue(chain, "Jet_phi",1)

    dphi_1 = abs(metPhi-leadingjetPhi)
    dphi_2 = abs(metPhi-subleadingjetPhi)

    if dphi_1>pi : dphi_1 -= pi
    if dphi_2>pi : dphi_2 -= pi

    plots['met']['histo'][s["name"]].Fill(met, weight)
    plots['dPhi_1']['histo'][s['name']].Fill(cos(dphi_1), weight)
    plots['dPhi_2']['histo'][s['name']].Fill(cos(dphi_2), weight)

  del eList



#######################################################
#             Drawing done here                       #
#######################################################
#Some coloring
#TTJets["color"]=ROOT.kRed
WJetsHTToLNu["color"]=ROOT.kGreen
#TTH["color"]=ROOT.kMagenta
#TTW["color"]=ROOT.kMagenta-3
#TTZ["color"]=ROOT.kMagenta-6
#singleTop["color"]=ROOT.kOrange
DY["color"]=ROOT.kBlue
DY_15["color"]=ROOT.kRed
#Plotvariables
signal = {'path': ["SMS_T2tt_2J_mStop425_mLSP325","SMS_T2tt_2J_mStop500_mLSP325","SMS_T2tt_2J_mStop650_mLSP325","SMS_T2tt_2J_mStop850_mLSP100"], 'name': ["T2tt(425,325)","T2tt(500,325)","T2tt(650,325)","T2tt(850,100)"]}
yminimum = 10**-0.5
legendtextsize = 0.032
signalscaling = 100

makedraw1D = True

if makedraw1D:
  for plot in plots.keys():
    for s in backgrounds+signals:
      integral = plots[plot]['histo'][s['name']].Integral()
      plots[plot]['histo'][s['name']].Scale(1./integral)

    #Make a stack for backgrounds
    l=ROOT.TLegend(0.6,0.8,1.0,1.0)
    l.SetFillColor(0)
    l.SetShadowColor(ROOT.kWhite)
    l.SetBorderSize(1)
    l.SetTextSize(legendtextsize)

    #Plot!
    c1 = ROOT.TCanvas()
    for i,b in enumerate(backgrounds):
      plots[plot]['histo'][b["name"]].SetLineColor(b["color"])
      plots[plot]['histo'][b["name"]].SetLineWidth(3)
      plots[plot]['histo'][b["name"]].SetMarkerSize(0)
      plots[plot]['histo'][b["name"]].Draw("same")
      l.AddEntry(plots[plot]['histo'][b["name"]],b['name'])
      if i == 0: 
        plots[plot]['histo'][b["name"]].GetXaxis().SetTitle(plots[plot]['title'])
        plots[plot]['histo'][b["name"]].GetYaxis().SetTitle("Events / %i GeV"%( (plots[plot]['binning'][2]-plots[plot]['binning'][1])/plots[plot]['binning'][0]) )
        plots[plot]['histo'][b["name"]].GetYaxis().SetRangeUser(0.00001,2)
    c1.SetLogy()
    l.Draw()
    c1.Print(plotDir+"/test/"+plots[plot]['name']+".png")
  
