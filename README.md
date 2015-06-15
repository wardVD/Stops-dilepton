# Stops-dilepton 
cmsrel CMSSW_7_2_3_patch1;

cd CMSSW_7_2_3_patch1/src ;

cmsenv ;

git cms-addpkg FWCore/Version

git clone https://github.com/wardVD/Stops-dilepton StopsDilepton
