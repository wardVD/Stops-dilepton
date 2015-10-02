import copy, os, sys
from StopsDilepton.tools.localInfo import dataDir
dir = dataDir 

SingleMuon_Run2015B = { "name" : "SingleMuon_Run2015B", 
"bins":[
#"SingleMuon_Run2015B-17Jul2015-v1",
"SingleMuon_Run2015B-PromptReco-v1",
]}
SingleMu_Run2015B = { "name" : "SingleMu_Run2015B", 
"bins":[
#"SingleMu_Run2015B-17Jul2015-v1",
"SingleMu_Run2015B-PromptReco-v1",
]}
SingleElectron_Run2015B = { "name" : "SingleElectron_Run2015B", 
"bins":[
#"SingleElectron_Run2015B-17Jul2015-v1",
"SingleElectron_Run2015B-PromptReco-v1",
]}
DoubleEG_Run2015B = { "name" :"DoubleEG_Run2015B", 
"bins":[
#"DoubleEG_Run2015B-17Jul2015-v1",
"DoubleEG_Run2015B-PromptReco-v1",
]}
MuonEG_Run2015B = { "name" :"MuonEG_Run2015B", 
"bins":[
#"MuonEG_Run2015B-17Jul2015-v1",
"MuonEG_Run2015B-PromptReco-v1",
]}
EGamma_Run2015B = { "name" : "EGamma_Run2015B", 
"bins":[
#"EGamma_Run2015B-17Jul2015-v1",
"EGamma_Run2015B-PromptReco-v1",
]}
DoubleMuon_Run2015B = { "name" : "DoubleMuon_Run2015B", 
"bins":[
#"DoubleMuon_Run2015B-17Jul2015-v1",
"DoubleMuon_Run2015B-PromptReco-v1",
]}
JetHT_Run2015B = { "name" : "JetHT_Run2015B", 
"bins":[
#"JetHT_Run2015B-17Jul2015-v1",
"JetHT_Run2015B-PromptReco-v1",
]}
MET_Run2015B = { "name" : "MET_Run2015B", 
"bins":[
#"MET_Run2015B-17Jul2015-v1",
"MET_Run2015B-PromptReco-v1",
]}

allSamples_Data50ns_1l = [SingleMuon_Run2015B, SingleMu_Run2015B, SingleElectron_Run2015B, DoubleEG_Run2015B, MuonEG_Run2015B, EGamma_Run2015B, DoubleMuon_Run2015B, JetHT_Run2015B, MET_Run2015B]
import ROOT 
for s in allSamples_Data50ns_1l:
  s.update({ 
    'dir' : dir,
    'color':ROOT.kBlack,
    'isData':True,
    'lumi':42.
  })

