import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()
import numpy

from math import *
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()
from StopsDilepton.tools.helpers import getChain, getObjDict, getEList, getVarValue, genmatching, latexmaker, piemaker, getWeight, deltaPhi
from StopsDilepton.tools.objectSelection import getLeptons, looseMuID, looseEleID, getJets, ele_ID_eta, getGenParts
from StopsDilepton.tools.localInfo import *

#preselection: MET>40, njets>=2, n_bjets>=1, n_lep>=2
#See here for the Sum$ syntax: https://root.cern.ch/root/html/TTree.html#TTree:Draw@2
preselection = 'met_pt>40&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.814)>=1&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2&&Sum$(LepGood_pt>20)>=2'

#######################################################
#        SELECT WHAT YOU WANT TO DO HERE              #
#######################################################
reduceStat = 1 #recude the statistics, i.e. 10 is ten times less samples to look at
makedraw1D = True
makedraw2D = True
makelatextables = False #Ignore this if you're not Ward
makepiechart = False    #Ignore this if you're not Ward

#######################################################
#                 load all the samples                #
#######################################################
from StopsDilepton.samples.cmgTuplesPostProcessed_PHYS14 import *
from StopsDilepton.samples.cmgTuples_SPRING15_WardPrivateProduction import *
#backgrounds = [WJetsHTToLNu, TTH, TTW, TTZ, DYWARD, singleTop, TTJets]#, QCD]
backgrounds = [DY_15,TTJets_15]
signals = [SMS_T2tt_2J_mStop425_mLSP325, SMS_T2tt_2J_mStop500_mLSP325, SMS_T2tt_2J_mStop650_mLSP325, SMS_T2tt_2J_mStop850_mLSP100]
#signals = []


#######################################################
#            get the TChains for each sample          #
#######################################################
#PHYS14 and my(!) SPRING15 ntuples are structured a bit differently (i.e. treeName is different). PHYS14 have correct weight stored in ntuple
#SPRING15 has to make the weight with xsec,luminosity and totalweight (total genWeight) that I saved by hand
for s in backgrounds+signals:
  if s.has_key('totalweight'): s['chain'] = getChain(s,histname="",treeName="tree")
  else:                        s['chain'] = getChain(s,histname="")


#ROOT output file
#MET_n = numpy.array([-999],dtype=float)
#MT2ee_n =numpy.array([-999],dtype=float)
#MT2emu_n =numpy.array([-999],dtype=float)
#MT2mumu_n =numpy.array([-999],dtype=float)



#######################################################
#           define binning of 1D histograms           #
#######################################################
mllbinning = [25,25,325] 
mt2llbinning = [25,0,300]
metbinning = [20,0,800]
mt2bbbinning = [25,0,550]
mt2blblbinning = [25,0,550]
kinMetSigbinning = [25,0,25]
leadingjetptbinning = [25,25,575]
subleadingjetptbinning = [25,25,575]
leadingleptonptbinning = [25,25,575]
subleadingleptonptbinning = [25,25,575]
njetsbinning = [15,0,15]
nbjetsbinning = [10,0,10]
cosbinning = [25,-1.1,1.1]
partonbinning = [32,-10,22]
phibinning = [20,0,pi]

