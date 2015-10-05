import ROOT
from ROOT import TTree, TFile, AddressOf, gROOT, TH1F
from array import array
import numpy as n
from math import *


#list_of_plots = [
#    Plot("et"           , TH1F("pho_et"           , "Lead #gamma: E_{T};E_{T} (GeV);entries/bin", 25, 0.0, 100.0)),
#    Plot("eta"          , TH1F("pho_eta"          , "Lead #gamma: #eta;#eta;entries/bin"        , 25, -3.0, 3.0)),
#    Plot("sigmaIetaIeta", TH1F("pho_sigmaIEtaIEta", "Lead #gamma: #sigma_{i#etai#eta};#sigma_{i#etai#eta};entries/bin",20, 0, 0.06)),
#    Plot("metEt/et"     , TH1F("metEt_over_phoEt" , "MET / E_{T}(#gamma);MET/E_{T}(sc);entries/bin"   , 20, 0.0, 3.0)),
#    Plot("phi:eta"      , TH2F("phoPhi_vs_phoEta" , "Lead #gamma: #phi vs #eta;#eta;#phi"             , 50, -2.5, 2.5, 18, -3.14, 3.14))
#    ]

MET = TH1F("MET", 'E_{T}', 25, 0, 500) 

f = ROOT.TFile.Open("outfile.root")

for event in f.AnaTree :

#    print "met = %d: mt2ll = %d: mt2bb = %d: mt2blbl %d" % (event.MET,event.mt2ll,event.mt2bb,event.mt2blbl)

       MET.Fill( event.MET )


c1 = ROOT.TCanvas()
#bkg_stack.SetMaximum(2*bkg_stack.GetMaximum())
#bkg_stack.SetMinimum(10**-1.5)
MET.Draw('')
c1.SetLogy()
c1.Print("~/www/php-plots/test.png")
