from optparse import OptionParser
parser = OptionParser()
parser.add_option("--mode", dest="mode", default="doubleMu", type="string", action="store", help="doubleMu, doubleEle, muEle")
parser.add_option("--zMode", dest="zMode", default="onZ", type="string", action="store", help="onZ, offZ, allZ")
#parser.add_option("--small", dest="small", default = False, action="store_true", help="small")
#parser.add_option("--OS", dest="OS", default = True, action="store_true", help="require OS?")

(options, args) = parser.parse_args()

import ROOT
ROOT.TH1F().SetDefaultSumw2()
from array import array
from math import cos,sin,sqrt,cosh,pi
import os, copy, sys
import itertools

small = False
from StopsDilepton.samples.cmgTuples_Spring15_50ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_Spring15_25ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data50ns_1l_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_postProcessed import *
from StopsDilepton.tools.objectSelection import getLeptons, getMuons, getElectrons, getGoodMuons, getGoodElectrons, getGoodLeptons, mZ
from StopsDilepton.tools.helpers import getVarValue, getYieldFromChain, getChain
from StopsDilepton.tools.localInfo import plotDir
from simplePlotHelpers import plot, stack, loopAndFill, drawNMStacks
from StopsDilepton.tools.puReweighting import getReweightingFunction

puReweightingFunc = getReweightingFunction(era="Run2015D_205pb")
#puReweightingFunc = getReweightingFunction(era="Run2015D_205pb_doubleMu_onZ_isOS")
puReweighting = lambda c:puReweightingFunc(getVarValue(c, "nVert"))

cutBranches = ["weight", "leptonPt", "met*", "nVert",\
               'Jet_pt', "Jet_id", "Jet_eta", "Jet_phi", "Jet_btagCSV",
               "LepGood_pdgId", "LepGood_mediumMuonId", "LepGood_miniRelIso", "LepGood_sip3d", "LepGood_dxy", "LepGood_dz", "LepGood_convVeto", "LepGood_lostHits",
               "Flag_HBHENoiseFilter", "Flag_HBHENoiseIsoFilter", "Flag_HBHENoiseFilterMinZeroPatched", "Flag_goodVertices", "Flag_CSCTightHaloFilter", "Flag_eeBadScFilter",
               "HLT_mumuIso", "HLT_ee_DZ", "HLT_mue",
               "is*","dl_*","l1_*","l2_*", "nGoodMuons", "nGoodElectrons"
                ]
subdir = "png25ns_2l"
#preprefixes = ["PUDoubleMuOnZIsOS"]
preprefixes = []

def getZCut(mode):
  zstr = "abs(dl_mass - "+str(mZ)+")"
  if mode.lower()=="onz": return zstr+"<15"
  if mode.lower()=="offz": return zstr+">15"
  return "(1)"

#filterCut = "(Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_goodVertices&&Flag_CSCTightHaloFilter&&Flag_eeBadScFilter)"
filterCut = "(Flag_HBHENoiseFilterMinZeroPatched&&Flag_goodVertices&&Flag_CSCTightHaloFilter&&Flag_eeBadScFilter)"
#filterCut = "(1)"

#nMu = "Sum$(abs(LepGood_pdgId)==13&&LepGood_mediumMuonId==1&&LepGood_miniRelIso<0.1&&LepGood_sip3d<4.0&&abs(LepGood_dxy)<0.05&&abs(LepGood_dz)<0.1)"
#nEle = "Sum$(abs(LepGood_pdgId)==11&&LepGood_convVeto==1&&LepGood_miniRelIso<0.2&&LepGood_sip3d<4.0&&abs(LepGood_dxy)<0.05&&abs(LepGood_dz)<0.1&&LepGood_lostHits==0)"
triggerMuMu = "HLT_mumuIso"
triggerEleEle = "HLT_ee_DZ"
triggerMuEle = "HLT_mue"

