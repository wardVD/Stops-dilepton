import copy, os, sys

data_path = "/data/rschoefbeck/cmgTuples/Run2015D/"

SingleMuon_Run2015D_PromptReco = { "name" : "SingleMuon_Run2015D-PromptReco-v3","lumi":143.8}
MuonEG_Run2015D_PromptReco = { "name" : "MuonEG_Run2015D-PromptReco-v3","lumi":125.0}
SingleElectron_Run2015D_PromptReco = { "name" : "SingleElectron_Run2015D-PromptReco-v3","lumi":146.0}
DoubleEG_Run2015D_PromptReco = { "name" : "DoubleEG_Run2015D-PromptReco-v3","lumi":147.4}
DoubleMuon_Run2015D_PromptReco = { "name" : "DoubleMuon_Run2015D-PromptReco-v3","lumi":123.9}
JetHT_Run2015D_PromptReco = { "name" : "JetHT_Run2015D-PromptReco-v3","lumi":135.9}
MET_Run2015D_PromptReco = { "name" : "MET_Run2015D-PromptReco-v3","lumi":124.9}

allSamples_Data25ns = [SingleMuon_Run2015D_PromptReco, MuonEG_Run2015D_PromptReco, SingleElectron_Run2015D_PromptReco, DoubleEG_Run2015D_PromptReco, DoubleMuon_Run2015D_PromptReco, JetHT_Run2015D_PromptReco, MET_Run2015D_PromptReco]

for s in allSamples_Data25ns:
  s['chunkString'] = s['name']
  s.update({ 
    "rootFileLocation":"tree.root",
    "skimAnalyzerDir":"",
    "treeName":"tree",
    'isData':True,
    'dir' : data_path
  })
