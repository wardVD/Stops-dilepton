# Stops-dilepton 
cmsrel CMSSW_7_4_7_patch1;

cd CMSSW_7_4_7_patch1/src ;

cmsenv ;

git cms-addpkg FWCore/Version

git clone https://github.com/wardVD/Stops-dilepton StopsDilepton

cd $CMSSW_BASE/src

scram b -j9

To run: 

cd StopsDilepton/plots/plotsWard/

python plot.py

** To compile TMVA **
cd TMVA/test; source setup.[c]sh; 
cd ..
make
******************** 

