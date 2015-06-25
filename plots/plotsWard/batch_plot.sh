cd /afs/cern.ch/work/w/wvandrie/public/STOPS/CMSSW_7_2_3_patch1/src/
eval `scramv1 runtime -sh`;
scram b -j9
mkdir -p /afs/cern.ch/user/w/wvandrie/eos;
/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select -b fuse mount /afs/cern.ch/user/w/wvandrie/eos;
cd /afs/cern.ch/work/w/wvandrie/public/STOPS/CMSSW_7_2_3_patch1/src/StopsDilepton/plots/plotsWard
python plot.py
