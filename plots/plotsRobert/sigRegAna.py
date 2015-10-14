import ROOT
from math import sqrt
#helpers
from StopsDilepton.samples.cmgTuples_Spring15_25ns_postProcessed import *
from StopsDilepton.samples.cmgTuples_Data25ns_postProcessed import *
from StopsDilepton.tools.helpers import getVarValue, getYieldFromChain, getChain
from StopsDilepton.tools.localInfo import plotDir
#Define chains for signals and backgrounds

import pickle
regions = pickle.load(file('/afs/hephy.at/data/rschoefbeck01/StopsDilepton/regions/'+prefix+'.pkl'))
vars=[]

reg={}
for r in regions:
  for c in r['cuts']:
    if c['name'] not in vars: vars.append(c['name'])

def sOverB(s,b):
  if b>0:
    return s/b
  else:
    return 0.
def sOverSqrtB(s,b):
  if b>0:
    return s/sqrt(b)
  else:
    return 0.

def maxFOM(r, fom=sOverB):
  return  max([fom(r['sigYields'][s], r['bkgYield']) for s in r['sigYields'].keys()])

goodRegions = filter(lambda r:maxFOM(r)>1, regions)

 
