
import os
if os.environ['USER'] in ['wvandrie']:
  plotDir = "/afs/cern.ch/user/w/wvandrie/www/Stops/"
  dataDir = "/afs/cern.ch/work/w/wvandrie/public/STOPS/ANALYSIS/CMSSW_7_4_7_patch1/src/StopsDilepton/samplesCopyWard_Spring15_new/"
if os.environ['USER'] in ['didar']:
  plotDir = "."
  dataDir = "~/eos/cms/store/cmst3/group/susy/schoef/postProcessed_Phys14V3_diLep" #needs EOS mount on lxplus at ~/eos 
if os.environ['USER'] in ['schoef', 'rschoefbeck', 'schoefbeck']:
  plotDir = "/afs/hephy.at/user/r/rschoefbeck/www/png2L/"
  dataDir = "/data/rschoefbeck/cmgTuples/postProcessed_Spring15_pass2/dilep/" 
if os.environ['USER'] in ['sigamani']:
  plotDir = "...."
  dataDir = "/afs/cern.ch/work/w/wvandrie/public/STOPS/ANALYSIS/CMSSW_7_4_7_patch1/src/StopsDilepton/samplesCopyWard_Spring15_new/"
