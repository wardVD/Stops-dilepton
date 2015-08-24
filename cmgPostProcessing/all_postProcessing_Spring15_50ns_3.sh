#!/bin/sh 
########Spring15###############
python cmgPostProcessing.py --skim=dilep  --samples=WJetsToLNu_50ns
python cmgPostProcessing.py --skim=dilep  --samples=TToLeptons_tch_50ns
python cmgPostProcessing.py --skim=dilep  --samples=TBar_tWch_50ns
python cmgPostProcessing.py --skim=dilep  --samples=T_tWch_50ns
