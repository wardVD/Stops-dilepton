import ROOT
from math import pi, sqrt, cos, sin, sinh, log
from array import array
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()

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

  binwidth = (mt2ll['binning'][2]-mt2ll['binning'][1])/(mt2ll['binning'][0])

  if mt2cut%binwidth == 0:

    bin1 = int(mt2cut/binwidth) + 1
    bin2 = mt2ll['binning'][0] + 1

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
    sortedhist = sorted(mt2ll['histo'].items(),key=lambda l:l[1].Integral(bin1,bin2))
    for item in sortedhist:
      samplename = item[0].replace("_","\_")
      if a == 0:
        output.write("\\multirow{"+ str(len(sortedhist)) +"}{*}{"+ str(int(mt2cut)) +"} & " + samplename + " & " + str(round(item[1].Integral(bin1,bin2),2)) + "\\\\" + '\n')
      else:
        output.write(" & " + samplename + " & " + str(round(item[1].Integral(bin1,bin2),2)) + "\\\\" + '\n')
      a+=1
    output.write("\\hline" + '\n')
    output.write("\\hline" + '\n')
  
    output.write("\\end{tabular}" + '\n')
    
    output.write("\\end{document}")
  
    output.close()

  else:

    print '\n' + '\n' + "binwidth for MT2ll and cut for MT2ll in table are not compatible, please change! No table for " +channel+  " is produced." + '\n' + '\n'

  
def piemaker(mt2cut,channel,plots):

  mt2ll = plots[channel]['mt2ll']

  binwidth = (mt2ll['binning'][2]-mt2ll['binning'][1])/(mt2ll['binning'][0])

  bin1 = int(mt2cut/binwidth) + 1
  bin2 = mt2ll['binning'][0] + 1
  sortedhist = sorted(mt2ll['histo'].items(),key=lambda l:l[1].Integral(bin1,bin2))

  ROOT.gStyle.SetOptStat(0)
  canvas = ROOT.TCanvas()
  canvas.SetRightMargin(0.3)
  canvas.SetBottomMargin(0.3)
  vals = array('f', [item[1].Integral(bin1,bin2) for item in sortedhist])
  pie = ROOT.TPie('Pie_''channel''_forMT2llcutat''mt2cut','',len(vals),vals)
  pie.SetLabelsOffset(-0.2)
  pie.SetLabelFormat("#splitline{%val}{(%perc)}")
  pie.SetCircle(0.35,0.35,0.3)
  legend = ROOT.TLegend(0.7,0.7,0.9,0.9)
  legend.SetFillColor(0)
  legend.SetShadowColor(ROOT.kWhite)
  legend.SetBorderSize(1)
  legend.SetTextSize(0.032)
  for i in range(len(vals)):
    pie.SetEntryFillColor(i,i+2)
    sortedhist[i][1].SetFillColor(i+2)
    legend.AddEntry(sortedhist[i][1],sortedhist[i][0],"f")
    legend.AddEntry(pie.GetSlice(i),sortedhist[i][0],"f")
  pie.Draw('nol < t')
  legend.Draw("same")
  canvas.Print("Pie_"+channel+"_forMT2llcutat"+str(int(mt2cut))+".png")
