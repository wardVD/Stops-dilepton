import os
if os.environ['USER'] in ['wvandrie']:
  plotDir = "/afs/cern.ch/user/w/wvandrie/www/Stops/"
  dataDir = "~/eos/cms/store/cmst3/group/susy/schoef/postProcessed_Phys14V3_diLep" #needs EOS mount on lxplus at ~/eos
if os.environ['USER'] in ['didar']:
  plotDir = "."
  dataDir = "~/eos/cms/store/cmst3/group/susy/schoef/postProcessed_Phys14V3_diLep" #needs EOS mount on lxplus at ~/eos 
if os.environ['USER'] in ['schoef', 'rschoefbeck', 'schoefbeck']:
  plotDir = "/afs/hephy.at/user/r/rschoefbeck/www/png2L/"
  dataDir = "/data/rschoefbeck/cmgTuples/postProcessed_Phys14V3_diLep/diLep/" 