cuts=[
 ("njet2", "(Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))>=2"),
 ("nbtag1", "Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.890)>=1"),
 ("mll20", "dl_mass>20"),
# ("met80", "met_pt>80"),
# ("metSig5", "met_pt/sqrt(Sum$(Jet_pt*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)))>5"),
# ("dPhiJet0-dPhiJet1", "cos(met_phi-Jet_phi[0])<cos(0.25)&&cos(met_phi-Jet_phi[1])<cos(0.25)"),
  ]
for i in range(len(cuts)+1):
#for i in reversed(range(len(cuts)+1)):
  for comb in itertools.combinations(cuts,i):
#    presel = [("isOS","isOS"), ("mRelIso01", "LepGood_miniRelIso[l1_index]<0.1&&LepGood_miniRelIso[l2_index]<0.1")]
    presel = [("isOS","isOS")]
    presel.extend( comb )

    prefix = '_'.join(preprefixes+[options.mode, options.zMode, '-'.join([p[0] for p in presel])]) 
    preselCuts = [p[1] for p in presel]

    if options.mode=="doubleMu":
      cutString = "&&".join(["isMuMu==1&&nGoodMuons==2&&nGoodElectrons==0", getZCut(options.zMode)] + preselCuts)
      dataCut = "&&".join([triggerMuMu, filterCut])
      dataSample = DoubleMuon_Run2015D
    if options.mode=="doubleEle":
      cutString = "&&".join(["isEE==1&&nGoodMuons==0&&nGoodElectrons==2", getZCut(options.zMode)] + preselCuts)
      dataCut = "&&".join([triggerEleEle, filterCut])
      dataSample = DoubleEG_Run2015D
    if options.mode=="muEle":
      cutString = "&&".join(["isEMu==1&&nGoodMuons==1&&nGoodElectrons==1", getZCut(options.zMode)] + preselCuts)
      dataCut = "&&".join([triggerMuEle, filterCut])
      dataSample = MuonEG_Run2015D

    cutFunc = None
    lumiScaleFac = dataSample["lumi"]/1000.
    backgrounds = [TTLep_25ns, WJetsToLNu_25ns, DY_25ns, singleTop_25ns, QCDMu_25ns]
    data = getYieldFromChain(getChain(dataSample,histname=""), cutString = "&&".join([cutString, dataCut]), weight='weight') 
    bkg  = 0. 
    for s in backgrounds:
      bkg+= getYieldFromChain(getChain(s,histname=""), cutString, weight='weight')

    scaleFac = data/(bkg*lumiScaleFac)

    print "After lumiscale %3.3f there is bkg %7.1f and data %7.1f: re-normalizing scaleFac by %3.3f"%(lumiScaleFac, lumiScaleFac*bkg, data, scaleFac)
     
    ratioOps = {'yLabel':'Data/MC', 'numIndex':1, 'denIndex':0 ,'yRange':None, 'logY':False, 'color':ROOT.kBlack, 'yRange':(0.1, 2.1)}
    #ratioOps = None

    def getStack(labels, var, binning, cut, options={}):

      style_Data         = {'legendText':dataSample['name'],      'style':"e", 'lineThickness':0, 'errorBars':True, 'color':ROOT.kBlack, 'markerStyle':20, 'markerSize':1}
      style_WJets        = {'legendText':'W + Jets',         'style':"f", 'lineThickness':0, 'errorBars':False, 'color':42, 'markerStyle':None, 'markerSize':None}
      style_TTJets       = {'legendText':'t#bar{t} + Jets',  'style':"f", 'linethickNess':0, 'errorBars':False, 'color':7, 'markerStyle':None, 'markerSize':None}
      style_DY           = {'legendText':'DY + Jets',  'style':"f", 'linethickNess':0, 'errorBars':False,       'color':8, 'markerStyle':None, 'markerSize':None}
      style_TTX          = {'legendText':'t#bar{t} + W/Z/H',  'style':"f", 'linethickNess':0, 'errorBars':False, 'color':ROOT.kYellow+2, 'markerStyle':None, 'markerSize':None}
      style_diBoson         = {'legendText':'WW/WZ/ZZ',  'style':"f", 'linethickNess':0, 'errorBars':False, 'color':ROOT.kGreen-5, 'markerStyle':None, 'markerSize':None}
      style_QCD          = {'legendText':'QCD',  'style':"f", 'linethickNess':0, 'errorBars':False,             'color':46, 'markerStyle':None, 'markerSize':None}
      style_singleTop    = {'legendText':'single top',  'style':"f", 'linethickNess':0, 'errorBars':False,      'color':40, 'markerStyle':None, 'markerSize':None}
      
      data               = plot(var, binning, cut, sample=dataSample,       style=style_Data)
      MC_TTJets          = plot(var, binning, cut, sample=TTLep_25ns,       style=style_TTJets,    weightString="weight", weightFunc=puReweighting)
      MC_WJetsToLNu      = plot(var, binning, cut, sample=WJetsToLNu_25ns,   style=style_WJets,     weightString="weight", weightFunc=puReweighting)
      MC_DY              = plot(var, binning, cut, sample=DY_25ns,           style=style_DY,        weightString="weight", weightFunc=puReweighting)
      MC_singleTop       = plot(var, binning, cut, sample=singleTop_25ns,    style=style_singleTop, weightString="weight", weightFunc=puReweighting)
      MC_QCD             = plot(var, binning, cut, sample=QCDMu_25ns,        style=style_QCD,       weightString="weight", weightFunc=puReweighting)
      MC_TTX             = plot(var, binning, cut, sample=TTX_25ns,          style=style_TTX, weightString="weight", weightFunc=puReweighting)
      MC_diBoson         = plot(var, binning, cut, sample=diBosons_25ns,     style=style_diBoson, weightString="weight", weightFunc=puReweighting)

      mcStack = [MC_TTJets, MC_DY,  MC_QCD, MC_singleTop, MC_WJetsToLNu, MC_diBoson, MC_TTX]
      for s in mcStack:
    #    print s,s.sample
        s.sample['scale'] = lumiScaleFac*scaleFac

      plotLists = [mcStack, [data]]
