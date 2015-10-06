import copy, os, sys
from StopsDilepton.tools.localInfo import dataDir
dir = dataDir 

DoubleEG_Run2015D = { "name" :"DoubleEG_Run2015D", 
"bins":[
"DoubleEG_Run2015D-PromptReco-v3",
],
"lumi":209.2
}
MuonEG_Run2015D = { "name" :"MuonEG_Run2015D", 
"bins":[
"MuonEG_Run2015D-PromptReco-v3",
],
"lumi":209.2,
}
DoubleMuon_Run2015D = { "name" : "DoubleMuon_Run2015D", 
"bins":[
"DoubleMuon_Run2015D-PromptReco-v3",
],
"lumi":204.2
}

allSamples_Data25ns = [DoubleEG_Run2015D, MuonEG_Run2015D, DoubleMuon_Run2015D]
import ROOT 
for s in allSamples_Data25ns:
  s.update({ 
    'dir' : dir,
    'color':ROOT.kBlack,
    'isData':True
  })

