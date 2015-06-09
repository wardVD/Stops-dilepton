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

def getLeptons(c):
  return [getObjDict(c, 'LepGood_', ['eta','pt','phi','charge', 'dxy', 'dz', 'relIso03','tightId', 'pdgId', 'mediumMuonId', 'eleMVAId', 'miniRelIso', 'sip3d', 'mvaIdPhys14', 'convVeto', 'lostHits'], i) for i in range(int(getVarValue(c, 'nLepGood')))]
#  return filter(lambda m:abs(m['pdgId'])==13, res)

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

def mvaIDPhys14(l):
  if abs(l["eta"]) < 0.8 and l["mvaIdPhys14"] > 0.73 : return True
  #elif abs(l["eta"]) >= 0.8 and abs(l["eta"]) < 1.44 and l["mvaIdPhys14"] > 0.57 : return True
  #elif abs(l["eta"]) > 1.57 and l["mvaIdPhys14"]  > 0.05 : return True
  elif abs(l["eta"]) >= 0.8 and abs(l["eta"]) < 1.479 and l["mvaIdPhys14"] > 0.57 : return True
  elif abs(l["eta"]) > 1.479 and l["mvaIdPhys14"]  > 0.05 : return True
  else: return False

def looseEleID(l, ptCut=20, absEtaCut=2.4):
  return \
    l["pt"]>=ptCut\
    and abs(l["eta"])<absEtaCut\
    and abs(l["pdgId"])==11\
    and mvaIDPhys14(l)\
    and l["miniRelIso"]<0.2\
    and l["convVeto"]\
    and l["lostHits"]==0\
    and l["sip3d"] < 4.0\
    and l["dxy"] < 0.05\
    and l["dz"] < 0.1\

#def looseEleID(l, ptCut=20, absEtaCut=2.4):
#  return \
#    abs(l["pdgId"])==11\
#    and l["eleMVAId"]==1 and l["miniRelIso"]<0.4 and l["sip3d"]<4.0\
#    and l["pt"]>=ptCut and abs(l["eta"])<absEtaCut

def ele_ID_eta(r,nLep,ele_MVAID_cuts):
  if abs(r.LepGood_eta[nLep]) < 0.8 and r.LepGood_mvaIdPhys14[nLep] > ele_MVAID_cuts['eta08'] : return True
  elif abs(r.LepGood_eta[nLep]) > 0.8 and abs(r.LepGood_eta[nLep]) < 1.44 and r.LepGood_mvaIdPhys14[nLep] > ele_MVAID_cuts['eta104'] : return True
  elif abs(r.LepGood_eta[nLep]) > 1.57 and r.LepGood_mvaIdPhys14[nLep] > ele_MVAID_cuts['eta204'] : return True
  return False

def cmgLooseEleID(r, nLep, ptCut , absEtaCut, ele_MVAID_cuts):
  return r.LepGood_pt[nLep]>=ptCut and (abs(r.LepGood_eta[nLep])<1.44 or abs(r.LepGood_eta[nLep])>1.57) and abs(r.LepGood_eta[nLep])<absEtaCut and r.LepGood_miniRelIso[nLep]<0.4 and ele_ID_eta(r,nLep,ele_MVAID_cuts) and r.LepGood_lostHits[nLep]<=1 and r.LepGood_convVeto[nLep] and r.LepGood_sip3d[nLep] < 4.0 

#def ele_ID_eta(r,nLep,ele_MVAID_cuts):
#  if abs(r.LepGood_eta[nLep]) < 0.8 and r.LepGood_mvaIdPhys14[nLep] > ele_MVAID_cuts['eta08'] : return True
#  elif abs(r.LepGood_eta[nLep]) > 0.8 and abs(r.LepGood_eta[nLep]) < 1.44 and r.LepGood_mvaIdPhys14[nLep] > ele_MVAID_cuts['eta104'] : return True
#  elif abs(r.LepGood_eta[nLep]) > 1.57 and r.LepGood_mvaIdPhys14[nLep] > ele_MVAID_cuts['eta204'] : return True
#  return False
#  
#def cmgLooseMuID(r, nLep, ptCut, absEtaCut):
#  return r.LepGood_mediumMuonId[nLep]==1 and r.LepGood_miniRelIso[nLep]<0.4 and r.LepGood_sip3d[nLep]<4.0 and r.LepGood_pt[nLep]>=ptCut and abs(r.LepGood_eta[nLep])<absEtaCut
#
#def cmgLooseEleID(r, nLep, ptCut , absEtaCut, ele_MVAID_cuts):
#  return r.LepGood_pt[nLep]>=ptCut and (abs(r.LepGood_eta[nLep])<1.44 or abs(r.LepGood_eta[nLep])>1.57) and abs(r.LepGood_eta[nLep])<absEtaCut and r.LepGood_miniRelIso[nLep]<0.4 and ele_ID_eta(r,nLep,ele_MVAID_cuts) and r.LepGood_lostHits[nLep]<=1 and r.LepGood_convVeto[nLep] and r.LepGood_sip3d[nLep] < 4.0 
#
#def cmgLooseLepID(r, nLep, ptCuts, absEtaCuts, ele_MVAID_cuts):
#  if abs(r.LepGood_pdgId[nLep])==11: return cmgLooseEleID(r, nLep=nLep, ptCut=ptCuts[0], absEtaCut=absEtaCuts[0], ele_MVAID_cuts=ele_MVAID_cuts)
#  elif abs(r.LepGood_pdgId[nLep])==13: return cmgLooseMuID(r, nLep=nLep, ptCut=ptCuts[1], absEtaCut=absEtaCuts[1])
#
#def cmgLooseLepIndices(r, ptCuts=(7.,5.), absEtaCuts=(2.5,2.4),ele_MVAID_cuts = {'eta08':0.35 , 'eta104':0.20,'eta204': -0.52} , nMax=8):
#  return [i for i in range(min(nMax, r.nLepGood)) if cmgLooseLepID(r, nLep=i, ptCuts=ptCuts, absEtaCuts=absEtaCuts,ele_MVAID_cuts=ele_MVAID_cuts) ]
#
#def splitIndList(var, l, val):
#  resLow = []
#  resHigh = []
#  for x in l:
#    if var[x]>val:
#      resHigh.append(x)
#    else:
#      resLow.append(x)
#  return resLow, resHigh
#
#def splitListOfObjects(var, val, s):
#  resLow = []
#  resHigh = []
#  for x in s:
#    if x[var]<val:
#      resLow.append(x)
#    else:
#      resHigh.append(x)
#  return resLow, resHigh

