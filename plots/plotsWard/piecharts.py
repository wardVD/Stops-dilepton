import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()
import numpy
from pylab import *
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from math import *

from StopsDilepton.tools.helpers import getChain, getObjDict, getEList, getVarValue, genmatching, latexmaker, piemaker, getWeight
from StopsDilepton.tools.objectSelection import getLeptons, looseMuID, looseEleID, getJets, getGenParts
from StopsDilepton.tools.localInfo import *
from StopsDilepton.tools.mt2Calculator import mt2Calculator
mt2Calc = mt2Calculator()


#preselection: MET>40, njets>=2, n_bjets>=1, n_lep>=2
#For now see here for the Sum$ syntax: https://root.cern.ch/root/html/TTree.html#TTree:Draw@2
preselection = 'met_pt>40&&Sum$(LepGood_pt>20)==2'


#######################################################
#        SELECT WHAT YOU WANT TO DO HERE              #
#######################################################
reduceStat = 1 #recude the statistics, i.e. 10 is ten times less samples to look at

#######################################################
#                 load all the samples                #
#######################################################
from StopsDilepton.samples.cmgTuples_Spring15_50ns_postProcessed import *
backgrounds = [singleTop_50ns,QCDMu_50ns,DY_50ns,TTJets_50ns]
#signals = [SMS_T2tt_2J_mStop425_mLSP325, SMS_T2tt_2J_mStop500_mLSP325, SMS_T2tt_2J_mStop650_mLSP325, SMS_T2tt_2J_mStop850_mLSP100]
signals = []


#######################################################
#            get the TChains for each sample          #
#######################################################
for s in backgrounds+signals:
  s['chain'] = getChain(s,histname="")


#######################################################
#         Define piecharts you want to make           #
#######################################################
piechart = {\
  "OF":{\
    "(0,0)" :{},
    "(1,0)" :{},
    "(1,1)" :{},
    "(>=2,0)" :{},
    "(>=2,>=1)" :{},
    },
  "SF":{\
    "(0,0)" :{},
    "(1,0)" :{},
    "(1,1)" :{},
    "(>=2,0)" :{},
    "(>=2,>=1)" :{},
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
    if ev%10000==0:print "At ", 100*ev/nEvents, "%"
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
    nlep = len(allLeptons)

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
          
          twoleptons = True
          l0pt, l0eta, l0phi = leptons[lep]['file'][0]['pt'],  leptons[lep]['file'][0]['eta'],  leptons[lep]['file'][0]['phi']
          l1pt, l1eta, l1phi = leptons[lep]['file'][1]['pt'],  leptons[lep]['file'][1]['eta'],  leptons[lep]['file'][1]['phi']
          leadingleptonpt = l0pt
          subleadingleptonpt = l1pt
          mll = sqrt(2.*l0pt*l1pt*(cosh(l0eta-l1eta)-cos(l0phi-l1phi)))
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
          zveto = False
      if (twoleptons and mll>20 and not zveto) or (twoleptons and mll > 20 and zveto and abs(mll-90.2)>15):
        mt2Calc.setMet(met,metPhi)
        mt2Calc.setLeptons(l0pt, l0eta, l0phi, l1pt, l1eta, l1phi)        
        mt2ll = mt2Calc.mt2ll()
        jets = filter(lambda j:j['pt']>30 and abs(j['eta'])<2.4 and j['id'], getJets(chain))
        ht = sum([j['pt'] for j in jets])
        bjetspt = filter(lambda j:j['btagCSV']>0.814, jets)
        nobjets = filter(lambda j:j['btagCSV']<0.814, jets)
        njets = len(jets)
        nbjets = len(bjetspt)
        nmuons = len(muons)
        nelectrons = len(electrons)

        if mt2ll < 100: continue

        if (nmuons == 1 and nelectrons == 1):

          if njets == 0: 
            if nbjets == 0:
              piechart["OF"]["(0,0)"][s["name"]]+=1
          elif njets == 1:
            if nbjets == 0: 
              piechart["OF"]["(1,0)"][s["name"]]+=1
            elif nbjets == 1: 
              piechart["OF"]["(1,1)"][s["name"]]+=1
          elif njets >= 2:
            if nbjets == 0: 
              piechart["OF"]["(>=2,0)"][s["name"]]+=1
            else: 
              piechart["OF"]["(>=2,>=1)"][s["name"]]+=1
        else:
          if njets == 0:
            if nbjets == 0:
              piechart["SF"]["(0,0)"][s["name"]]+=1
          elif njets == 1:
            if nbjets == 0: 
              piechart["SF"]["(1,0)"][s["name"]]+=1
            elif nbjets == 1: 
              piechart["SF"]["(1,1)"][s["name"]]+=1
          elif njets >= 2:
            if nbjets == 0: 
              piechart["SF"]["(>=2,0)"][s["name"]]+=1
            else: 
              piechart["SF"]["(>=2,>=1)"][s["name"]]+=1

  del eList


def makefigure(piechart):

    fig1 = plt.figure(figsize=(10,10))
    gridx=len(piechart["SF"])+1
    gridy=4  #jet multiplicity, SF and OF and add one for legend
    colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral']
    colors = colors[:len(piechart["SF"])]
    for ikey,key in enumerate(piechart.keys()):
        plt.subplot(gridx,gridy,ikey+2)
        plt.text(0.5,0.5,key,fontsize=20)
        plt.axis("off")
        k = ikey+6
        for icolumn,column in enumerate(sorted(piechart[key].keys())):
            if ikey == 0:
                plt.subplot(gridx,gridy,k-1)
                plt.text(0.5,0.5,column,fontsize=15)
                plt.axis('off')
            bkgs = [i for i,j in (piechart[key][column]).iteritems()]
            bkgrates = [j for i,j in (piechart[key][column]).iteritems()]
            if k%gridy==0: k+=1
            plt.subplot(gridx,gridy,k)
            plt.pie(bkgrates,colors=colors,autopct='%1.1f%%')
            plt.axis('equal')
            k+=4

    plt.subplot(gridx,gridy,gridy+4)
    
    yellowgreen_patch = mpatches.Patch(color="yellowgreen",label=bkgs[0])
    gold_patch = mpatches.Patch(color="gold",label=bkgs[1])
    lightskyblue_patch = mpatches.Patch(color="lightskyblue",label=bkgs[2])
    lightcoral_patch = mpatches.Patch(color="lightcoral",label=bkgs[3])

    plt.legend([yellowgreen_patch,gold_patch,lightskyblue_patch,lightcoral_patch],bkgs)
    plt.axis('off')
    plt.savefig('piecharts.png')



makefigure(piechart)