#######################################################
#             make plot in each sample:               #
#######################################################
plots = {\
  'mumu':{\
  'mll': {'title':'M_{ll} (GeV)', 'name':'mll', 'binning': mllbinning, 'histo':{}},
  'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
  'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'binning': metbinning, 'histo':{}},
  'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'MT2bb', 'binning': mt2bbbinning, 'histo':{}},
  'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'MT2blbl', 'binning': mt2blblbinning, 'histo':{}},
  'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2})', 'name':'kinMetSig', 'binning': kinMetSigbinning, 'histo':{}},
  'leadingjetpt': {'title':'leading jet p_{T} (GeV)', 'name':'leadingjetpt', 'binning': leadingjetptbinning, 'histo':{}},
  'subleadingjetpt': {'title':'subleading jet p_{T} (GeV)', 'name':'subleadingjetpt', 'binning': subleadingjetptbinning, 'histo':{}},
  'leadingleptonpt': {'title':'leading lep p_{T} (GeV)', 'name':'leadingleptonpt', 'binning': leadingleptonptbinning, 'histo':{}},
  'subleadingleptonpt': {'title':'subleading lep p_{T} (GeV)', 'name':'subleadingleptonpt', 'binning': subleadingleptonptbinning, 'histo':{}},
  'njets': {'title': 'njets', 'name':'njets', 'binning': njetsbinning, 'histo':{}},
  'nbjets': {'title': 'nbjets', 'name':'nbjets', 'binning': nbjetsbinning, 'histo':{}},
  'leadingjetpartonId':{'title': 'Leading Jet Parton Id','name':'LeadingJetPartonId','binning':partonbinning,'histo':{}},
  'CosMinDphi':{'title':'Cos(Min(dPhi(MET,jet_1|jet_2)))','name':'CosMinDphiJets', 'binning':cosbinning, 'histo':{}},
  'CosMinDphiMt2llcut':{'title':'Cos(Min(dPhi(MET,jet_1|jet_2)))', 'name':'CosMinDphiJetsMt2llcut', 'binning':cosbinning, 'histo':{},'tag':'MT2cut'},
  'MinDphi':{'title':'Min(dPhi(MET,jet_1|jet_2))','name':'MinDphiJets', 'binning':phibinning, 'histo':{}},
  'MinDphiMt2llcut':{'title':'Min(dPhi(MET,jet_1|jet_2))', 'name':'MinDphiJetsMt2llcut', 'binning':phibinning, 'histo':{},'tag':'MT2cut'},
  },
  'ee':{\
  'mll': {'title':'M_{ll} (GeV)', 'name':'mll', 'binning': mllbinning, 'histo':{}},
  'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
  'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'binning': metbinning, 'histo':{}},
  'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'MT2bb', 'binning': mt2bbbinning, 'histo':{}},
  'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'MT2blbl', 'binning': mt2blblbinning, 'histo':{}},
  'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2})', 'name':'kinMetSig', 'binning': kinMetSigbinning, 'histo':{}},
  'leadingjetpt': {'title':'leading jet p_{T} (GeV)', 'name':'leadingjetpt', 'binning': leadingjetptbinning, 'histo':{}},
  'subleadingjetpt': {'title':'subleading jet p_{T} (GeV)', 'name':'subleadingjetpt', 'binning': subleadingjetptbinning, 'histo':{}},
  'leadingleptonpt': {'title':'leading lep p_{T} (GeV)', 'name':'leadingleptonpt', 'binning': leadingleptonptbinning, 'histo':{}},
  'subleadingleptonpt': {'title':'subleading lep p_{T} (GeV)', 'name':'subleadingleptonpt', 'binning': subleadingleptonptbinning, 'histo':{}},
  'njets': {'title': 'njets', 'name':'njets', 'binning': njetsbinning, 'histo':{}},
  'nbjets': {'title': 'nbjets', 'name':'nbjets', 'binning': nbjetsbinning, 'histo':{}},
  'leadingjetpartonId':{'title': 'Leading Jet Parton Id','name':'LeadingJetPartonId','binning':partonbinning,'histo':{}},
  'CosMinDphi':{'title':'Cos(Min(dPhi(MET,jet_1|jet_2)))','name':'CosMinDphiJets', 'binning':cosbinning, 'histo':{}},
  'CosMinDphiMt2llcut':{'title':'Cos(Min(dPhi(MET,jet_1|jet_2)))', 'name':'CosMinDphiJetsMt2llcut', 'binning':cosbinning, 'histo':{},'tag':'MT2cut'},
  'MinDphi':{'title':'Min(dPhi(MET,jet_1|jet_2))','name':'MinDphiJets', 'binning':phibinning, 'histo':{}},
  'MinDphiMt2llcut':{'title':'Min(dPhi(MET,jet_1|jet_2))', 'name':'MinDphiJetsMt2llcut', 'binning':phibinning, 'histo':{},'tag':'MT2cut'},
  },
  'emu':{\
  'mll': {'title':'M_{ll} (GeV)', 'name':'mll', 'binning': mllbinning, 'histo':{}},
  'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
  'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'binning': metbinning, 'histo':{}},
  'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'MT2bb', 'binning': mt2bbbinning, 'histo':{}},
  'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'MT2blbl', 'binning': mt2blblbinning, 'histo':{}},
  'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2})', 'name':'kinMetSig', 'binning': kinMetSigbinning, 'histo':{}},
  'leadingjetpt': {'title':'leading jet p_{T} (GeV)', 'name':'leadingjetpt', 'binning': leadingjetptbinning, 'histo':{}},
  'subleadingjetpt': {'title':'subleading jet p_{T} (GeV)', 'name':'subleadingjetpt', 'binning': subleadingjetptbinning, 'histo':{}},
  'leadingleptonpt': {'title':'leading lep p_{T} (GeV)', 'name':'leadingleptonpt', 'binning': leadingleptonptbinning, 'histo':{}},
  'subleadingleptonpt': {'title':'subleading lep p_{T} (GeV)', 'name':'subleadingleptonpt', 'binning': subleadingleptonptbinning, 'histo':{}},
  'njets': {'title': 'njets', 'name':'njets', 'binning': njetsbinning, 'histo':{}},
  'nbjets': {'title': 'nbjets', 'name':'nbjets', 'binning': nbjetsbinning, 'histo':{}},
  'leadingjetpartonId':{'title': 'Leading Jet Parton Id','name':'LeadingJetPartonId','binning':partonbinning,'histo':{}},
  'CosMinDphi':{'title':'Cos(Min(dPhi(MET,jet_1|jet_2)))','name':'CosMinDphiJets', 'binning':cosbinning, 'histo':{}},
  'CosMinDphiMt2llcut':{'title':'Cos(Min(dPhi(MET,jet_1|jet_2)))', 'name':'CosMinDphiJetsMt2llcut', 'binning':cosbinning, 'histo':{},'tag':'MT2cut'},
  'MinDphi':{'title':'Min(dPhi(MET,jet_1|jet_2))','name':'MinDphiJets', 'binning':phibinning, 'histo':{}},
  'MinDphiMt2llcut':{'title':'Min(dPhi(MET,jet_1|jet_2))', 'name':'MinDphiJetsMt2llcut', 'binning':phibinning, 'histo':{},'tag':'MT2cut'},
},
}

