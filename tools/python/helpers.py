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
  #elistTMP_t = ROOT.gROOT.Get('eListTMP_t')
  elistTMP_t = ROOT.gDirectory.Get('eListTMP_t')
  elistTMP = elistTMP_t.Clone(newname)
  del elistTMP_t
  return elistTMP

def getObjDict(c, prefix, variables, i):
 return {var: c.GetLeaf(prefix+var).GetValue(i) for var in variables}

def genmatching(lepton,genparticles):
  for gen in genparticles:
      deltaphi = abs(lepton['phi'] - gen['phi'])
      if (deltaphi > pi): deltaphi = 2*pi - deltaphi
      deltaeta = abs(lepton['eta'] - gen['eta'])
      deltar = sqrt(deltaphi**2 + deltaeta**2)
      if deltar<0.01:
        print deltar
        print gen['motherId']

def latexmaker(mt2cut,channel,plots):

  mt2ll = plots[channel]['mt2ll']
  output = open("./table_"+channel+".tex","w")

  output.write("\\documentclass[8pt]{article}" + '\n')
  output.write("\\usepackage[margin=0.5in]{geometry}" + '\n')
  output.write("\\usepackage{verbatim}" + '\n')
  output.write("\\usepackage{hyperref}" + '\n')
  output.write("\\usepackage{epsfig}" + '\n')
  output.write("\\usepackage{graphicx}" + '\n')
  output.write("\\usepackage{epsfig}" + '\n')
  output.write("\\usepackage{subfigure,              rotating,              rotate}" + '\n')
  output.write("\\usepackage{relsize}" + '\n')
  output.write("\\usepackage{fancyheadings}" + '\n')
  output.write("\usepackage{multirow}" + '\n')
  output.write("\\usepackage[latin1]{inputenc}" + '\n')
  output.write("\\usepackage{footnpag}" + '\n')
  output.write("\\usepackage{enumerate}" + '\n')
  output.write("\\usepackage{color}" + '\n')
  output.write("\\newcommand{\\doglobally}[1]{{\\globaldefs=1#1}}" + '\n')
  output.write("\\begin{document}" + '\n')
  
  
  output.write("\\begin{tabular}{|c|c|c|c|c|c|}" + '\n')
  output.write("\\hline" + '\n')
  output.write("$M_{T2}$ cut (GeV) & Sample & Count \\\\"+ '\n')
  output.write("\\hline" + '\n')
  output.write("\\hline" + '\n')
  a = 0
  for key in mt2ll['histo']:
    if a == 0:
      output.write("\\multirow{"+ str(len(mt2ll['histo'])) +"}{*}{"+ mt2cut +"} & " + key + " & " + str(round(mt2ll['histo'][key].Integral(),2)) + "\\\\" + '\n')
    else:
      output.write(" & " + key + " & " + str(round(mt2ll['histo'][key].Integral(),2)) + "\\\\" + '\n')
    a+=1
  output.write("\\hline" + '\n')
  output.write("\\hline" + '\n')
  
  output.write("\\end{tabular}" + '\n')
  
  output.write("\\end{document}")
  
  output.close()
