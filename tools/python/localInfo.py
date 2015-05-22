import os
if os.environ['USER'] in ['schoef', 'rschoefbeck', 'schoefbeck']:
  plotDir = "/afs/hephy.at/user/r/rschoefbeck/www/png2L/"
  dataDir = "/data/rschoefbeck/cmgTuples/postProcessed_Phys14V3_diLep/diLep/" 
if os.environ['USER'] in ['ward']:
  plotDir = "yourDir"
  dataDir = "~/eos/cms/store/cmst3/group/susy/schoef/postProcessed_Phys14V3_diLep"