#######################################################
#          make plots specifically for SF             #
#######################################################
plotsSF = {\
  'SF':{\
  'mll': {'title':'M_{ll} (GeV)', 'name':'mll', 'binning': mllbinning, 'histo':{}},
  'mt2ll': {'title':'M_{T2ll} (GeV)', 'name':'MT2ll', 'binning': mt2llbinning, 'histo':{}},
  'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'binning': metbinning, 'histo':{}},
  'mt2bb':{'title':'M_{T2bb} (GeV)', 'name':'MT2bb', 'binning': mt2bbbinning, 'histo':{}},
  'mt2blbl':{'title':'M_{T2blbl} (GeV)', 'name':'MT2blbl', 'binning': mt2blblbinning, 'histo':{}},
  'kinMetSig':{'title':'MET/#sqrt{H_{T}} (GeV^{1/2})', 'name':'kinMetSig', 'binning': kinMetSigbinning, 'histo':{}},
  'leadingjetpt': {'title':'leading jet p_{T} (GeV)', 'name':'leadingjetpt', 'binning': leadingjetptbinning, 'histo':{}},
  'subleadingjetpt': {'title':'subleading jet p_{T} (GeV)', 'name':'subleadingjetpt', 'binning': subleadingjetptbinning, 'histo':{}},
  'leadingleptonpt': {'title':'leading lep p_{T} (GeV)', 'name':'leadingleptonpt', 'binning': leadingleptonptbinning, 'histo':{}},
  'subleadingleptonpt': {'title':'subleading lep p_{T} (GeV)', 'name':'subleadingleptonpt', 'binning': subleadingleptonptbinning, 'histo':{}},
  'njets': {'title': 'njets', 'name':'njets', 'binning': njetsbinning, 'histo':{}},
  'nbjets': {'title': 'nbjets', 'name':'nbjets', 'binning': nbjetsbinning, 'histo':{}},
  'leadingjetpartonId':{'title': 'Leading Jet Parton Id','name':'LeadingJetPartonId','binning':partonbinning,'histo':{}},
  'CosMinDphi':{'title':'Cos(Min(dPhi(MET,jet_1|jet_2)))','name':'CosMinDphiJets', 'binning':cosbinning, 'histo':{}},
  'CosMinDphiMt2llcut':{'title':'Cos(Min(dPhi(MET,jet_1|jet_2)))', 'name':'CosMinDphiJetsMt2llcut', 'binning':cosbinning, 'histo':{},'tag':'MT2cut'},
  'MinDphi':{'title':'Min(dPhi(MET,jet_1|jet_2))','name':'MinDphiJets', 'binning':phibinning, 'histo':{}},
  'MinDphiMt2llcut':{'title':'Min(dPhi(MET,jet_1|jet_2))', 'name':'MinDphiJetsMt2llcut', 'binning':phibinning, 'histo':{},'tag':'MT2cut'},
  },
}


