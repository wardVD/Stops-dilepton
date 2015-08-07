import ROOT
ROOT.gROOT.LoadMacro("$CMSSW_BASE/src/StopsDilepton/tools/scripts/tdrstyle.C")
ROOT.setTDRStyle()
import numpy

from math import *
from StopsDilepton.tools.helpers import getChain,  getWeight
from StopsDilepton.tools.localInfo import *
from datetime import datetime

start = datetime.now()
print '\n','\n', "Starting code",'\n','\n'


#preselection: MET>40, njets>=2, n_bjets>=1, n_lep>=2
#For now see here for the Sum$ syntax: https://root.cern.ch/root/html/TTree.html#TTree:Draw@2
#preselection = 'met_pt>40&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id&&Jet_btagCSV>0.814)>=1&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2&&Sum$(LepGood_pt>20)>=2'
preselection = 'met_pt>40&&Sum$(Jet_pt>30&&abs(Jet_eta)<2.4&&Jet_id)>=2&&Sum$(LepGood_pt>20)==2'

#######################################################
#        SELECT WHAT YOU WANT TO DO HERE              #
#######################################################
reduceStat = 1 #recude the statistics, i.e. 10 is ten times less samples to look at
makedraw1D = True
makedraw2D = True

#######################################################
#                 load all the samples                #
#######################################################
from StopsDilepton.plots.cmgTuplesPostProcessed_PHYS14 import *
from StopsDilepton.plots.cmgTuples_SPRING15 import *
#backgrounds = [WJetsHTToLNu, TTH, TTW, TTZ, DYWARD, singleTop, TTJets]#, QCD]
backgrounds = [DY_15,DY]
#signals = [SMS_T2tt_2J_mStop425_mLSP325, SMS_T2tt_2J_mStop500_mLSP325, SMS_T2tt_2J_mStop650_mLSP325, SMS_T2tt_2J_mStop850_mLSP100]
signals = []


#######################################################
#            get the TChains for each sample          #
#######################################################
for s in backgrounds+signals:
  if s.has_key('totalweight'): s['chain'] = getChain(s,histname="",treeName="tree")
  else:                        s['chain'] = getChain(s,histname="")

plots = {\
  'met': {'title':'E^{miss}_{T} (GeV)', 'name':'MET', 'histo':{}},
  'dPhi_1':{'title':'cos(dPhi(MET,jet_1))', 'name':'leadingdPhi', 'histo':{}},
  'dPhi_2':{'title':'cos(dPhi(MET,jet_2))', 'name':'subleadingdPhi', 'histo':{}},
  'njets': {'title':'nJets', 'name':'nJets', 'histo':{}},
  }
plots2D = {\
  'metvsdPhi_1':{'Xtitle':'Cos(dPhi(MET,jet_1))','Ytitle':'MET', 'name':'METvsLeadingdPhi', 'histo':{}},
  'metvsMaxdPhi_Max':{'Xtitle':'Max(Cos(dPhi(MET,jet))','Ytitle':'MET', 'name':'max(METvsdPhi),jet_pt>100_Max', 'histo':{}},
  'metvsMaxdPhi_MaxIf':{'Xtitle':'Max(Cos(dPhi(MET,jet))','Ytitle':'MET', 'name':'max(METvsdPhi),jet_pt>100_MaxIf', 'histo':{}}
  }


