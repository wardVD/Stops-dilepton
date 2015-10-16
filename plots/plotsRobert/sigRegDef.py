import ROOT

#helpers
from StopsDilepton.samples.cmgTuples_Spring15_25ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_postProcessed import *
from StopsDilepton.tools.helpers import getVarValue, getYieldFromChain, getChain
from StopsDilepton.tools.localInfo import plotDir
#Define chains for signals and backgrounds
c_bkg = getChain([TTLep_25ns, DY_25ns, singleTop_25ns], histname='')

signals=[
  SMS_T2tt_2J_mStop425_mLSP325,
  SMS_T2tt_2J_mStop500_mLSP325,
  SMS_T2tt_2J_mStop650_mLSP325,
  SMS_T2tt_2J_mStop850_mLSP100,
]
for s in signals:
  s['chain'] = getChain(s,histname='')

cuts=[
 ("lepVeto", "nGoodMuons+nGoodElectrons==2"),
 ("njet2", "(Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id))>=2"), 
 ("nbtag1", "Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.890)>=1"), 
 ("mll20", "dl_mass>20"), 
 ("met80", "met_pt>80"), 
 ("metSig5", "met_pt/sqrt(Sum$(Jet_pt*(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)))>5"), 
 ("dPhiJet0-dPhiJet1", "abs(cos(met_phi-Jet_phi[0]))<cos(0.25)&&abs(cos(met_phi-Jet_phi[1]))<cos(0.25)"), 
 ("isOS","isOS==1"),
 ("SFOF","( (isMuMu==1||isEE==1)&&abs(dl_mass-90.2)>=15 || isEMu==1 )"), 
  ]
preselection = "&&".join(c[1] for c in cuts)
prefix = "3D_step50"
##Set preselection cut
#print "Setting event list for samples... "
#for i, c in enumerate([c_bkg] + [s['chain'] for s in signals]):
#  c.Draw(">>eList_"+str(i), cut)
#  eList = ROOT.gDirectory.Get("eList_"+str(i))
#  c.SetEventList(eList)
#  del eList
#
#print "..done." 

lumiFac=10

#Define variables to be optimized
variables = [
{'name':'dl_mt2ll',   'thresholds':[0, 50, 100, 150, 200, 250, 300]},
{'name':'dl_mt2bb',   'thresholds':[80, 120, 160, 200, 250, 300]},
{'name':'dl_mt2blbl', 'thresholds':[0, 50, 100, 150, 200, 250, 300]},
]


#Helper: returns cut string for given variable and bin
def cutString(varName, bin):
  res=varName+">"+str(bin[0])
  if bin[1]>0:res=res+"&&"+varName+"<="+str(bin[1])
  return res

def regionCondition(bkgYield, sigYields):
  #return True if signal region is large enough. 
  return max(sigYields.values())>0.9 and bkgYield>0.
#  return max([bkgYield]+sigYields.values())>0.9

lowestCuts = "&&".join([cutString(v['name'], (v['thresholds'][0],-1)) for v in variables])
regions=[]
def findBinning(variables=variables, selection=('(1)', []), prefix=""):
  #take first variable
  var = variables[0]
  remainder = variables[1:]
  #descend the list of thresholds
  upperCut=-1
  for t in reversed(var['thresholds']):
    bin = ( t, upperCut )
#    print selection
    print prefix+"%s (cut: %s). Now Looking into %s %s."%(", ".join([s['name']+":"+str(s['cut']) for s in selection[1]]), selection[0], var['name'], repr(bin))
    cut_str = cutString(var['name'], bin)
    cut =  "&&".join([lowestCuts, preselection, selection[0], cut_str])
    signalYields  = {s['name']:lumiFac*getYieldFromChain(s['chain'], cut, 'weight') for s in signals}
    bkgYield      = max(0, lumiFac*getYieldFromChain(c_bkg, cut, 'weight'))

    thisSelection=(selection[0]+"&&"+cut_str,selection[1]+[{'name':var['name'], 'cut': (t, upperCut)}])
    #Is the region large enough?
    print " "*len(prefix)+"Cut:", cut
    print " "*len(prefix)+"Found bkg",bkgYield, "sig.:", signalYields.values()
    if regionCondition(bkgYield, signalYields):
      #Yes -> split it with the next variable
      if len(remainder)>0:
        print prefix+"Splitting up-->"
        findBinning(variables=remainder, selection = thisSelection, prefix="--> "+prefix)
      else:
        print " "*len(prefix)+"Adding: "+", ".join([s['name']+":"+str(s['cut']) for s in thisSelection[1]])
        regions.append({'cuts':thisSelection[1], 'sigYields':signalYields,'bkgYield':bkgYield})
      upperCut = t
    else:
      #No->merge 
      pass
  if not regionCondition(bkgYield, signalYields):
    print " "*len(prefix)+"Loop done. Adding region: "+", ".join([s['name']+":"+str(s['cut']) for s in thisSelection[1]])
    regions.append({'cuts':thisSelection[1], 'sigYields':signalYields,'bkgYield':bkgYield})

findBinning()

import pickle
pickle.dump(regions, file('/afs/hephy.at/data/rschoefbeck01/StopsDilepton/regions/'+prefix+'.pkl','w'))