#      plotLists = [mcStack]

      for pL in plotLists:
        for p in pL:
          p.sample['small']=small

      opt = {'small':small, 'yHeadRoomFac':12, 'labels':labels, 'logX':False, 'logY':True, 'yRange':[0.11, "auto"], 'ratio':ratioOps, 'fileName':var['name']}
    #  opt = {'small':small, 'yHeadRoomFac':12, 'labels':labels, 'logX':False, 'logY':True, 'yRange':[0.11, "auto"], 'ratio':None, 'fileName':var['name']}

      if opt.has_key('ratio') and opt['ratio']:
        opt['texLines'] = [{'pos':(0.15, 0.95),'text':'CMS Preliminary', 'options':{'size':0.052}},\
                           {'pos':(0.47, 0.95), 'text':'L='+str(dataSample['lumi'])+' pb{}^{-1} (13 TeV) Scale %3.2f'%scaleFac, 'options':{'size':0.052}}]
        opt['legend'] = {'coordinates':[0.55,0.90 - len(mcStack)*0.05,.98,.93],'boxed':True}
      else:
        opt['texLines'] = [{'pos':(0.16, 0.965), 'text':'CMS Preliminary',       'options':{'size':0.038}},\
                           {'pos':(0.47, 0.965),  'text':'L='+str(dataSample['lumi'])+' pb{}^{-1} (13 TeV) Scale %3.2f'%scaleFac,'options':{'size':0.038}}]
        opt['legend'] = {'coordinates':[0.55,0.90 - len(mcStack)*0.05,.98,.95],'boxed':True}

      opt.update(options)
      res = stack(plotLists, options = opt)
      res.usedBranches = cutBranches
      return res

    allStacks=[]

    dl_mass_stack  = getStack(
        labels={'x':'m(ll) (GeV)','y':'Number of Events / 3 GeV'},
    #    var={'name':'mll','func':mll, 'overFlow':'upper', 'branches':[]},
        var={'name':'dl_mass','leaf':"dl_mass", 'overFlow':'upper', 'branches':[]},
        binning={'binning':[150/3,0,150]},
        cut={'string':cutString,'func':cutFunc,'dataCut':dataCut},
        )
    allStacks.append(dl_mass_stack)

    dl_pt_stack  = getStack(
        labels={'x':'p_{T}(ll) (GeV)','y':'Number of Events / 10 GeV'},
    #    var={'name':'mll','func':mll, 'overFlow':'upper', 'branches':[]},
        var={'name':'dl_pt','leaf':"dl_pt", 'overFlow':'upper', 'branches':[]},
        binning={'binning':[40,0,400]},
        cut={'string':cutString,'func':cutFunc,'dataCut':dataCut},
        )
    allStacks.append(dl_pt_stack)

    dl_eta_stack  = getStack(
        labels={'x':'#eta(ll) ','y':'Number of Events'},
    #    var={'name':'mll','func':mll, 'overFlow':'upper', 'branches':[]},
        var={'name':'dl_eta','leaf':"dl_eta", 'overFlow':'upper', 'branches':[]},
        binning={'binning':[30,-3,3]},
        cut={'string':cutString,'func':cutFunc,'dataCut':dataCut},
        )
    allStacks.append(dl_eta_stack)

    dl_phi_stack  = getStack(
        labels={'x':'#phi(ll) (GeV)','y':'Number of Events'},
    #    var={'name':'mll','func':mll, 'overFlow':'upper', 'branches':[]},
        var={'name':'dl_phi','leaf':"dl_phi", 'overFlow':'upper', 'branches':[]},
        binning={'binning':[30,-pi,pi]},
        cut={'string':cutString,'func':cutFunc,'dataCut':dataCut},
        )
    allStacks.append(dl_phi_stack)

    dl_mt2ll_stack  = getStack(
        labels={'x':'MT_{2}^{ll} (GeV)','y':'Number of Events / 20 GeV'},
    #    var={'name':'mll','func':mll, 'overFlow':'upper', 'branches':[]},
        var={'name':'dl_mt2ll','leaf':"dl_mt2ll", 'overFlow':'upper', 'branches':[]},
        binning={'binning':[300/20,0,300]},
        cut={'string':cutString,'func':cutFunc,'dataCut':dataCut},
        )
    allStacks.append(dl_mt2ll_stack)
    dl_mt2bb_stack  = getStack(
        labels={'x':'MT_{2}^{bb} (GeV)','y':'Number of Events / 20 GeV'},
    #    var={'name':'mll','func':mll, 'overFlow':'upper', 'branches':[]},
        var={'name':'dl_mt2bb','leaf':"dl_mt2bb", 'overFlow':'upper', 'branches':[]},
        binning={'binning':[(400-80)/20,80,400]},
        cut={'string':cutString,'func':cutFunc,'dataCut':dataCut},
        )
    allStacks.append(dl_mt2bb_stack)
    dl_mt2blbl_stack  = getStack(
        labels={'x':'MT_{2}^{blbl} (GeV)','y':'Number of Events / 20 GeV'},
    #    var={'name':'mll','func':mll, 'overFlow':'upper', 'branches':[]},
        var={'name':'dl_mt2blbl','leaf':"dl_mt2blbl", 'overFlow':'upper', 'branches':[]},
        binning={'binning':[300/20,0,300]},
        cut={'string':cutString,'func':cutFunc,'dataCut':dataCut},
        )
    allStacks.append(dl_mt2blbl_stack)

    dl_mtautau_stack  = getStack(
        labels={'x':'m_{#tau#tau} (GeV)','y':'Number of Events / 5 GeV'},
    #    var={'name':'mll','func':mll, 'overFlow':'upper', 'branches':[]},
        var={'name':'dl_mtautau','leaf':"dl_mtautau", 'overFlow':'upper', 'branches':[]},
        binning={'binning':[20,0,400]},
        cut={'string':cutString,'func':cutFunc,'dataCut':dataCut},
        )
    allStacks.append(dl_mtautau_stack)

    l1_pt_stack  = getStack(
        labels={'x':'p_{T}(l_{1}) (GeV)','y':'Number of Events / 5 GeV'},
    #    var={'name':'mll','func':mll, 'overFlow':'upper', 'branches':[]},
        var={'name':'l1_pt','leaf':"l1_pt", 'overFlow':'upper', 'branches':[]},
        binning={'binning':[60,0,300]},
        cut={'string':cutString,'func':cutFunc,'dataCut':dataCut},
        )
    allStacks.append(l1_pt_stack)
    l1_eta_stack  = getStack(
        labels={'x':'#eta(l_{1})','y':'Number of Events'},
        var={'name':'l1_eta','leaf':"l1_eta", 'overFlow':'upper', 'branches':[]},
        binning={'binning':[36,-3.3,3.3]},
        cut={'string':cutString,'func':cutFunc,'dataCut':dataCut},
        )
    allStacks.append(l1_eta_stack)
    l1_phi_stack  = getStack(
        labels={'x':'#phi(l_{1})','y':'Number of Events'},
        var={'name':'l1_phi','leaf':"l1_phi", 'overFlow':'upper', 'branches':[]},
        binning={'binning':[30,-pi,pi]},
        cut={'string':cutString,'func':cutFunc,'dataCut':dataCut},
        )
    allStacks.append(l1_phi_stack)
    l1_pdgId_stack  = getStack(
        labels={'x':'pdgId(l_{1})','y':'Number of Events'},
        var={'name':'l1_pdgId','leaf':"l1_pdgId", 'overFlow':'upper', 'branches':[]},
        binning={'binning':[32,-16,16]},
        cut={'string':cutString,'func':cutFunc,'dataCut':dataCut},
        )
    allStacks.append(l1_pdgId_stack)
    l2_pt_stack  = getStack(
        labels={'x':'p_{T}(l_{1}) (GeV)','y':'Number of Events / 5 GeV'},
    #    var={'name':'mll','func':mll, 'overFlow':'upper', 'branches':[]},
        var={'name':'l2_pt','leaf':"l2_pt", 'overFlow':'upper', 'branches':[]},
        binning={'binning':[60,0,300]},
        cut={'string':cutString,'func':cutFunc,'dataCut':dataCut},
        )
    allStacks.append(l2_pt_stack)
    l2_eta_stack  = getStack(
        labels={'x':'#eta(l_{1})','y':'Number of Events'},
        var={'name':'l2_eta','leaf':"l2_eta", 'overFlow':'upper', 'branches':[]},
        binning={'binning':[30,-3,3]},
        cut={'string':cutString,'func':cutFunc,'dataCut':dataCut},
        )
    allStacks.append(l2_eta_stack)
    l2_phi_stack  = getStack(
        labels={'x':'#phi(l_{1})','y':'Number of Events'},
        var={'name':'l2_phi','leaf':"l2_phi", 'overFlow':'upper', 'branches':[]},
        binning={'binning':[30,-pi,pi]},
        cut={'string':cutString,'func':cutFunc,'dataCut':dataCut},
        )
    allStacks.append(l2_phi_stack)
    l2_pdgId_stack  = getStack(
        labels={'x':'pdgId(l_{1})','y':'Number of Events'},
        var={'name':'l2_pdgId','leaf':"l2_pdgId", 'overFlow':'upper', 'branches':[]},
        binning={'binning':[32,-16,16]},
        cut={'string':cutString,'func':cutFunc,'dataCut':dataCut},
        )
    allStacks.append(l2_pdgId_stack)

    metZoomed_stack  = getStack(
        labels={'x':'#slash{E}_{T} (GeV)','y':'Number of Events / 10 GeV'},
        var={'name':'metZoomed','leaf':'met_pt', 'overFlow':'upper'},
        binning={'binning':[22,0,220]},
        cut={'string':cutString,'func':cutFunc,'dataCut':dataCut},
        )
    allStacks.append(metZoomed_stack)

    met_stack  = getStack(
        labels={'x':'#slash{E}_{T} (GeV)','y':'Number of Events / 50 GeV'},
        var={'name':'met','leaf':'met_pt', 'overFlow':'upper'},
        binning={'binning':[1050/50,0,1050]},
        cut={'string':cutString,'func':cutFunc,'dataCut':dataCut},
        )
    allStacks.append(met_stack)

    metSig_stack  = getStack(
        labels={'x':'#slash{E}_{T}/#sqrt(H_{T}) (GeV^{1/2})','y':'Number of Events / 100 GeV'},
    #    var={'name':'ht','leaf':'htJet40ja', 'overFlow':'upper'},
        var={'name':'metSig','TTreeFormula':'met_pt/sqrt(Sum$(Jet_pt*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)))', 'overFlow':'upper'},
        binning={'binning':[20,0,20]},
        cut={'string':cutString,'func':cutFunc, 'dataCut':dataCut})
    allStacks.append(metSig_stack)

    ht_stack  = getStack(
        labels={'x':'H_{T} (GeV)','y':'Number of Events / 100 GeV'},
    #    var={'name':'ht','leaf':'htJet40ja', 'overFlow':'upper'},
        var={'name':'ht','TTreeFormula':'Sum$(Jet_pt*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))', 'overFlow':'upper'},
        binning={'binning':[2600/100,0,2600]},
        cut={'string':cutString,'func':cutFunc, 'dataCut':dataCut})
    allStacks.append(ht_stack)

    ht_zoomed_stack  = getStack(
        labels={'x':'H_{T} (GeV)','y':'Number of Events / 30 GeV'},
    #    var={'name':'ht_zoomed','leaf':'ht_zoomedJet40ja', 'overFlow':'upper'},
        var={'name':'ht_zoomed','TTreeFormula':'Sum$(Jet_pt*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))', 'overFlow':'upper'},
        binning={'binning':[390/15,0,390]},
        cut={'string':cutString,'func':cutFunc, 'dataCut':dataCut})
    allStacks.append(ht_zoomed_stack)

    cosMetJet0phi_stack  = getStack(
        labels={'x':'Cos(#phi(#slash{E}_{T}, Jet[0]))','y':'Number of Events'},
    #    var={'name':'mll','func':mll, 'overFlow':'upper', 'branches':[]},
        var={'name':'cosMetJet0phi','TTreeFormula':"cos(met_phi-Jet_phi[0])", 'overFlow':'upper', 'branches':[]},
        binning={'binning':[30,-1,1]},
        cut={'string':cutString,'func':cutFunc,'dataCut':dataCut},
        )
    allStacks.append(cosMetJet0phi_stack)

    cosMetJet1phi_stack  = getStack(
        labels={'x':'Cos(#phi(#slash{E}_{T}, Jet[1]))','y':'Number of Events'},
    #    var={'name':'mll','func':mll, 'overFlow':'upper', 'branches':[]},
        var={'name':'cosMetJet1phi','TTreeFormula':"cos(met_phi-Jet_phi[1])", 'overFlow':'upper', 'branches':[]},
        binning={'binning':[30,-1,1]},
        cut={'string':cutString,'func':cutFunc,'dataCut':dataCut},
        )
    allStacks.append(cosMetJet1phi_stack)

    lepGood_pt0_stack  = getStack(
        labels={'x':'p_{T}(l) (GeV)','y':'Number of Events / 25 GeV'},
        var={'name':'LepGood_pt0','leaf':'LepGood_pt','ind':0, 'overFlow':'upper'},
        binning={'binning':[975/25,0,975]},
        cut={'string':cutString,'func':cutFunc, 'dataCut':dataCut})
    allStacks.append(lepGood_pt0_stack)


    jet0pt_stack  = getStack(
        labels={'x':'p_{T}(leading jet) (GeV)','y':'Number of Events / 20 GeV'},
        var={'name':'jet0pt','leaf':'Jet_pt','ind':0, 'overFlow':'upper'},
        binning={'binning':[980/20,0,980]},
        cut={'string':cutString,'func':cutFunc, 'dataCut':dataCut})
    allStacks.append(jet0pt_stack)
    jet1pt_stack  = getStack(
        labels={'x':'p_{T}(2^{nd.} leading jet) (GeV)','y':'Number of Events / 20 GeV'},
        var={'name':'jet1pt','leaf':'Jet_pt','ind':1, 'overFlow':'upper'},
        binning={'binning':[980/20,0,980]},
        cut={'string':cutString,'func':cutFunc, 'dataCut':dataCut})
    allStacks.append(jet1pt_stack)
    jet2pt_stack  = getStack(
        labels={'x':'p_{T}(3^{rd.} leading jet) (GeV)','y':'Number of Events / 20 GeV'},
        var={'name':'jet2pt','leaf':'Jet_pt','ind':2, 'overFlow':'upper'},
        binning={'binning':[400/20,0,400]},
        cut={'string':cutString,'func':cutFunc, 'dataCut':dataCut})
    allStacks.append(jet2pt_stack)
    jet3pt_stack  = getStack(
        labels={'x':'p_{T}(4^{th.} leading jet) (GeV)','y':'Number of Events / 20 GeV'},
        var={'name':'jet3pt','leaf':'Jet_pt','ind':3, 'overFlow':'upper'},
        binning={'binning':[400/20,0,400]},
        cut={'string':cutString,'func':cutFunc, 'dataCut':dataCut})
    allStacks.append(jet3pt_stack)
    jet4pt_stack  = getStack(
        labels={'x':'p_{T}(5^{th.} leading jet) (GeV)','y':'Number of Events / 20 GeV'},
        var={'name':'jet4pt','leaf':'Jet_pt','ind':4, 'overFlow':'upper'},
        binning={'binning':[400/20,0,400]},
        cut={'string':cutString,'func':cutFunc, 'dataCut':dataCut})
    allStacks.append(jet4pt_stack)

