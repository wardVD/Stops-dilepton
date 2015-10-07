import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()

import ROOT
from ROOT import TTree, TFile, AddressOf, gROOT
from array import array
import numpy as n

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


preselectionMC = 'Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.890)>=1&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2&&Sum$(LepGood_pt>20)==2'
preselectionData = 'Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.890)>=1&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2&&Sum$(LepGood_pt>20)==2&&Flag_goodVertices&&Flag_CSCTightHaloFilter&&Flag_eeBadScFilter&&Flag_HBHENoiseFilterMinZeroPatched'


prefix="def"
reduceStat = 1
lumiScale = 1.

#load all the samples
from StopsDilepton.samples.cmgTuples_Spring15_25ns_postProcessed import *

backgrounds = [diBosons_25ns,WJetsToLNu_25ns,singleTop_25ns,QCDMu_25ns,DYHT_25ns,TTJets_25ns]
#backgrounds = [TTJets_25ns] 
for b in backgrounds:
  b['isData']=0

signals = [SMS_T2tt_2J_mStop425_mLSP325, SMS_T2tt_2J_mStop500_mLSP325, SMS_T2tt_2J_mStop650_mLSP325, SMS_T2tt_2J_mStop850_mLSP100]
#signals = [SMS_T2tt_2J_mStop425_mLSP325] 
for s in signals:
  s['isData']=0

data = [DoubleEG_25ns,DoubleMuon_25ns,MuonEG_25ns]
for d in data:
  d['isData']=1

#get the TChains for each sample
for s in backgrounds+signals+data:
  s['chain'] = getChain(s,histname="")

