#!/bin/sh 
########Spring15###############

#python cmgPostProcessing.py --skim=dilep  --samples=DYJetsToLL_M_10to50_25ns
#python cmgPostProcessing.py --skim=dilep  --samples=DYJetsToLL_M_50_25ns
#python cmgPostProcessing.py --skim=dilep  --samples=DYJetsToLL_M_50_HT100to200_25ns
#python cmgPostProcessing.py --skim=dilep  --samples=DYJetsToLL_M_50_HT200to400_25ns
#python cmgPostProcessing.py --skim=dilep  --samples=DYJetsToLL_M_50_HT400to600_25ns
#python cmgPostProcessing.py --skim=dilep  --samples=DYJetsToLL_M_50_HT600toInf_25ns
python cmgPostProcessing.py --skim=dilep  --overwrite --samples=TTLep_pow_25ns
python cmgPostProcessing.py --skim=dilep  --overwrite --samples=DYJetsToLL_M_5to50_25ns
python cmgPostProcessing.py --skim=dilep  --overwrite --samples=DYJetsToLL_M_5to50_HT100to200_25ns
python cmgPostProcessing.py --skim=dilep  --overwrite --samples=DYJetsToLL_M_5to50_HT200to400_25ns
python cmgPostProcessing.py --skim=dilep  --overwrite --samples=DYJetsToLL_M_5to50_HT400to600_25ns
python cmgPostProcessing.py --skim=dilep  --overwrite --samples=DYJetsToLL_M_5to50_HT600toInf_25ns
