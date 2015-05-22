import ROOT, array
from math import pi, sqrt, cos, sin, sinh, cosh

ROOT.gROOT.ProcessLine(".L $CMSSW_BASE/src/StopsDilepton/tools/scripts/mt2_bisect.cpp+")

def mt2(metPt, metPhi, l1Pt, l1Phi, l2Pt, l2Phi):
  mt2 = ROOT.mt2()
  pmiss  = array.array('d',[  0., metPt*cos(metPhi), metPt*sin(metPhi)] )
  l1     = array.array('d',[  0., l1Pt*cos(l1Phi), l1Pt*sin(l1Phi)] )
  l2     = array.array('d',[  0., l2Pt*cos(l2Phi), l2Pt*sin(l2Phi)] )
  mn = 0.
  mt2.set_mn(mn)
  mt2_values=[]
  mt2.set_momenta(l1, l2, pmiss)
  return mt2.get_mt2()
