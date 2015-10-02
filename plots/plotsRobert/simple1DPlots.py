import ROOT
from array import array
from math import cos,sin,sqrt,cosh,pi
import os, copy, sys

ROOT.TH1F().SetDefaultSumw2()

small = False
from StopsDilepton.samples.cmgTuples_Spring15_50ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_Spring15_25ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data50ns_1l_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_postProcessed import *
from StopsDilepton.tools.objectSelection import getLeptons, getMuons, getElectrons, getGoodMuons, getGoodElectrons, getGoodLeptons, mZ
from Workspace.RA4Analysis.simplePlotHelpers import plot, stack, loopAndFill, drawNMStacks
from optparse import OptionParser
parser = OptionParser()
parser.add_option("--mode", dest="mode", default="doubleMu", type="string", action="store", help="doubleMu, doubleEle, eleMu")
parser.add_option("--zMode", dest="zMode", default="None", type="string", action="store", help="onZ, offZ, None")
#parser.add_option("--small", dest="small", default = False, action="store_true", help="small")
parser.add_option("--OS", dest="OS", default = False, action="store_true", help="require OS?")

(options, args) = parser.parse_args()

cutBranches = ["weight", "leptonPt", "met*", \
               'Jet_pt', "Jet_id", "Jet_eta", "Jet_btagCSV",
               "LepGood_pdgId", "LepGood_mediumMuonId", "LepGood_miniRelIso", "LepGood_sip3d", "LepGood_dxy", "LepGood_dz", "LepGood_convVeto", "LepGood_lostHits",
               "Flag_HBHENoiseFilter", "Flag_HBHENoiseIsoFilter", "Flag_HBHENoiseFilterMinZeroPatched", "Flag_goodVertices", "Flag_CSCTightHaloFilter", "Flag_eeBadScFilter",
               "HLT_mumuIso", "HLT_ee_DZ", "HLT_mue",
               "is*","dl_*"
                ]
subdir = "/png50ns_2l/"

prefix = '_'.join([options.mode, options.zMode]) 

filterCut = "(Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_goodVertices&&Flag_CSCTightHaloFilter&&Flag_eeBadScFilter)"
#filterCut = "(Flag_HBHENoiseFilterMinZeroPatched&&Flag_goodVertices&&Flag_CSCTightHaloFilter&&Flag_eeBadScFilter)"
#filterCut = "(1)"

#nMu = "Sum$(abs(LepGood_pdgId)==13&&LepGood_mediumMuonId==1&&LepGood_miniRelIso<0.1&&LepGood_sip3d<4.0&&abs(LepGood_dxy)<0.05&&abs(LepGood_dz)<0.1)"
#nEle = "Sum$(abs(LepGood_pdgId)==11&&LepGood_convVeto==1&&LepGood_miniRelIso<0.2&&LepGood_sip3d<4.0&&abs(LepGood_dxy)<0.05&&abs(LepGood_dz)<0.1&&LepGood_lostHits==0)"
triggerMuMu = "HLT_mumuIso"
triggerEleEle = "HLT_ee_DZ"
triggerMuEle = "HLT_mue"

preselCuts = ["((Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))>=2)"]
if options.OS : preselCuts.append("isOS")

def getZCut(mode):
  zstr = "abs(dl_mass - "+str(mZ)+")"
  if mode=="onZ": return zstr+"<15"
  if mode=="offZ": return zstr+">15"
  return "(1)"

if options.mode=="doubleMu":
  presel = "&&".join(["isMuMu==1", getZCut(options.zMode)] + preselCuts)
  dataCut = "&&".join([triggerMuMu, filterCut])
  dataSample = DoubleMuon_Run2015D
if options.mode=="doubleEle":
  presel = "&&".join(["isEE==1", getZCut(options.zMode)] + preselCuts)
  dataCut = "&&".join([triggerEleEle, filterCut])
  dataSample = DoubleEG_Run2015D
if options.mode=="muEle":
  presel = "&&".join(["isEMu==1", getZCut(options.zMode)] + preselCuts)
  dataCut = "&&".join([triggerMuEle, filterCut])
  dataSample = MuonEG_Run2015D

