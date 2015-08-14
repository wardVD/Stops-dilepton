# Stops-dilepton 
cmsrel CMSSW_7_2_3_patch1;

cd CMSSW_7_2_3_patch1/src ;

cmsenv ;

git cms-addpkg FWCore/Version

git clone https://github.com/wardVD/Stops-dilepton StopsDilepton

cd $CMSSW_RELEASE_BASE/src

To run: python plot.py

** To compile TMVA **
cd TMVA/test; source setup.[c]sh; 
cd ..
make
******************** 

