import ROOT
from math import pi, sqrt, cos, sin, sinh, log
from array import array

def getFileList(dir, minAgeDPM=0, histname='histo', xrootPrefix='root://hephyse.oeaw.ac.at/', maxN=-1):
  import os, subprocess, datetime
  monthConv = {'Jan':1, 'Feb':2,'Mar':3,'Apr':4,"May":5, "Jun":6,"Jul":7,"Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}
  if dir[0:5] != "/dpm/":
    filelist = os.listdir(os.path.expanduser(dir))
    filelist = [dir+'/'+f for f in filelist if histname in f]
  else:
    filelist = []
    p = subprocess.Popen(["dpns-ls -l "+ dir], shell = True , stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
      if not (histname=="" or line.count(histname)):continue
      line=line[:-1]
      sline = line.split()
      fname = sline[-1]
      size = sline[4]
      if int(size)!=0:
        month, day = sline[5:7]
        hour, minute = sline[7].split(':')
        age = (datetime.datetime.now() - datetime.datetime(2014, monthConv[month], int(day), int(hour), int(minute))).total_seconds()/3600
        if age>=minAgeDPM:
          filelist.append(fname)
        else:
          print "Omitting",fname,'too young:',str(age)+'h'
    filelist = [xrootPrefix+dir+'/'+f for f in filelist]
  if maxN>=0:
    filelist = filelist[:maxN]
  return filelist

def getChain(sL, minAgeDPM=0, histname='histo', xrootPrefix='root://hephyse.oeaw.ac.at/', maxN=-1, treeName="Events"):
  if not type(sL)==type([]):
    sList = [sL]
  else:
    sList= sL 
  c = ROOT.TChain(treeName)
  i=0
  for s in sList:
    if type(s)==type(""):
      for f in getFileList(s, minAgeDPM, histname, xrootPrefix, maxN):
        i+=1
        c.Add(f)
    if type(s)==type({}):
      if s.has_key('file'):
        c.Add(s['file'])
        i+=1
      if s.has_key('fromDPM') and s['fromDPM']:
        for f in getFileList(s['dir'], minAgeDPM, histname, xrootPrefix, maxN):
          i+=1
          c.Add(f)
      if s.has_key('bins'):
        for b in s['bins']:
          dir = s['dirname'] if s.has_key('dirname') else s['dir']
          for f in getFileList(dir+'/'+b, minAgeDPM, histname, xrootPrefix, maxN):
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