#    nbtags_stack  = getStack(
#        labels={'x':'number of b-tags (CSVM)','y':'Number of Events'},
#        var={'name':'nBTags','TTreeFormula':"Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.890)", 'overFlow':'upper'},
#        binning={'binning':[8,0,8]},
#        cut={'string':cutString,'func':cutFunc, 'dataCut':dataCut})
#    allStacks.append(nbtags_stack)
#
#    njets_stack  = getStack(
#        labels={'x':'number of jets','y':'Number of Events'},
#        var={'name':'njets','TTreeFormula':'Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)', 'overFlow':'upper'},
#        binning={'binning':[14,0,14]},
#        cut={'string':cutString,'func':cutFunc, 'dataCut':dataCut})
#    allStacks.append(njets_stack)
#
#    nVert_stack  = getStack(
#        labels={'x':'vertex multiplicity','y':'Number of Events'},
#        var={'name':'nVert','leaf':"nVert", 'overFlow':'upper'},
#        binning={'binning':[50,0,50]},
#        cut={'string':cutString,'func':cutFunc, 'dataCut':dataCut})
#    allStacks.append(nVert_stack)

    loopAndFill(allStacks)

    path = '/'.join([plotDir, subdir, prefix])
    print "path",path
    if not os.path.exists(path): os.makedirs(path)
    stuff=[]
    for stk in allStacks:
      stuff.append(drawNMStacks(1,1,[stk], path=path, filename=stk.options['fileName']))

    ROOT.gDirectory.GetListOfFiles().ls()

