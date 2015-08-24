import copy, os, sys
from StopsDilepton.tools.localInfo import dataDir
dir = dataDir 

SingleMuon_Run2015B = { "name" : "SingleMuon_Run2015B", 
"bins":["SingleMuon_Run2015B_17Jul2015",
"SingleMuon_Run2015B_PromptReco",]}
SingleMu_Run2015B = { "name" : "SingleMu_Run2015B", 
"bins":["SingleMu_Run2015B_17Jul2015",
"SingleMu_Run2015B_PromptReco",]}
SingleElectron_Run2015B = { "name" : "SingleElectron_Run2015B", 
"bins":["SingleElectron_Run2015B_17Jul2015",
"SingleElectron_Run2015B_PromptReco",]}
DoubleEG_Run2015B = { "name" : "DoubleEG_Run2015B", 
"bins":["DoubleEG_Run2015B_17Jul2015",
"DoubleEG_Run2015B_PromptReco",]}
EGamma_Run2015B = { "name" : "EGamma_Run2015B", 
"bins":["EGamma_Run2015B_17Jul2015",
"EGamma_Run2015B_PromptReco",]}
DoubleMuon_Run2015B = { "name" : "DoubleMuon_Run2015B", 
"bins":["DoubleMuon_Run2015B_17Jul2015",
"DoubleMuon_Run2015B_PromptReco",]}
JetHT_Run2015B = { "name" : "JetHT_Run2015B", 
"bins":["JetHT_Run2015B_17Jul2015",
"JetHT_Run2015B_PromptReco",]}
MET_Run2015B = { "name" : "MET_Run2015B", 
"bins":["MET_Run2015B_17Jul2015",
"MET_Run2015B_PromptReco",]}

allSamples_Data50ns_1l = [SingleMuon_Run2015B, SingleMu_Run2015B, SingleElectron_Run2015B, DoubleEG_Run2015B, EGamma_Run2015B, DoubleMuon_Run2015B, JetHT_Run2015B, MET_Run2015B]
 
for s in allSamples_Data50ns_1l:
  s.update({ 
    'dir' : dir,
  })

