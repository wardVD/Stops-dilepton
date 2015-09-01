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
preselection = 'met_pt>40&&Sum$(LepGood_pt>20)>=2'


#######################################################
#        SELECT WHAT YOU WANT TO DO HERE              #
#######################################################
reduceStat = 100 #recude the statistics, i.e. 10 is ten times less samples to look at

#######################################################
#                 load all the samples                #
#######################################################
from StopsDilepton.samples.cmgTuplesPostProcessed_PHYS14 import *
#backgrounds = [WJetsHTToLNu, TTH, TTW, TTZ, DYWARD, singleTop, TTJets]#, QCD]
backgrounds = [TTH]
#signals = [SMS_T2tt_2J_mStop425_mLSP325, SMS_T2tt_2J_mStop500_mLSP325, SMS_T2tt_2J_mStop650_mLSP325, SMS_T2tt_2J_mStop850_mLSP100]
signals = []


#######################################################
#            get the TChains for each sample          #
#######################################################
for s in backgrounds+signals:
  if s==DYWARD: s['chain'] = getChain(s,histname="",treeName="tree")
  else:         s['chain'] = getChain(s,histname="")


#######################################################
#         Define piecharts you want to make           #
#######################################################
piechart = {\
  "OF":{\
    "njets_0_bjets_0" :{},
    "njets_1_bjets_0" :{},
    "njets_1_bjets_1" :{},
    "njets_2andmore_bjets_0" :{},
    "njets_2andmore_bjets_1andmore" :{},
    },
  "SF":{\
    "njets_0_bjets_0" :{},
    "njets_1_bjets_0" :{},
    "njets_1_bjets_1" :{},
    "njets_2andmore_bjets_0" :{},
    "njets_2andmore_bjets_1andmore" :{},
    }
}


#######################################################
#            Start filling in the histograms          #
#######################################################
for s in backgrounds+signals:
  for flavor in piechart.keys():
    for piece in piechart[flavor].keys():
      piechart[flavor][piece][s["name"]] = 0
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
    #Leptons 
    allLeptons = getLeptons(chain) 
    muons = filter(looseMuID, allLeptons)    
    electrons = filter(looseEleID, allLeptons)
    nlep = len(allLeptons)
    nmuons = len(muons)
    nelectrons = len(electrons)

    jets = filter(lambda j:j['pt']>30 and abs(j['eta'])<2.4 and j['id'], getJets(chain))
    ht = sum([j['pt'] for j in jets])
    bjetspt = filter(lambda j:j['btagCSV']>0.814, jets)
    nobjets = filter(lambda j:j['btagCSV']<0.814, jets)
    njets = len(jets)
    nbjets = len(bjetspt)

    if nmuons+nelectrons != 2: continue
    if (nmuons == 1 and nelectrons == 1):
      if njets == 0: 
        piechart["OF"]["njets_0_bjets_0"][s["name"]]+=1
      elif njets == 1:
        if nbjets == 0: 
          piechart["OF"]["njets_1_bjets_0"][s["name"]]+=1
        else: 
          piechart["OF"]["njets_1_bjets_1"][s["name"]]+=1
      elif njets > 1:
        if nbjets == 0: 
          piechart["OF"]["njets_2andmore_bjets_0"][s["name"]]+=1
        else: 
          piechart["OF"]["njets_2andmore_bjets_1andmore"][s["name"]]+=1
    else:
      if njets == 0: 
        piechart["SF"]["njets_0_bjets_0"][s["name"]]+=1
      elif njets == 1:
        if nbjets == 0: 
          piechart["SF"]["njets_1_bjets_0"][s["name"]]+=1
        else: 
          piechart["SF"]["njets_1_bjets_1"][s["name"]]+=1
      elif njets > 1:
        if nbjets == 0: 
          piechart["SF"]["njets_2andmore_bjets_0"][s["name"]]+=1
        else: 
          piechart["SF"]["njets_2andmore_bjets_1andmore"][s["name"]]+=1

  del eList

file = open("text.txt",w)
hiernogvalalles


for keys in piechart.keys():
  for otherkeys in piechart[keys]:
    
#######################################################
#            make piecharts from histograms           #
#######################################################
piemaker(120.,piechart)

