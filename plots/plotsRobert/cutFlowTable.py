import ROOT

#helpers
from StopsDilepton.samples.cmgTuples_Spring15_25ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_postProcessed import *
from StopsDilepton.tools.helpers import getVarValue, getYieldFromChain, getChain
from StopsDilepton.tools.localInfo import plotDir
#Define chains for signals and backgrounds
samples = [
  TTLep_25ns, 
  SMS_T2tt_2J_mStop425_mLSP325,
  SMS_T2tt_2J_mStop500_mLSP325,
  SMS_T2tt_2J_mStop650_mLSP325,
  SMS_T2tt_2J_mStop850_mLSP100,
]
for s in samples:
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
 ("SFZVeto","( (isMuMu==1||isEE==1)&&abs(dl_mass-90.2)>=15 || isEMu==1 )"), 
  ]

lumiFac=10
for s in samples:
  print "\nSample: %s"%s['name']
  for i in range(len(cuts)+1):
    selection = "&&".join(c[1] for c in cuts[:i])
    if selection=="":selection="(1)"
    name = "-".join(c[0] for c in cuts[:i])
    y = lumiFac*getYieldFromChain(s['chain'], selection, 'weight')
    n = getYieldFromChain(s['chain'], selection, '(1)')
    print "%10.3f %10i %s"%(y,n,name)
#    print "%10.3f %10i %s %s"%(y,n,name,selection)
