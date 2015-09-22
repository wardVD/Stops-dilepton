from StopsDilepton.tools.helpers import getVarValue, getObjDict
from math import *

mZ=90.2
   
def getJets(c):
  return [getObjDict(c, 'Jet_', ['eta','pt','phi','btagCMVA','btagCSV', 'id'], i) for i in range(int(getVarValue(c, 'nJet')))]

def getGoodJets(c):
  return filter(lambda j:j['pt']>30 and abs(j['eta'])<2.4 and j['id'], getJets(c))

def getGoodBJets(c):
  return filter(lambda j:j['btagCSV']>0.890, getGoodJets(c))

def getGenLeps(c):
  return [getObjDict(c, 'genLep_', ['eta','pt','phi','charge', 'pdgId', 'sourceId'], i) for i in range(int(getVarValue(c, 'ngenLep')))]

def getGenParts(c):
  return [getObjDict(c, 'GenPart_', ['eta','pt','phi','charge', 'pdgId', 'motherId', 'grandmotherId'], i) for i in range(int(getVarValue(c, 'nGenPart')))]

def getGenPartsAll(c):
  return [getObjDict(c, 'genPartAll_', ['eta','pt','phi','charge', 'pdgId', 'motherId', 'grandmotherId'], i) for i in range(int(getVarValue(c, 'ngenPartAll')))]

def looseMuID(l, ptCut=20, absEtaCut=2.4):
  return \
    l["pt"]>=ptCut\
    and abs(l["pdgId"])==13\
    and abs(l["eta"])<absEtaCut\
    and l["mediumMuonId"]==1 \
    and l["miniRelIso"]<0.2 \
    and l["sip3d"]<4.0\
    and l["dxy"]<0.05\
    and l["dz"]<0.1\

def cmgMVAEleID(l,mva_cuts):
  aeta = abs(l["eta"])
  for abs_e, mva in mva_cuts.iteritems():
    if aeta>=abs_e[0] and aeta<abs_e[1] and l["mvaIdPhys14"] >mva: return True
  return False
  
ele_MVAID_cuts_loose = {(0,0.8):0.35 , (0.8, 1.44):0.20, (1.57, 999): -0.52}
ele_MVAID_cuts_vloose = {(0,0.8):-0.11 , (0.8, 1.44):-0.35, (1.57, 999): -0.55}
ele_MVAID_cuts_tight = {(0,0.8):0.73 , (0.8, 1.44):0.57, (1.57, 999):  0.05}

def looseEleID(l, ptCut=20, absEtaCut=2.4):
  return \
    l["pt"]>=ptCut\
    and abs(l["eta"])<absEtaCut\
    and abs(l["pdgId"])==11\
    and cmgMVAEleID(l, ele_MVAID_cuts_loose)\
    and l["miniRelIso"]<0.2\
    and l["convVeto"]\
    and l["lostHits"]==0\
    and l["sip3d"] < 4.0\
    and l["dxy"] < 0.05\
    and l["dz"] < 0.1\

def getLeptons(c):
  return [getObjDict(c, 'LepGood_', ['eta','pt','phi','charge', 'dxy', 'dz','mass', 'relIso03','tightId', 'pdgId', 'mediumMuonId', 'miniRelIso', 'sip3d', 'mvaIdPhys14', 'convVeto', 'lostHits'], i) for i in range(int(getVarValue(c, 'nLepGood')))]
def getMuons(c):
  return [getObjDict(c, 'LepGood_', ['eta','pt','phi','charge', 'dxy', 'dz', 'relIso03','tightId', 'pdgId', 'mediumMuonId', 'miniRelIso', 'sip3d', 'mvaIdPhys14', 'convVeto', 'lostHits'], i) for i in range(int(getVarValue(c, 'nLepGood'))) if abs(getVarValue(c,"LepGood_pdgId",i))==13]
def getElectrons(c):
  return [getObjDict(c, 'LepGood_', ['eta','pt','phi','charge', 'dxy', 'dz', 'relIso03','tightId', 'pdgId', 'mediumMuonId', 'miniRelIso', 'sip3d', 'mvaIdPhys14', 'convVeto', 'lostHits'], i) for i in range(int(getVarValue(c, 'nLepGood'))) if abs(getVarValue(c,"LepGood_pdgId",i))==11]
def getGoodMuons(c):
  return [l for l in getMuons(c) if looseMuID(l)]
def getGoodElectrons(c):
  return [l for l in getElectrons(c) if looseEleID(l)]
def getGoodLeptons(c):
  return [l for l in getLeptons(c) if (abs(l["pdgId"])==11 and looseEleID(l)) or (abs(l["pdgId"])==13 and looseMuID(l))]
def m_ll(l1,l2):
  return sqrt(2.*l1['pt']*l2['pt']*(cosh(l1['eta']-l2['eta']) - cos(l1['phi']-l2['phi'])))
def pt_ll(l1,l2):
  return sqrt((l1['pt']*cos(l1['phi']) + l2['pt']*cos(l2['phi']))**2 + (l1['pt']*sin(l1['phi']) + l2['pt']*sin(l2['phi']))**2)
