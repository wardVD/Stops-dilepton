# Stops-dilepton 
cmsrel CMSSW_7_2_3_patch1
cd CMSSW_7_2_3_patch1/src 
cmsenv 
git cms-addpkg FWCore/Version #initialization of git repo

#(CMSSW forbids hyphen in module name->cmsenv won't work)
git clone https://github.com/wardVD/Stops-dilepton StopsDilepton
