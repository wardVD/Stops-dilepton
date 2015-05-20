import ROOT
from math import pi, sqrt, cos, sin, sinh, log
from array import array

def getFileList(dir, histname='histo', maxN=-1):
  import os
  filelist = os.listdir(os.path.expanduser(dir))
  filelist = [dir+'/'+f for f in filelist if histname in f]
  if maxN>=0:
    filelist = filelist[:maxN]
  return filelist

def getChain(sampleList, histname='histo', maxN=-1, treeName="Events"):
  if not type(sampleList)==type([]):
    sampleList_ = [sampleList]
  else:
    sampleList_= sampleList 
  c = ROOT.TChain(treeName)
  i=0
  for s in sampleList_:
    if type(s)==type(""):
      for f in getFileList(s, histname, maxN):
        i+=1
        c.Add(f)
    if type(s)==type({}):
      if s.has_key('file'):
        c.Add(s['file'])
        i+=1
      if s.has_key('bins'):
        for b in s['bins']:
          dir = s['dirname'] if s.has_key('dirname') else s['dir']
          for f in getFileList(dir+'/'+b, histname, maxN):
            i+=1
            c.Add(f)
  print "Added ",i,'files from sample',s['name']
  return c

def getObjFromFile(fname, hname):
  f = ROOT.TFile(fname)
  assert not f.IsZombie()
  f.cd()
  htmp = f.Get(hname)
  if not htmp:  return htmp
  ROOT.gDirectory.cd('PyROOT:/')
  res = htmp.Clone()
  f.Close()
  return res

def getVar(c, var, n=0):
    l = c.GetLeaf(var)
    try:
       return l.GetValue(n)
    except:
      raise Exception("Unsuccessful getVarValue for leaf %s and index %i"%(var, n))

def getVarValue(c, var, n=0):
  varNameHisto = var
  leaf = c.GetAlias(varNameHisto)
  if leaf!='':
    try:
      return c.GetLeaf(leaf).GetValue(n)
    except:
      raise Exception("Unsuccessful getVarValue for leaf %s and index %i"%(leaf, n))
  else:
    l = c.GetLeaf(var)
    if l:return l.GetValue(n)
    return float('nan')

def getEList(chain, cut, newname='eListTMP'):
  chain.Draw('>>eListTMP_t', cut)
  elistTMP_t = ROOT.gROOT.Get('eListTMP_t')
  elistTMP = elistTMP_t.Clone(newname)
  del elistTMP_t
  return elistTMP

