from StopsDilepton.tools.helpers import getVarValue, getObjDict
from math import *
   
def getJets(c):
  return [getObjDict(c, 'Jet_', ['eta','pt','phi','btagCMVA','btagCSV','mcMatchFlav' ,'partonId', 'id'], i) for i in range(int(getVarValue(c, 'nJet')))]

def getGenLeps(c):
  return [getObjDict(c, 'genLep_', ['eta','pt','phi','charge', 'pdgId', 'sourceId'], i) for i in range(int(getVarValue(c, 'ngenLep')))]

def getGenParts(c):
  return [getObjDict(c, 'GenPart_', ['eta','pt','phi','charge', 'pdgId', 'motherId', 'grandmotherId'], i) for i in range(int(getVarValue(c, 'nGenPart')))]

def getGenPartsAll(c):
  return [getObjDict(c, 'genPartAll_', ['eta','pt','phi','charge', 'pdgId', 'motherId', 'grandmotherId'], i) for i in range(int(getVarValue(c, 'ngenPartAll')))]

#def getLeptons(c):
#  return [getObjDict(c, 'LepGood_', ['eta','pt','phi','charge', 'dxy', 'dz', 'relIso03','tightId', 'pdgId', 'mediumMuonId', 'eleMVAId', 'miniRelIso', 'sip3d', 'mvaIdPhys14', 'convVeto', 'lostHits'], i) for i in range(int(getVarValue(c, 'nLepGood')))]

def getLeptons(c):
  return [getObjDict(c, 'LepGood_', ['eta','pt','phi','charge', 'dxy', 'dz', 'relIso03','tightId', 'pdgId', 'mediumMuonId', 'miniRelIso', 'sip3d', 'mvaIdPhys14', 'convVeto', 'lostHits'], i) for i in range(int(getVarValue(c, 'nLepGood')))]

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

#def mvaIDPhys14(l):
#  if abs(l["eta"]) < 0.8 and l["mvaIdPhys14"] > 0.73 : return True
#  #elif abs(l["eta"]) >= 0.8 and abs(l["eta"]) < 1.44 and l["mvaIdPhys14"] > 0.57 : return True
#  #elif abs(l["eta"]) > 1.57 and l["mvaIdPhys14"]  > 0.05 : return True
#  elif abs(l["eta"]) >= 0.8 and abs(l["eta"]) < 1.479 and l["mvaIdPhys14"] > 0.57 : return True
#  elif abs(l["eta"]) > 1.479 and l["mvaIdPhys14"]  > 0.05 : return True
#  else: return False

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


