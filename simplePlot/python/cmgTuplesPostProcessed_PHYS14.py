import copy, os, sys

dir = "~/eos/cms/store/cmst3/group/susy/schoef/postProcessed_Phys14V3_diLep"

TTJets={\
"name" : "ttJets",
"bins" : ["TTJets"],
'dir' : dir,
}
WJetsHTToLNu={\
"name" : "WJetsHTToLNu",
"bins" : ["WJetsToLNu_HT100to200", "WJetsToLNu_HT200to400", "WJetsToLNu_HT400to600", "WJetsToLNu_HT600toInf"],
'dir' : dir,
}
TTVH={\
"name" : "TTVH",
"bins" : ["TTH", "TTWJets", "TTZJets"],
'dir' : dir,
}
singleTop={\
"name" : "singleTop",
"bins" : ["TBarToLeptons_sch", "TBarToLeptons_tch", "TBar_tWch", "TToLeptons_sch", "TToLeptons_tch", "T_tWch"],
'dir' : dir,
}
DY={\
"name" : "DY",
"bins" : ["DYJetsToLL_M50_HT100to200", "DYJetsToLL_M50_HT200to400", "DYJetsToLL_M50_HT400to600", "DYJetsToLL_M50_HT600toInf"],
'dir' : dir,
}
QCD={\
"name" : "QCD",
"bins" : ["QCD_HT_250To500", "QCD_HT_500To1000", "QCD_HT_1000ToInf"],
'dir' : dir,
}

allSignalStrings=[\
"SMS_T2tt_2J_mStop425_mLSP325",
"SMS_T2tt_2J_mStop500_mLSP325",
"SMS_T2tt_2J_mStop650_mLSP325",
"SMS_T2tt_2J_mStop850_mLSP100",
]

def getSignalSample(signal):
  if signal in allSignalStrings:
    return {
      "name" : signal,
      'dir' : dir,
      'bins':[signal]}
  else:
    print "Signal",signal,"unknown. Available: ",", ".join(allSignalStrings)

allSignals=[]
for s in allSignalStrings:
  sm = getSignalSample(s)
  exec(s+"=sm")
  exec("allSignals.append(s)")