for s in backgrounds+signals+data:
#for s in signals+data: 

  fout = TFile(s["name"]+'.root','RECREATE')
  t = TTree('anaTree','Tree of variables')

  MET 		 			= n.zeros(1, dtype=float)
  METPhi 		 		= n.zeros(1, dtype=float)
  ptLeadingJet 			= n.zeros(1, dtype=float)
  ptSubLeadingJet 		= n.zeros(1, dtype=float)
  ptLeadingLepton 		= n.zeros(1, dtype=float)
  ptSubLeadingLepton 	= n.zeros(1, dtype=float)
  mt2ll 				= n.zeros(1, dtype=float)
  mt2bb 				= n.zeros(1, dtype=float)
  mt2blbl 				= n.zeros(1, dtype=float)
  HT 					= n.zeros(1, dtype=float)
  dileptonInvariantMass	= n.zeros(1, dtype=float)
  xsecWeight 			= n.zeros(1, dtype=float)
  pileupWeight 			= n.zeros(1, dtype=float)
  nbjets 				= n.zeros(1, dtype=int)
  njets	 				= n.zeros(1, dtype=int)
  nleptons 				= n.zeros(1, dtype=int)
  nVertices 			= n.zeros(1, dtype=int)
  isMC 					= n.zeros(1, dtype=int)
  isElecElec 			= n.zeros(1, dtype=int)
  isMuonMuon 			= n.zeros(1, dtype=int)
  isMuonElec 			= n.zeros(1, dtype=int)
  Process 				= bytearray(200)


  lepton1 = ROOT.TLorentzVector()
  lepton2 = ROOT.TLorentzVector()
  jet1 = ROOT.TLorentzVector()
  jet2 = ROOT.TLorentzVector()
  bjet1 = ROOT.TLorentzVector()
  bjet2 = ROOT.TLorentzVector()

  t.Branch("MET", MET, "MET/D")
  t.Branch("METPhi", METPhi, "METPhi/D")
  t.Branch("ptLeadingJet", ptLeadingJet, "ptLeadingJet/D")
  t.Branch("ptSubLeadingJet", ptSubLeadingJet, "ptSubLeadingJet/D")
  t.Branch("ptLeadingLepton", ptLeadingLepton, "ptLeadingLepton/D")
  t.Branch("ptSubLeadingLepton", ptSubLeadingLepton, "ptSubLeadingLepton/D")
  t.Branch("mt2ll", mt2ll, "mt2ll/D")
  t.Branch("mt2bb", mt2bb, "mt2bb/D")
  t.Branch("mt2blbl", mt2blbl, "mt2blbl/D")
  t.Branch("HT", HT, "HT/D")
  t.Branch("dileptonInvariantMass", dileptonInvariantMass, "dileptonInvariantMass/D")
  t.Branch("xsecWeight", xsecWeight, "xsecWeight/D")
  t.Branch("pileupWeight", pileupWeight, "pileupWeight/D")
  t.Branch("nbjets", nbjets, "nbjets/I")
  t.Branch("njets", njets, "njets/I")
  t.Branch("nleptons", nleptons, "nleptons/I")
  t.Branch("nVertices", nVertices, "nVertices/I")
  t.Branch("isMC", isMC, "isMC/I")
  t.Branch("isElecElec", isElecElec, "isElecElec/I")
  t.Branch("isMuonMuon", isMuonMuon, "isMuonMuon/I")
  t.Branch("isMuonElec", isMuonElec, "isMuonElec/I")
  t.Branch("LeadingLepton","TLorentzVector",lepton1)
  t.Branch("SubLeadingLepton","TLorentzVector",lepton2)
  t.Branch("LeadingBJet","TLorentzVector",bjet1)
  t.Branch("SubLeadingBJet","TLorentzVector",bjet2)
  t.Branch("LeadingJet","TLorentzVector",jet1)
  t.Branch("SubLeadingJet","TLorentzVector",jet2)
  t.Branch('Process', Process, 'Process[200]/C')


  chain = s["chain"]
  print "Looping over %s" % s["name"]

  if s['isData']==0:
   eList = getEList(chain, preselectionMC) 
   nEvents = eList.GetN()/reduceStat
   print "Found %i events in %s after preselection %s, looping over %i" % (eList.GetN(),s["name"],preselectionMC,nEvents)

  else:
   eList = getEList(chain, preselectionData) 
   nEvents = eList.GetN()/reduceStat
   print "Found %i events in %s after preselection %s, looping over %i" % (eList.GetN(),s["name"],preselectionData,nEvents)


  for ev in range(nEvents):
    if ev%10000==0:print "At %i/%i"%(ev,nEvents)
    chain.GetEntry(eList.GetEntry(ev))

    mt2Calc.reset()
    weight = reduceStat*getVarValue(chain, "weight")*lumiScale if not s['isData'] else 1

    met = getVarValue(chain, "met_pt")
    metPhi = getVarValue(chain, "met_phi")
    metEta = getVarValue(chain, "met_eta")
    mt2ll[0] = 0
    mt2bb[0] = 0
    mt2blbl[0] = 0
    MET[0] = met 
    METPhi[0] = metPhi 
    xsecWeight[0] = weight
    pileupWeight[0] = getVarValue(chain,"puWeight")
    isMC[0] = 1-s['isData']
    isElecElec[0] = 0 
    isMuonMuon[0] = 0 
    isMuonElec[0] = 0 

    triggerMuMu = getVarValue(chain,"HLT_mumuIso")
    triggerEleEle = getVarValue(chain,"HLT_ee_DZ")
    triggerMuEle = getVarValue(chain,"HLT_mue")
    trigger = 0

    if s['isData'] == 0:
      trigger = 1
    if not s["name"].find("DoubleEG") and triggerEleEle :
      trigger = 1
    if not s["name"].find("DoubleEG") and triggerEleEle==0 :
      trigger = 0
    if not s["name"].find("DoubleMuon") and triggerMuMu :
      trigger = 1
    if not s["name"].find("DoubleMuon") and triggerMuMu==0 :
      trigger = 0
    if not s["name"].find("MuonEG") and triggerMuEle :
      trigger = 1
    if not s["name"].find("MuonEG") and triggerMuEle==0 :
      trigger = 0
    

    leptons = filter(lambda l: looseMuID(l) or looseEleID(l), getLeptons(chain))
    jets = filter(lambda j:j['pt']>30 and abs(j['eta'])<2.4 and j['id'], getJets(chain))
    bjets = filter(lambda j:j['btagCSV']>0.890, jets)

    nbjets[0] = len(bjets)
    njets[0] = len(jets)
    nleptons[0] = len(leptons)
    Process[:200] = s["name"]

    if len(leptons)==2: 
 
      ## OF SF choice 
      if leptons[0]['pdgId']+leptons[1]['pdgId']==0 and abs(leptons[0]['pdgId'])==11:
          isElecElec[0] = 1
      if leptons[0]['pdgId']+leptons[1]['pdgId']==0 and abs(leptons[0]['pdgId'])==13:
          isMuonMuon[0] = 1
      if abs(leptons[0]['pdgId'])+abs(leptons[1]['pdgId'])==24: 
          isMuonElec[0] = 1


      l0pt, l0eta, l0phi, l0mass = leptons[0]['pt'],  leptons[0]['eta'],  leptons[0]['phi'],  leptons[0]['mass']
      l1pt, l1eta, l1phi, l1mass = leptons[1]['pt'],  leptons[1]['eta'],  leptons[1]['phi'],  leptons[1]['mass'] 
      mll = sqrt(2.*l0pt*l1pt*(cosh(l0eta-l1eta)-cos(l0phi-l1phi)))

      dileptonInvariantMass[0] = mll
      ptLeadingLepton[0] = l0pt 
      ptSubLeadingLepton[0] = l1pt

      lepton1.SetPtEtaPhiM(l0pt, l0eta, l0phi, l0mass)
      lepton2.SetPtEtaPhiM(l1pt, l1eta, l1phi, l1mass)

      lepton1.SetPtEtaPhiM(l0pt, l0eta, l0phi, l0mass)
      lepton2.SetPtEtaPhiM(l1pt, l1eta, l1phi, l1mass)


      l0pt, l0eta, l0phi, l0mass = leptons[0]['pt'],  leptons[0]['eta'],  leptons[0]['phi'],  leptons[0]['mass']
      if len(bjets)==2:
        mt2Calc.setMet(met,metPhi)
        mt2Calc.setLeptons(l0pt, l0eta, l0phi, l1pt, l1eta, l1phi)
        mt2ll[0] = mt2Calc.mt2ll()
        HT[0] = sum([j['pt'] for j in jets])
        mt2Calc.setBJets(bjets[0]['pt'], bjets[0]['eta'], bjets[0]['phi'], bjets[1]['pt'], bjets[1]['eta'], bjets[1]['phi'])
        mt2bb[0]   = mt2Calc.mt2bb()
        mt2blbl[0] = mt2Calc.mt2blbl()

  
  if  nbjets[0]>0 and nleptons[0]==2 and njets[0]>1 and trigger==1:  

    t.Fill()


  del eList

  fout.Write()
  fout.Close()


## Change name of root files
os.system("mv DoubleMuon.root ntuples/DoubleMuon.root")
os.system("mv DoubleEG.root ntuples/DoubleElec.root")
os.system("mv MuonEG.root ntuples/MuonElec.root")
os.system("mv SMS_T2tt_2J_mStop425_mLSP325.root ntuples/T2ttS425N325.root")
os.system("mv SMS_T2tt_2J_mStop500_mLSP325.root ntuples/T2ttS500N325.root")
os.system("mv SMS_T2tt_2J_mStop650_mLSP325.root ntuples/T2ttS650N325.root")
os.system("mv SMS_T2tt_2J_mStop850_mLSP100.root ntuples/T2ttS850N100.root")
os.system("mv DY.root ntuples/DrellYan.root")
os.system("mv QCD (MuPt5 enriched).root ntuples/QCDMu.root")
os.system("mv tt+Jets.root ntuples/TTJets.root")
os.system("mv WW+WZ+ZZ.root ntuples/DiBosons.root")
os.system("mv W+Jets.root ntuples/WJets.root")
os.system("mv singletop.root ntuples/singleTop.root")