#######################################################
#                   2D plots                          #
#######################################################
dimensional = {\
  'ee': {\
  'metvsmt2ll': {'xtitle':'M_{T2ll} (GeV)','ytitle':'E^{miss}_{T} (GeV)', 'name': 'METvsMT2ll', 'ybinning': metbinning, 'xbinning': mt2llbinning, 'histo': {}},
  'MT2llvsCosdPhi_1':{'xtitle':'Cos(dPhi(MET,jet_1))','ytitle':'MT2ll', 'name':'MT2llvsCosDphiLeadingJet', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
  'MT2llvsCosdPhi_2':{'xtitle':'Cos(dPhi(MET,jet_2))','ytitle':'MT2ll', 'name':'MT2llvsCosDphiSubleadingJet', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
  'MT2llvsCosMinDphi':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'MT2ll', 'name':'MT2llvsCosMinDphiJets', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
  'MT2llvsdPhi_1':{'xtitle':'dPhi(MET,jet_1)','ytitle':'MT2ll', 'name':'MT2llvsDphiLeadingJet', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
  'MT2llvsdPhi_2':{'xtitle':'dPhi(MET,jet_2)','ytitle':'MT2ll', 'name':'MT2llvsDphiSubleadingJet', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
  'MT2llvsMinDphi':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'MT2ll', 'name':'MT2llvsMinDphiJets', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
  'metvsCosdPhi_1':{'xtitle':'Cos(dPhi(MET,jet_1))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosDphiLeadingJet', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
  'metvsCosdPhi_2':{'xtitle':'Cos(dPhi(MET,jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosDphiSubleadingJet', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
  'metvsCosMinDphi':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosMinDphiJets', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
  'metvsCosMinDphiMt2llcut':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosMinDphiJetsMt2llcut', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{},'tag':'MT2cut'},
  'metvsdPhi_1':{'xtitle':'dPhi(MET,jet_1)','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsDphiLeadingJet', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
  'metvsdPhi_2':{'xtitle':'dPhi(MET,jet_2)','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsDphiSubleadingJet', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
  'metvsMinDphi':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsMinDphiJets', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
  'metvsMinDphiMt2llcut':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsMinDphiJetsMt2llcut', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{},'tag':'MT2cut'},
 },
  'mumu': {\
  'metvsmt2ll': {'xtitle':'M_{T2ll} (GeV)','ytitle':'E^{miss}_{T} (GeV)', 'name': 'METvsMT2ll', 'ybinning': metbinning, 'xbinning': mt2llbinning, 'histo': {}},
  'MT2llvsCosdPhi_1':{'xtitle':'Cos(dPhi(MET,jet_1))','ytitle':'MT2ll', 'name':'MT2llvsCosDphiLeadingJet', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
  'MT2llvsCosdPhi_2':{'xtitle':'Cos(dPhi(MET,jet_2))','ytitle':'MT2ll', 'name':'MT2llvsCosDphiSubleadingJet', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
  'MT2llvsCosMinDphi':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'MT2ll', 'name':'MT2llvsCosMinDphiJets', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
  'MT2llvsdPhi_1':{'xtitle':'dPhi(MET,jet_1)','ytitle':'MT2ll', 'name':'MT2llvsDphiLeadingJet', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
  'MT2llvsdPhi_2':{'xtitle':'dPhi(MET,jet_2)','ytitle':'MT2ll', 'name':'MT2llvsDphiSubleadingJet', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
  'MT2llvsMinDphi':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'MT2ll', 'name':'MT2llvsMinDphiJets', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
  'metvsCosdPhi_1':{'xtitle':'Cos(dPhi(MET,jet_1))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosDphiLeadingJet', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
  'metvsCosdPhi_2':{'xtitle':'Cos(dPhi(MET,jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosDphiSubleadingJet', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
  'metvsCosMinDphi':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosMinDphiJets', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
  'metvsCosMinDphiMt2llcut':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosMinDphiJetsMt2llcut', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{},'tag':'MT2cut'},
  'metvsdPhi_1':{'xtitle':'dPhi(MET,jet_1)','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsDphiLeadingJet', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
  'metvsdPhi_2':{'xtitle':'dPhi(MET,jet_2)','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsDphiSubleadingJet', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
  'metvsMinDphi':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsMinDphiJets', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
  'metvsMinDphiMt2llcut':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsMinDphiJetsMt2llcut', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{},'tag':'MT2cut'},
 },
  'emu': {\
  'metvsmt2ll': {'xtitle':'M_{T2ll} (GeV)','ytitle':'E^{miss}_{T} (GeV)', 'name': 'METvsMT2ll', 'ybinning': metbinning, 'xbinning': mt2llbinning, 'histo': {}},
  'MT2llvsCosdPhi_1':{'xtitle':'Cos(dPhi(MET,jet_1))','ytitle':'MT2ll', 'name':'MT2llvsCosDphiLeadingJet', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
  'MT2llvsCosdPhi_2':{'xtitle':'Cos(dPhi(MET,jet_2))','ytitle':'MT2ll', 'name':'MT2llvsCosDphiSubleadingJet', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
  'MT2llvsCosMinDphi':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'MT2ll', 'name':'MT2llvsCosMinDphiJets', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
  'MT2llvsdPhi_1':{'xtitle':'dPhi(MET,jet_1)','ytitle':'MT2ll', 'name':'MT2llvsDphiLeadingJet', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
  'MT2llvsdPhi_2':{'xtitle':'dPhi(MET,jet_2)','ytitle':'MT2ll', 'name':'MT2llvsDphiSubleadingJet', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
  'MT2llvsMinDphi':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'MT2ll', 'name':'MT2llvsMinDphiJets', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
  'metvsCosdPhi_1':{'xtitle':'Cos(dPhi(MET,jet_1))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosDphiLeadingJet', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
  'metvsCosdPhi_2':{'xtitle':'Cos(dPhi(MET,jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosDphiSubleadingJet', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
  'metvsCosMinDphi':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosMinDphiJets', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
  'metvsCosMinDphiMt2llcut':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosMinDphiJetsMt2llcut', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{},'tag':'MT2cut'},
  'metvsdPhi_1':{'xtitle':'dPhi(MET,jet_1)','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsDphiLeadingJet', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
  'metvsdPhi_2':{'xtitle':'dPhi(MET,jet_2)','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsDphiSubleadingJet', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
  'metvsMinDphi':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsMinDphiJets', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
  'metvsMinDphiMt2llcut':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsMinDphiJetsMt2llcut', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{},'tag':'MT2cut'},
  }
}

dimensionalSF={\
  'SF': {\
  'metvsmt2ll': {'xtitle':'M_{T2ll} (GeV)','ytitle':'E^{miss}_{T} (GeV)', 'name': 'METvsMT2ll', 'ybinning': metbinning, 'xbinning': mt2llbinning, 'histo': {}},
  'MT2llvsCosdPhi_1':{'xtitle':'Cos(dPhi(MET,jet_1))','ytitle':'MT2ll', 'name':'MT2llvsCosDphiLeadingJet', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
  'MT2llvsCosdPhi_2':{'xtitle':'Cos(dPhi(MET,jet_2))','ytitle':'MT2ll', 'name':'MT2llvsCosDphiSubleadingJet', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
  'MT2llvsCosMinDphi':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'MT2ll', 'name':'MT2llvsCosMinDphiJets', 'ybinning': mt2llbinning, 'xbinning':cosbinning, 'histo':{}},
  'MT2llvsdPhi_1':{'xtitle':'dPhi(MET,jet_1)','ytitle':'MT2ll', 'name':'MT2llvsDphiLeadingJet', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
  'MT2llvsdPhi_2':{'xtitle':'dPhi(MET,jet_2)','ytitle':'MT2ll', 'name':'MT2llvsDphiSubleadingJet', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
  'MT2llvsMinDphi':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'MT2ll', 'name':'MT2llvsMinDphiJets', 'ybinning': mt2llbinning, 'xbinning':phibinning, 'histo':{}},
  'metvsCosdPhi_1':{'xtitle':'Cos(dPhi(MET,jet_1))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosDphiLeadingJet', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
  'metvsCosdPhi_2':{'xtitle':'Cos(dPhi(MET,jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosDphiSubleadingJet', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
  'metvsCosMinDphi':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosMinDphiJets', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{}},
  'metvsCosMinDphiMt2llcut':{'xtitle':'Cos(Min(dPhi(MET,jet_1|jet_2)))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsCosMinDphiJetsMt2llcut', 'ybinning': metbinning, 'xbinning':cosbinning, 'histo':{},'tag':'MT2cut'},
  'metvsdPhi_1':{'xtitle':'dPhi(MET,jet_1)','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsDphiLeadingJet', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
  'metvsdPhi_2':{'xtitle':'dPhi(MET,jet_2)','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsDphiSubleadingJet', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
  'metvsMinDphi':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsMinDphiJets', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{}},
  'metvsMinDphiMt2llcut':{'xtitle':'Min(dPhi(MET,jet_1|jet_2))','ytitle':'E^{miss}_{T} (GeV)', 'name':'metvsMinDphiJetsMt2llcut', 'ybinning': metbinning, 'xbinning':phibinning, 'histo':{},'tag':'MT2cut'},
  }
}

#######################################################
#            Start filling in the histograms          #
#######################################################
for s in backgrounds+signals:
  #construct 1D histograms
  for pk in plots.keys():
    for plot in plots[pk].keys():
      plots[pk][plot]['histo'][s["name"]] = ROOT.TH1F(plots[pk][plot]['name']+"_"+s["name"]+"_"+pk, plots[pk][plot]['name']+"_"+s["name"]+"_"+pk, *plots[pk][plot]['binning'])
  #construct 2D histograms
  for pk in dimensional.keys():
    for plot in dimensional[pk].keys():
      dimensional[pk][plot]['histo'][s["name"]] = ROOT.TH2F(dimensional[pk][plot]['name']+"_"+s["name"]+"_"+pk, dimensional[pk][plot]['name']+"_"+s["name"]+"_"+pk, dimensional[pk][plot]['xbinning'][0], dimensional[pk][plot]['xbinning'][1],dimensional[pk][plot]['xbinning'][2], dimensional[pk][plot]['ybinning'][0], dimensional[pk][plot]['ybinning'][1],dimensional[pk][plot]['ybinning'][2])

  chain = s["chain"]
   
  chain.SetBranchStatus("*",0)
  chain.SetBranchStatus("met_pt",1)
  chain.SetBranchStatus("met_phi",1)
  chain.SetBranchStatus("Jet_pt",1)
  chain.SetBranchStatus("Jet_eta",1)
  chain.SetBranchStatus("Jet_id",1)
  chain.SetBranchStatus("Jet_btagCSV",1)
  chain.SetBranchStatus("LepGood_pt",1)
  chain.SetBranchStatus("LepGood_eta",1)
  chain.SetBranchStatus("LepGood_phi",1)
  chain.SetBranchStatus("LepGood_charge",1)
  chain.SetBranchStatus("LepGood_dxy",1)
  chain.SetBranchStatus("LepGood_dz",1)
  chain.SetBranchStatus("LepGood_relIso03",1)
  chain.SetBranchStatus("LepGood_tightId",1)
  chain.SetBranchStatus("LepGood_pdgId",1)
  chain.SetBranchStatus("LepGood_mediumMuonId",1)
  chain.SetBranchStatus("LepGood_miniRelIso",1)
  chain.SetBranchStatus("LepGood_sip3d",1)
  chain.SetBranchStatus("LepGood_mvaIdPhys14",1)
  chain.SetBranchStatus("LepGood_convVeto",1)
  chain.SetBranchStatus("LepGood_lostHits",1)
  chain.SetBranchStatus("Jet_eta",1)
  chain.SetBranchStatus("Jet_pt",1)
  chain.SetBranchStatus("Jet_phi",1)
  chain.SetBranchStatus("Jet_btagCMVA",1)
  chain.SetBranchStatus("Jet_btagCSV",1)
  chain.SetBranchStatus("Jet_mcMatchFlav",1)
  chain.SetBranchStatus("Jet_partonId",1)
  chain.SetBranchStatus("Jet_id",1)
  chain.SetBranchStatus("weight",1)
  chain.SetBranchStatus("genWeight",1)
  chain.SetBranchStatus("xsec",1)

  #Using Event loop
  #get EList after preselection
  print "Looping over %s" % s["name"]
  eList = getEList(chain, preselection) 
  nEvents = eList.GetN()/reduceStat
  print "Found %i events in %s after preselection %s, looping over %i" % (eList.GetN(),s["name"],preselection,nEvents)
 
  #ROOT output file
  #TreeFile = ROOT.TFile("./trees/tree"+s["name"]+".root","recreate")
  #Tree = ROOT.TTree("VarTree","Tree of Variables")
  #Tree.Branch("MET",MET_n,"MET/D")
  #Tree.Branch("MT2ee",MT2ee_n,"MT2ee/D")
  #Tree.Branch("MT2emu",MT2emu_n,"MT2emu/D")
  #Tree.Branch("MT2mumu",MT2mumu_n,"MT2mumu/D")
  for ev in range(nEvents):
    if ev%10000==0:print "At %i/%i"%(ev,nEvents)
    chain.GetEntry(eList.GetEntry(ev))
    mt2Calc.reset()
    #event weight (L= 4fb^-1)
    if s.has_key('totalweight'): weight = getWeight(chain,s, 4000) #this method for Ward's SPRING15 samples
    else:                        weight = reduceStat*getVarValue(chain, "weight") #this method for Robert's PHYS14 samples
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
    #GENinfo
    #genparticles = getGenParts(chain)
    #ROOT output file
    #MET_n[0] = met

    #SF and OF channels
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
          #genmatching(leptons[lep]['file'][0],genparticles)
          twoleptons = True
          l0pt, l0eta, l0phi = leptons[lep]['file'][0]['pt'],  leptons[lep]['file'][0]['eta'],  leptons[lep]['file'][0]['phi']
          l1pt, l1eta, l1phi = leptons[lep]['file'][1]['pt'],  leptons[lep]['file'][1]['eta'],  leptons[lep]['file'][1]['phi']
          leadingleptonpt = l0pt
          subleadingleptonpt = l1pt
          mll = sqrt(2.*l0pt*l1pt*(cosh(l0eta-l1eta)-cos(l0phi-l1phi)))
          plots[leptons[lep]['name']]['mll']['histo'][s["name"]].Fill(mll,weight) #mll as n-1 plot without Z-mass cut
          zveto = True
      #Opposite Flavor
      if lep == 'emu':
        if len(leptons[lep]['file'][0])==1 and len(leptons[lep]['file'][1])==1 and leptons[lep]['file'][0][0]['pdgId']*leptons[lep]['file'][1][0]['pdgId']<0:
          twoleptons = True
          l0pt, l0eta, l0phi = leptons[lep]['file'][0][0]['pt'],  leptons[lep]['file'][0][0]['eta'],  leptons[lep]['file'][0][0]['phi']
          l1pt, l1eta, l1phi = leptons[lep]['file'][1][0]['pt'],  leptons[lep]['file'][1][0]['eta'],  leptons[lep]['file'][1][0]['phi']
          if l1pt > l0pt :
            leadingleptonpt = l1pt
            subleadingleptonpt = l0pt
          else:
            leadingleptonpt = l0pt
            subleadingleptonpt = l1pt
          mll = sqrt(2.*l0pt*l1pt*(cosh(l0eta-l1eta)-cos(l0phi-l1phi)))
          plots[leptons[lep]['name']]['mll']['histo'][s["name"]].Fill(mll,weight) #mll as n-1 plot without Z-mass cut
          zveto = False
      if (twoleptons and mll>20 and not zveto) or (twoleptons and mll > 20 and zveto and abs(mll-90.2)>15):
        plots[leptons[lep]['name']]['leadingjetpt']['histo'][s["name"]].Fill(leadingjetpt, weight)
        plots[leptons[lep]['name']]['subleadingjetpt']['histo'][s["name"]].Fill(subleadingjetpt, weight)
        plots[leptons[lep]['name']]['leadingleptonpt']['histo'][s["name"]].Fill(leadingleptonpt, weight)
        plots[leptons[lep]['name']]['subleadingleptonpt']['histo'][s["name"]].Fill(subleadingleptonpt, weight)
        mt2Calc.setMet(met,metPhi)
        mt2Calc.setLeptons(l0pt, l0eta, l0phi, l1pt, l1eta, l1phi)
        
        mt2ll = mt2Calc.mt2ll()
        #ROOT output file
        #if lep == 'e': MT2ee_n[0] = mt2ll
        #if lep == 'emu': MT2emu_n[0] = mt2ll
        #if lep == 'mu': MT2mumu_n[0] = mt2ll
        plots[leptons[lep]['name']]['mt2ll']['histo'][s["name"]].Fill(mt2ll, weight)
        dimensional[leptons[lep]['name']]['metvsmt2ll']['histo'][s["name"]].Fill(mt2ll,met)
        jets = filter(lambda j:j['pt']>30 and abs(j['eta'])<2.4 and j['id'], getJets(chain))
        ht = sum([j['pt'] for j in jets])
        PhiMetJet1 = deltaPhi(metPhi,getVarValue(chain, "Jet_phi",0))
        PhiMetJet2 = deltaPhi(metPhi,getVarValue(chain, "Jet_phi",1))
        dimensional[leptons[lep]['name']]['MT2llvsCosdPhi_1']['histo'][s['name']].Fill(cos(PhiMetJet1),mt2ll)
        dimensional[leptons[lep]['name']]['MT2llvsCosdPhi_2']['histo'][s['name']].Fill(cos(PhiMetJet2),mt2ll)
        dimensional[leptons[lep]['name']]['MT2llvsdPhi_1']['histo'][s['name']].Fill(PhiMetJet1,mt2ll)
        dimensional[leptons[lep]['name']]['MT2llvsdPhi_2']['histo'][s['name']].Fill(PhiMetJet2,mt2ll)
        dimensional[leptons[lep]['name']]['metvsCosdPhi_1']['histo'][s['name']].Fill(cos(PhiMetJet1),met)
        dimensional[leptons[lep]['name']]['metvsCosdPhi_2']['histo'][s['name']].Fill(cos(PhiMetJet2),met)
        dimensional[leptons[lep]['name']]['metvsdPhi_1']['histo'][s['name']].Fill(PhiMetJet1,met)
        dimensional[leptons[lep]['name']]['metvsdPhi_2']['histo'][s['name']].Fill(PhiMetJet2,met)
        if (PhiMetJet1 <= PhiMetJet2): #selecting min(dPhi)
          dimensional[leptons[lep]['name']]['MT2llvsCosMinDphi']['histo'][s['name']].Fill(cos(PhiMetJet1),mt2ll)
          dimensional[leptons[lep]['name']]['MT2llvsMinDphi']['histo'][s['name']].Fill(PhiMetJet1,mt2ll)
          plots[leptons[lep]['name']]['CosMinDphi']['histo'][s['name']].Fill(cos(PhiMetJet1),weight)
          plots[leptons[lep]['name']]['MinDphi']['histo'][s['name']].Fill(PhiMetJet1,weight)
          dimensional[leptons[lep]['name']]['metvsCosMinDphi']['histo'][s['name']].Fill(cos(PhiMetJet1),met)
          dimensional[leptons[lep]['name']]['metvsMinDphi']['histo'][s['name']].Fill(PhiMetJet1,met)
          if (mt2ll>=80):
            plots[leptons[lep]['name']]['CosMinDphiMt2llcut']['histo'][s['name']].Fill(cos(PhiMetJet1),weight)
            plots[leptons[lep]['name']]['MinDphiMt2llcut']['histo'][s['name']].Fill(PhiMetJet1,weight)
            dimensional[leptons[lep]['name']]['metvsCosMinDphiMt2llcut']['histo'][s['name']].Fill(cos(PhiMetJet1),met)
            dimensional[leptons[lep]['name']]['metvsMinDphiMt2llcut']['histo'][s['name']].Fill(PhiMetJet1,met)
        else:
          dimensional[leptons[lep]['name']]['MT2llvsCosMinDphi']['histo'][s['name']].Fill(cos(PhiMetJet2),mt2ll)
          dimensional[leptons[lep]['name']]['MT2llvsMinDphi']['histo'][s['name']].Fill(PhiMetJet2,mt2ll)
          plots[leptons[lep]['name']]['CosMinDphi']['histo'][s['name']].Fill(cos(PhiMetJet2),weight)
          plots[leptons[lep]['name']]['MinDphi']['histo'][s['name']].Fill(PhiMetJet2,weight)
          dimensional[leptons[lep]['name']]['metvsCosMinDphi']['histo'][s['name']].Fill(cos(PhiMetJet2),met)
          dimensional[leptons[lep]['name']]['metvsMinDphi']['histo'][s['name']].Fill(PhiMetJet2,met)
          if mt2ll>=80:
            plots[leptons[lep]['name']]['CosMinDphiMt2llcut']['histo'][s['name']].Fill(cos(PhiMetJet2),weight)
            plots[leptons[lep]['name']]['MinDphiMt2llcut']['histo'][s['name']].Fill(PhiMetJet2,weight)
            dimensional[leptons[lep]['name']]['metvsCosMinDphiMt2llcut']['histo'][s['name']].Fill(cos(PhiMetJet2),met)
            dimensional[leptons[lep]['name']]['metvsMinDphiMt2llcut']['histo'][s['name']].Fill(PhiMetJet2,met)
        
        plots[leptons[lep]['name']]['kinMetSig']['histo'][s["name"]].Fill(met/sqrt(ht), weight)
        plots[leptons[lep]['name']]['met']['histo'][s["name"]].Fill(met, weight)
        bjetspt = filter(lambda j:j['btagCSV']>0.814, jets)
        nobjets = filter(lambda j:j['btagCSV']<=0.814, jets)
        plots[leptons[lep]['name']]['njets']['histo'][s["name"]].Fill(len(jets),weight)
        plots[leptons[lep]['name']]['nbjets']['histo'][s["name"]].Fill(len(bjetspt),weight)
        plots[leptons[lep]['name']]['leadingjetpartonId']['histo'][s["name"]].Fill(getVarValue(chain,"Jet_partonId",0),weight)
        #2 or more bjets: two highest pt
        if len(bjetspt)>=2:
          mt2Calc.setBJets(bjetspt[0]['pt'], bjetspt[0]['eta'], bjetspt[0]['phi'], bjetspt[1]['pt'], bjetspt[1]['eta'], bjetspt[1]['phi'])
        #1 bjets: bjet+jet with highest pt
        if len(bjetspt)==1 and len(nobjets)>0:
          mt2Calc.setBJets(bjetspt[0]['pt'], bjetspt[0]['eta'], bjetspt[0]['phi'], nobjets[0]['pt'], nobjets[0]['eta'], nobjets[0]['phi'])
        if (len(bjetspt)==0) or (len(bjetspt)==1 and len(nobjets)==0): #last one seems necessary if btagCSV is 'nan'
          continue
        mt2bb   = mt2Calc.mt2bb()
        mt2blbl = mt2Calc.mt2blbl()
        plots[leptons[lep]['name']]['mt2bb']['histo'][s["name"]].Fill(mt2bb, weight)
        plots[leptons[lep]['name']]['mt2blbl']['histo'][s["name"]].Fill(mt2blbl, weight)
        #Tree.Fill()
  #TreeFile.Write()
  #TreeFile.Close()
  del eList

#######################################################
#           provide tables from histograms            #
#######################################################
if makelatextables:
  latexmaker(120.,'ee', plots)
  latexmaker(120.,'mumu', plots)
  latexmaker(120.,'emu',plots)


#######################################################
#            make piecharts from histograms           #
#######################################################
if makepiechart:
  piemaker(120.,'ee', plots)



#######################################################
#             Drawing done here                       #
#######################################################
#Some coloring

TTJets_15["color"]=ROOT.kRed
#WJetsHTToLNu["color"]=ROOT.kGreen
#TTH["color"]=ROOT.kMagenta
#TTW["color"]=ROOT.kMagenta-3
#TTZ["color"]=ROOT.kMagenta-6
#singleTop["color"]=ROOT.kOrange
#DY["color"]=ROOT.kBlue
DY_15["color"]=ROOT.kBlue
#Plotvariables
signal = {'path': ["SMS_T2tt_2J_mStop425_mLSP325","SMS_T2tt_2J_mStop500_mLSP325","SMS_T2tt_2J_mStop650_mLSP325","SMS_T2tt_2J_mStop850_mLSP100"], 'name': ["T2tt(425,325)","T2tt(500,325)","T2tt(650,325)","T2tt(850,100)"]}
yminimum = 10**-0.5
legendtextsize = 0.028
signalscaling = 100


if makedraw1D:

  for pk in plots.keys():
    for plot in plots[pk].keys():
      #Make a stack for backgrounds
      l=ROOT.TLegend(0.6,0.8,1.0,1.0)
      l.SetFillColor(0)
      l.SetShadowColor(ROOT.kWhite)
      l.SetBorderSize(1)
      l.SetTextSize(legendtextsize)
      bkg_stack = ROOT.THStack("bkgs","bkgs")
      for b in backgrounds:
        plots[pk][plot]['histo'][b["name"]].SetFillColor(b["color"])
        plots[pk][plot]['histo'][b["name"]].SetMarkerColor(b["color"])
        plots[pk][plot]['histo'][b["name"]].SetMarkerSize(0)
        bkg_stack.Add(plots[pk][plot]['histo'][b["name"]],"h")
        l.AddEntry(plots[pk][plot]['histo'][b["name"]], b["name"])
    
    #Plot!
      c1 = ROOT.TCanvas()
      bkg_stack.SetMaximum(30*bkg_stack.GetMaximum())
      bkg_stack.SetMinimum(yminimum)
      bkg_stack.Draw()
      bkg_stack.GetXaxis().SetTitle(plots[pk][plot]['title'])
      bkg_stack.GetYaxis().SetTitle("Events / %i GeV"%( (plots[pk][plot]['binning'][2]-plots[pk][plot]['binning'][1])/plots[pk][plot]['binning'][0]) )
      c1.SetLogy()
      signalPlot_1 = plots[pk][plot]['histo'][signal['path'][0]].Clone()
      signalPlot_2 = plots[pk][plot]['histo'][signal['path'][2]].Clone()
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
      if plots[pk][plot].has_key('tag'):
        print 'Tag found, adding to histogram'
        channeltag.AddText(plots[pk][plot]['tag'])
      channeltag.SetFillColor(ROOT.kWhite)
      channeltag.SetShadowColor(ROOT.kWhite)
      channeltag.Draw()
      c1.Print(plotDir+"/test/1D/"+plots[pk][plot]['name']+"_"+pk+".png")
    
  for plot in plotsSF['SF'].keys():
    bkg_stack_SF = ROOT.THStack("bkgs_SF","bkgs_SF")
    l=ROOT.TLegend(0.6,0.8,1.0,1.0)
    l.SetFillColor(0)
    l.SetShadowColor(ROOT.kWhite)
    l.SetBorderSize(1)
    l.SetTextSize(legendtextsize)
    for b in backgrounds:
      bkgforstack = plots['ee'][plot]['histo'][b["name"]]
      bkgforstack.Add(plots['mumu'][plot]['histo'][b["name"]])
      bkg_stack_SF.Add(bkgforstack,"h")
      l.AddEntry(bkgforstack, b["name"])
   
    c1 = ROOT.TCanvas()
    bkg_stack_SF.SetMaximum(30*bkg_stack_SF.GetMaximum())
    bkg_stack_SF.SetMinimum(yminimum)
    bkg_stack_SF.Draw()
    bkg_stack_SF.GetXaxis().SetTitle(plotsSF['SF'][plot]['title'])
    bkg_stack_SF.GetYaxis().SetTitle("Events / %i GeV"%( (plotsSF['SF'][plot]['binning'][2]-plotsSF['SF'][plot]['binning'][1])/plotsSF['SF'][plot]['binning'][0]) )
    c1.SetLogy()
    signalPlot_1 = plots['ee'][plot]['histo'][signal['path'][0]].Clone()
    signalPlot_1.Add(plots['mumu'][plot]['histo'][signal['path'][0]])
    signalPlot_2 = plots['ee'][plot]['histo'][signal['path'][2]].Clone()
    signalPlot_2.Add(plots['mumu'][plot]['histo'][signal['path'][2]])
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
    if plotsSF['SF'][plot].has_key('tag'):
      print 'Tag found, adding to histogram'
      channeltag.AddText(plots[pk][plot]['tag'])
    channeltag.SetFillColor(ROOT.kWhite)
    channeltag.SetShadowColor(ROOT.kWhite)
    channeltag.Draw()
    c1.Print(plotDir+"/test/1D/"+plotsSF['SF'][plot]['name']+"_SF.png")

if makedraw2D:

  c1 = ROOT.TCanvas()
  ROOT.gStyle.SetOptStat(0)
  ROOT.gStyle.SetPalette(1)
  c1.SetRightMargin(0.16)
  c1.SetLogz()

  for pk in dimensional.keys():
    for plot in dimensional[pk].keys():
    #Plot!
      for s in backgrounds+signals:
        plot2D = dimensional[pk][plot]['histo'][s["name"]]
        
        plot2D.Draw("colz")
        if plot2D.Integral()==0:continue
        ROOT.gPad.Update()
        palette = plot2D.GetListOfFunctions().FindObject("palette")
        palette.SetX1NDC(0.85)
        palette.SetX2NDC(0.9)
        palette.Draw()
        plot2D.GetXaxis().SetTitle(dimensional[pk][plot]['xtitle'])
        plot2D.GetYaxis().SetTitle(dimensional[pk][plot]['ytitle'])
        
        l=ROOT.TLegend(0.25,0.95,0.9,1.0)
        l.SetFillColor(0)
        l.SetShadowColor(ROOT.kWhite)
        l.SetBorderSize(1)
        l.SetTextSize(legendtextsize)
        l.AddEntry(plot2D,s["name"])
        l.Draw()
        channeltag = ROOT.TPaveText(0.65,0.7,0.8,0.85,"NDC")
        firstlep, secondlep = pk[:len(pk)/2], pk[len(pk)/2:]
        if firstlep == 'mu':
          firstlep = '#' + firstlep
        if secondlep == 'mu':
          secondlep = '#' + secondlep
        channeltag.AddText(firstlep+secondlep)
        if s in signals:
          index = signal['path'].index(s["name"])
          channeltag.AddText(signal["name"][index])
        if s in backgrounds:
          channeltag.AddText(s["name"])
        if dimensional[pk][plot].has_key('tag'):
          print 'Tag found, adding to histogram'
          channeltag.AddText(dimensional[pk][plot]['tag'])
        channeltag.SetFillColor(ROOT.kWhite)
        channeltag.SetShadowColor(ROOT.kWhite)
        channeltag.Draw()
        
        c1.Print(plotDir+"/test/2D/"+dimensionalSF[pk][plot]['name']+"/"+dimensionalSF[pk][plot]['name']+"_"+pk+"_"+s['name']+".png")
        c1.Clear()
  
  for pk in dimensionalSF.keys():
    for plot in dimensionalSF[pk].keys():
      for s in backgrounds+signals:
        plot2DSF = dimensional['ee'][plot]['histo'][s["name"]]
        plot2DSF.Add(dimensional['mumu'][plot]['histo'][s["name"]])
        
        plot2DSF.Draw("colz")
        if plot2DSF.Integral()==0:continue
        ROOT.gPad.Update()
        palette = plot2DSF.GetListOfFunctions().FindObject("palette")
        palette.SetX1NDC(0.85)
        palette.SetX2NDC(0.9)
        palette.Draw()
        plot2DSF.GetXaxis().SetTitle(dimensionalSF[pk][plot]['xtitle'])
        plot2DSF.GetYaxis().SetTitle(dimensionalSF[pk][plot]['ytitle'])
        
        l=ROOT.TLegend(0.25,0.95,0.9,1.0)
        l.SetFillColor(0)
        l.SetShadowColor(ROOT.kWhite)
        l.SetBorderSize(1)
        l.SetTextSize(legendtextsize)
        l.AddEntry(plot2DSF,s["name"])
        l.Draw()
        channeltag = ROOT.TPaveText(0.65,0.7,0.8,0.85,"NDC")
        channeltag.AddText("SF")
        if s in signals:
          index = signal['path'].index(s["name"])
          channeltag.AddText(signal["name"][index])
        if s in backgrounds:
          channeltag.AddText(s["name"])
        if dimensionalSF['SF'][plot].has_key('tag'):
          print 'Tag found, adding to histogram'
          channeltag.AddText(dimensionalSF[pk][plot]['tag'])
        channeltag.SetFillColor(ROOT.kWhite)
        channeltag.SetShadowColor(ROOT.kWhite)
        channeltag.Draw()
        
        c1.Print(plotDir+"/test/2D/"+dimensionalSF[pk][plot]['name']+"/"+dimensionalSF[pk][plot]['name']+"_"+pk+"_"+s['name']+".png")
        c1.Clear()