lumiScaleFac = dataSample["lumi"]/1000.

cutString=presel

cutFunc=None

ratioOps = {'yLabel':'Data/MC', 'numIndex':1, 'denIndex':0 ,'yRange':None, 'logY':False, 'color':ROOT.kBlack, 'yRange':(0.1, 2.1)}

def getStack(labels, var, binning, cut, options={}):

  style_Data         = {'legendText':'Single Muon',      'style':"e", 'lineThickness':0, 'errorBars':True, 'color':ROOT.kBlack, 'markerStyle':20, 'markerSize':1}

  style_WJets        = {'legendText':'W + Jets',         'style':"f", 'lineThickness':0, 'errorBars':False, 'color':42, 'markerStyle':None, 'markerSize':None}
  style_TTJets       = {'legendText':'t#bar{t} + Jets',  'style':"f", 'linethickNess':0, 'errorBars':False, 'color':7, 'markerStyle':None, 'markerSize':None}

  style_DY           = {'legendText':'DY + Jets',  'style':"f", 'linethickNess':0, 'errorBars':False,       'color':8, 'markerStyle':None, 'markerSize':None}
#  style_TTVH         = {'legendText':'t#bar{t} + W/Z/H',  'style':"f", 'linethickNess':0, 'errorBars':False, 'color':color("TTVH"), 'markerStyle':None, 'markerSize':None}
  style_QCD          = {'legendText':'QCD',  'style':"f", 'linethickNess':0, 'errorBars':False,             'color':46, 'markerStyle':None, 'markerSize':None}
  style_singleTop    = {'legendText':'single top',  'style':"f", 'linethickNess':0, 'errorBars':False,      'color':40, 'markerStyle':None, 'markerSize':None}
  
  data               = plot(var, binning, cut, sample=dataSample,       style=style_Data)
  MC_TTJets          = plot(var, binning, cut, sample=TTJets_50ns,       style=style_TTJets, weight={'string':'weight'})
  MC_WJetsToLNu      = plot(var, binning, cut, sample=WJetsToLNu_50ns,   style=style_WJets, weight={'string':'weight'})
  MC_DY              = plot(var, binning, cut, sample=DY_50ns,           style=style_DY, weight={'string':'weight'})
#  MC_TTVH            = plot(var, binning, cut, sample=TTVH,       style=style_TTVH, weight={'string':'weight'})
  MC_singleTop       = plot(var, binning, cut, sample=singleTop_50ns,    style=style_singleTop, weight={'string':'weight'})
  MC_QCD             = plot(var, binning, cut, sample=QCDMu_50ns,        style=style_QCD, weight={'string':'weight'})

  mcStack = [MC_TTJets, MC_DY,  MC_QCD, MC_singleTop, MC_WJetsToLNu]
#  mcStack = []
  for s in mcStack:
    s.sample['scale'] = lumiScaleFac

  plotLists = [mcStack, [data]]

  for pL in plotLists:
    for p in pL:
      p.sample['small']=small

  opt = {'small':small, 'yHeadRoomFac':12, 'labels':labels, 'logX':False, 'logY':True, 'yRange':[0.11, "auto"], 'ratio':ratioOps, 'fileName':var['name']}
#  opt = {'small':small, 'yHeadRoomFac':12, 'labels':labels, 'logX':False, 'logY':True, 'yRange':[0.11, "auto"], 'ratio':None, 'fileName':var['name']}

  if opt.has_key('ratio') and opt['ratio']:
    opt['texLines'] = [{'pos':(0.15, 0.95),'text':'CMS Preliminary', 'options':{'size':0.052}},\
                       {'pos':(0.7, 0.95), 'text':'L='+str(dataSample['lumi'])+' pb{}^{-1} (13 TeV)', 'options':{'size':0.052}}]
    opt['legend'] = {'coordinates':[0.55,0.90 - len(mcStack)*0.05,.98,.93],'boxed':True}
  else:
    opt['texLines'] = [{'pos':(0.16, 0.965), 'text':'CMS Preliminary',       'options':{'size':0.038}},\
                       {'pos':(0.7, 0.965),  'text':'L='+str(dataSample['lumi'])+' pb{}^{-1} (13 TeV)','options':{'size':0.038}}]
    opt['legend'] = {'coordinates':[0.55,0.90 - len(mcStack)*0.05,.98,.95],'boxed':True}

  opt.update(options)
  res = stack(plotLists, options = opt)
  res.usedBranches = cutBranches
  return res

