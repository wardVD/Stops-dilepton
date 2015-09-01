#!/bin/sh 
########Spring15###############

python cmgPostProcessing.py --skim=dilep  --samples=WZ_25ns
python cmgPostProcessing.py --skim=dilep  --samples=WWTo2L2Nu_25ns
python cmgPostProcessing.py --skim=dilep  --samples=ZZ_25ns
python cmgPostProcessing.py --skim=dilep  --samples=ZJetsToNuNu_HT200to400_25ns
python cmgPostProcessing.py --skim=dilep  --samples=ZJetsToNuNu_HT400to600_25ns
python cmgPostProcessing.py --skim=dilep  --samples=ZJetsToNuNu_HT600toInf_25ns

