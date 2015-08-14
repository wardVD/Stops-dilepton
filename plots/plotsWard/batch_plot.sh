cd /afs/cern.ch/work/w/wvandrie/public/STOPS/CMSSW_7_2_3_patch1/src/
eval `scramv1 runtime -sh`;
scram b -j9
cd /afs/cern.ch/work/w/wvandrie/public/STOPS/CMSSW_7_2_3_patch1/src/StopsDilepton/plots/plotsWard
python plot.py