#######################################################
#            Start filling in the histograms          #
#######################################################
for i,s in enumerate(backgrounds+signals):
  chain = s["chain"]

  chain.Draw("met_pt>>met"+str(i)+"(25,20,1020)",preselection)
  plots['met']['histo'][s["name"]] = ROOT.gDirectory.Get("met"+str(i))

  chain.Draw("cos(met_phi-Jet_phi[0])>>cos_1"+str(i)+"(50,-1.1,1.1)",preselection)
  plots['dPhi_1']['histo'][s["name"]] = ROOT.gDirectory.Get("cos_1"+str(i))

  chain.Draw("cos(met_phi-Jet_phi[1])>>cos_2"+str(i)+"(50,-1.1,1.1)",preselection)
  plots['dPhi_2']['histo'][s["name"]] = ROOT.gDirectory.Get("cos_2"+str(i))

  chain.Draw("Length$(Jet_pt)>>njets"+str(i)+"(10,0,10)",preselection)
  plots['njets']['histo'][s['name']] = ROOT.gDirectory.Get("njets"+str(i))

  chain.Draw("met_pt:cos(met_phi-Jet_phi[0])>>metvsdphi"+str(i)+"(50,-1,1,50,0,1000)",preselection)
  plots2D['metvsdPhi_1']['histo'][s['name']] = ROOT.gDirectory.Get("metvsdphi"+str(i))

  chain.Draw("met_pt:Max$((Jet_pt>100)*cos(met_phi-Jet_phi))>>max_metvsdphi"+str(i)+"(50,-1,1,50,0,1000)",preselection+'&&Jet_pt>100')
  plots2D['metvsMaxdPhi_Max']['histo'][s['name']] = ROOT.gDirectory.Get("max_metvsdphi"+str(i))
  
  chain.Draw("met_pt:MaxIf$(cos(met_phi-Jet_phi),Jet_pt>100)>>max_metvsdphi_2"+str(i)+"(50,-1,1,50,0,1000)",preselection+'&&Jet_pt>100')
  plots2D['metvsMaxdPhi_MaxIf']['histo'][s['name']] = ROOT.gDirectory.Get("max_metvsdphi_2"+str(i))

processtime = datetime.now()
print "Time to process chains: ", processtime - start

#######################################################
#             Drawing done here                       #
#######################################################
#Some coloring
DY["color"]=ROOT.kBlue
DY_15["color"]=ROOT.kRed
legendtextsize = 0.032

if makedraw1D:
  for plot in plots.keys():
    for s in backgrounds+signals:
      integral = plots[plot]['histo'][s['name']].Integral()
      plots[plot]['histo'][s['name']].Scale(1./integral)
     
    #Make a stack for backgrounds
    l=ROOT.TLegend(0.6,0.8,1.0,1.0)
    l.SetFillColor(0)
    l.SetShadowColor(ROOT.kWhite)
    l.SetBorderSize(1)
    l.SetTextSize(legendtextsize)

    #Plot!
    c1 = ROOT.TCanvas()
    for i,b in enumerate(backgrounds):
      plots[plot]['histo'][b["name"]].SetLineColor(b["color"])
      plots[plot]['histo'][b["name"]].SetLineWidth(3)
      plots[plot]['histo'][b["name"]].SetMarkerSize(0)
      plots[plot]['histo'][b["name"]].Draw("same")
      l.AddEntry(plots[plot]['histo'][b["name"]],b['name'])
      if i == 0: 
        plots[plot]['histo'][b["name"]].GetXaxis().SetTitle(plots[plot]['title'])
        plots[plot]['histo'][b["name"]].GetYaxis().SetTitle("Events (A.U.)")
        if plot!="met": plots[plot]['histo'][b["name"]].GetYaxis().SetRangeUser(0.001,2)
    c1.SetLogy()
    l.Draw()
    c1.Print(plotDir+"/testDY/"+plots[plot]['name']+".png")

if makedraw2D:
  for b in backgrounds+signals:
    for plot in plots2D.keys():
      c1 = ROOT.TCanvas()
      ROOT.gStyle.SetOptStat(0)
      ROOT.gStyle.SetPalette(1)
      c1.SetRightMargin(0.16)

      l=ROOT.TLegend(0.6,0.9,1.0,1.0)
      l.SetFillColor(0)
      l.SetShadowColor(ROOT.kWhite)
      l.SetBorderSize(1)
      l.SetTextSize(legendtextsize)

      plots2D[plot]['histo'][b["name"]].Draw("colz")
      ROOT.gPad.Update()
      palette = plots2D[plot]['histo'][b["name"]].GetListOfFunctions().FindObject("palette")
      palette.SetX1NDC(0.85)
      palette.SetX2NDC(0.9)
      palette.Draw()

      l.AddEntry(plots2D[plot]['histo'][b["name"]],b['name'])
      plots2D[plot]['histo'][b["name"]].GetXaxis().SetTitle(plots2D[plot]['Xtitle'])
      plots2D[plot]['histo'][b["name"]].GetYaxis().SetTitle(plots2D[plot]['Ytitle'])
      l.Draw()
      c1.SetLogz()
      c1.Print(plotDir+"/testDY/"+plots2D[plot]['name']+'_'+b['name']+".png")
      c1.Close()

makeplotstime = datetime.now()

print '\n','\n', "Total time processing: ", makeplotstime-start
