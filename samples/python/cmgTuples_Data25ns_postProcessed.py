import copy, os, sys
from StopsDilepton.tools.localInfo import dataDir
dir = dataDir 


DoubleEG_Run2015D = { "name" :"DoubleEG_Run2015D", 
"bins":[
"DoubleEG_Run2015D-PromptReco-v3",
],
"lumi":147.4
}
MuonEG_Run2015D = { "name" :"MuonEG_Run2015D", 
"bins":[
"MuonEG_Run2015D-PromptReco-v3",
],
"lumi":125.0,
}
DoubleMuon_Run2015D = { "name" : "DoubleMuon_Run2015D", 
"bins":[
"DoubleMuon_Run2015D-PromptReco-v3",
],
"lumi":123.9
}

allSamples_Data25ns = [DoubleEG_Run2015D, MuonEG_Run2015D, DoubleMuon_Run2015D]
import ROOT 
for s in allSamples_Data25ns:
  s.update({ 
    'dir' : dir,
    'color':ROOT.kBlack,
    'isData':True
  })

