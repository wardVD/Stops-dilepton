from StopsDilepton.tools.helpers import getObjFromFile
#Define a functor that returns a reweighting-function according to the era
def getReweightingFunction(era="Run2015D_205pb", histoTitle="nVtxReweight"):
  fileName = "$CMSSW_BASE/src/StopsDilepton/tools/python/puReweightingData/"+era+'.root'
  reweightingHisto = getObjFromFile(fileName, histoTitle)
  print "Loaded %s from file %s"%(histoTitle, fileName)
  def reweightingFunc(nvtx):
    return reweightingHisto.GetBinContent(reweightingHisto.FindBin(nvtx))

  return reweightingFunc