allStacks=[]

dl_mass_stack  = getStack(
    labels={'x':'m(ll) (GeV)','y':'Number of Events / 5 GeV'},
#    var={'name':'mll','func':mll, 'overFlow':'upper', 'branches':[]},
    var={'name':'dl_mass','leaf':"dl_mass", 'overFlow':'upper', 'branches':[]},
    binning={'binning':[100/5,50,150]},
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
    binning={'binning':[20,0,400]},
    cut={'string':cutString,'func':cutFunc,'dataCut':dataCut},
    )
allStacks.append(dl_mt2ll_stack)
dl_mt2bb_stack  = getStack(
    labels={'x':'MT_{2}^{bb} (GeV)','y':'Number of Events / 20 GeV'},
#    var={'name':'mll','func':mll, 'overFlow':'upper', 'branches':[]},
    var={'name':'dl_mt2bb','leaf':"dl_mt2bb", 'overFlow':'upper', 'branches':[]},
    binning={'binning':[20,0,400]},
    cut={'string':cutString,'func':cutFunc,'dataCut':dataCut},
    )
allStacks.append(dl_mt2bb_stack)
dl_mt2blbl_stack  = getStack(
    labels={'x':'MT_{2}^{blbl} (GeV)','y':'Number of Events / 20 GeV'},
#    var={'name':'mll','func':mll, 'overFlow':'upper', 'branches':[]},
    var={'name':'dl_mt2blbl','leaf':"dl_mt2blbl", 'overFlow':'upper', 'branches':[]},
    binning={'binning':[20,0,400]},
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

met_stack  = getStack(
    labels={'x':'#slash{E}_{T} (GeV)','y':'Number of Events / 50 GeV'},
    var={'name':'met','leaf':'met', 'overFlow':'upper'},
    binning={'binning':[1050/50,0,1050]},
    cut={'string':cutString,'func':cutFunc,'dataCut':dataCut},
    )
allStacks.append(met_stack)

ht_stack  = getStack(
    labels={'x':'H_{T} (GeV)','y':'Number of Events / 100 GeV'},
#    var={'name':'ht','leaf':'htJet40ja', 'overFlow':'upper'},
    var={'name':'ht','TTreeFormula':'Sum$(Jet_pt*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))', 'overFlow':'upper'},
    binning={'binning':[2600/100,0,2600]},
    cut={'string':cutString,'func':cutFunc, 'dataCut':dataCut})
allStacks.append(ht_stack)

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

nbtags_stack  = getStack(
    labels={'x':'number of b-tags (CSVM)','y':'Number of Events'},
    var={'name':'nBTags','TTreeFormula':"Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.890)", 'overFlow':'upper'},
    binning={'binning':[8,0,8]},
    cut={'string':cutString,'func':cutFunc, 'dataCut':dataCut})
allStacks.append(nbtags_stack)

njets_stack  = getStack(
    labels={'x':'number of jets','y':'Number of Events'},
    var={'name':'njets','TTreeFormula':'Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)', 'overFlow':'upper'},
    binning={'binning':[14,0,14]},
    cut={'string':cutString,'func':cutFunc, 'dataCut':dataCut})
allStacks.append(njets_stack)

nVert_stack  = getStack(
    labels={'x':'vertex multiplicity','y':'Number of Events'},
    var={'name':'nVert','leaf':"nVert", 'overFlow':'upper'},
    binning={'binning':[50,0,50]},
    cut={'string':cutString,'func':cutFunc, 'dataCut':dataCut})
allStacks.append(nVert_stack)

loopAndFill(allStacks)

stuff=[]
for stk in allStacks:
  stuff.append(drawNMStacks(1,1,[stk],         subdir+prefix+"_"+stk.options['fileName']))
