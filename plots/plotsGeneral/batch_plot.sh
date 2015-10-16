cd $CMSSW_BASE/src
eval `scramv1 runtime -sh`;
scram b -j9
cd ./StopsDilepton/plots/plotsGeneral
python plot.py
