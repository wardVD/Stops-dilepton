import ROOT
from math import pi, sqrt, cos, sin, sinh, log, cosh
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

def getChunks(sample,  maxN=-1):
#  print "sample" , sample , maxN
  import os, subprocess, datetime
  #print "sample dir:" , sample['dir']
  chunks = [{'name':x} for x in os.listdir(sample['dir']) if x.startswith(sample['chunkString']+'_Chunk') or x==sample['name']]
  #print chunks
  chunks=chunks[:maxN] if maxN>0 else chunks
  sumWeights=0
  failedChunks=[]
  goodChunks  =[] 
  const = 'All Events' if sample['isData'] else 'Sum Weights'
  for i, s in enumerate(chunks):
      if not sample.has_key("skimAnalyzerDir"):
        logfile = sample['dir']+'/'+s['name']+'/SkimReport.txt'
      else:
        logfile = sample['dir']+'/'+s['name']+"/"+sample["skimAnalyzerDir"]+'/SkimReport.txt'
      if os.path.isfile(logfile):
        line = [x for x in subprocess.check_output(["cat", logfile]).split('\n') if x.count(const)]
        assert len(line)==1,"Didn't find normalization constant '%s' in  number in file %s"%(const, logfile)
        #n = int(float(line[0].split()[2]))
        sumW = float(line[0].split()[2])
        inputFilename = sample['dir']+'/'+s['name']+'/'+sample['rootFileLocation']
        #print sumW, inputFilename
        if os.path.isfile(inputFilename):
          sumWeights+=sumW
          s['file']=inputFilename
          goodChunks.append(s)
        else:
          failedChunks.append(chunks[i])
      else:
        print "log file not found:  ", logfile
        failedChunks.append(chunks[i])
#    except: print "Chunk",s,"could not be added"
  eff = round(100*len(failedChunks)/float(len(chunks)),3)
  print "Chunks: %i total, %i good (normalization constant %f), %i bad. Inefficiency: %f"%(len(chunks),len(goodChunks),sumWeights,len(failedChunks), eff)
  for s in failedChunks: 
    print "Failed:",s
  return goodChunks, sumWeights

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

def getVarValue(c, var, n=-1):
  try:
    att = getattr(c, var)
    if n>=0:return att[n]
    return att
  except:  
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
  res={var: getVarValue(c, prefix+var, i) for var in variables}
  res['index']=i
  return res
#  return {var: c.GetLeaf(prefix+var).GetValue(i) for var in variables}

def getWeight(c,sample,lumi,n=0):
  genweight_value    = c.GetLeaf("genWeight").GetValue(n)
  lumi_value         = lumi
  xsec_value         = c.GetLeaf("xsec").GetValue(n)
  sumofweights_value = sum(sample['totalweight'])
  return (genweight_value*lumi_value*xsec_value)/sumofweights_value

def genmatching(lepton,genparticles):
  for gen in genparticles:
      deltaphi = abs(lepton['phi'] - gen['phi'])
      if (deltaphi > pi): deltaphi = 2*pi - deltaphi
      deltaeta = abs(lepton['eta'] - gen['eta'])
      deltar = sqrt(deltaphi**2 + deltaeta**2)
      if deltar<0.01:
        print deltar
        print gen['motherId']

def latexmaker_1(channel,plots,mt2cut):

  for cut in mt2cut:

    mt2ll = plots[channel]['mt2llwithcut'+cut]

    output = open("./tables/table_"+channel+"_mt2cutat"+cut+".tex","w")

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
    output.write("$M_{T2}$ cut at " + str(cut)  + " (GeV) & Count \\\\"+ '\n')
    output.write("\\hline" + '\n')
    output.write("\\hline" + '\n')
  
    sortedhist = sorted(mt2ll['histo'].items(),key=lambda l:l[1].Integral()) #set histogram with highest value first
    for item in sortedhist:
      samplename = item[0].replace("_","\_")
      output.write(samplename + " & " + str(round(item[1].Integral(),2)) + "\\\\" + '\n')
    output.write("\\hline" + '\n')
    output.write("\\hline" + '\n')
  
    output.write("\\end{tabular}" + '\n')
  
    output.write("\\end{document}")
  
    output.close()


def latexmaker_2(piechart,mt2llcut,channel):

  mt2ll = piechart[str(mt2llcut)][channel]["(>=2,>=1)"]

  output = open("./tables/table_"+channel+"_mt2ll"+str(mt2llcut)+".tex","w")

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
  output.write("$M_{T2}$ cut at " + str(mt2llcut)  + " (GeV) & Count \\\\"+ '\n')
  output.write("\\hline" + '\n')
  output.write("\\hline" + '\n')

  sortedhist = sorted(mt2ll.items(),key=lambda l:l[1])
  for item in sortedhist:
    samplename = item[0].replace("_","\_")
    output.write(samplename + " & " + str(round(item[1],2)) + "\\\\" + '\n')
  output.write("\\hline" + '\n')
  output.write("\\hline" + '\n')
  
  output.write("\\end{tabular}" + '\n')
    
  output.write("\\end{document}")
    
  output.close()

    
  
def piemaker(mt2cut,piechart):
  
  ROOT.gStyle.SetOptStat(0)
  canvas = ROOT.TCanvas('canvas','canvas',700,572)
  canvas.SetLeftMargin(0.2)
  ROOT.gStyle.SetPadLeftMargin(0.2)
  canvas.SetRightMargin(0.3)
  canvas.SetBottomMargin(0.3)
  height=1-ROOT.gStyle.GetPadBottomMargin()-ROOT.gStyle.GetPadTopMargin()
  width =1-ROOT.gStyle.GetPadLeftMargin()-ROOT.gStyle.GetPadRightMargin()
  canvas.cd()
  pies = []
  pads = []
  canvas.Divide(5,1)
  for ipiece, piece in enumerate(piechart["SF"].keys()):
    x0 = ROOT.gStyle.GetPadLeftMargin() + (0.01+ipiece)*width/float(len(piechart["SF"]))
    x1 = ROOT.gStyle.GetPadLeftMargin() + (0.99+ipiece)*width/float(len(piechart["SF"]))
    y0 = ROOT.gStyle.GetPadBottomMargin() + (0.01+1.)*height/float(2)
    y1 = ROOT.gStyle.GetPadBottomMargin() + (0.99+1.)*height/float(2)

    cols = array('i', [1])

    pielist = [piechart["SF"][piece][i] for i in piechart["SF"][piece]]
    pielist = array('f',pielist)
    temp = ROOT.TPie('pie_'+piece,'',len(pielist),pielist,cols)
    pies.append(temp)
  
  for ipiece, piece in enumerate(piechart["SF"].keys()):
    canvas.cd(ipiece+1)
    pies[ipiece].Draw("nol")

  canvas.SaveAs("Pie_SF_forMT2llcutat.png")
  #canvas.Close()

def deltaPhi(phi1, phi2):
  dphi = phi2-phi1
  if  dphi > pi:
    dphi -= 2.0*pi
  if dphi <= -pi:
    dphi += 2.0*pi
  return abs(dphi)

