#!/bin/sh 
########Spring15###############
python cmgPostProcessing.py --skim=dilep  --samples=TTJets_50ns
python cmgPostProcessing.py --skim=dilep  --samples=DYJetsToLL_M_10to50_50ns
python cmgPostProcessing.py --skim=dilep  --samples=DYJetsToLL_M_50_50ns
