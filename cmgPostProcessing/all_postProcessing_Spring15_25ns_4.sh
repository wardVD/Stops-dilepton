#!/bin/sh 
########Spring15###############

python cmgPostProcessing.py --skim=dilep  --samples=TToLeptons_sch_25ns
python cmgPostProcessing.py --skim=dilep  --samples=TToLeptons_tch_25ns
python cmgPostProcessing.py --skim=dilep  --samples=TBar_tWch_25ns
python cmgPostProcessing.py --skim=dilep  --samples=T_tWch_25ns
