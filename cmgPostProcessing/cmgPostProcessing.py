import ROOT
import sys, os, copy, random, subprocess, datetime
from array import array
from StopsDilepton.tools.convertHelpers import compileClass, readVar, printHeader, typeStr, createClassString

from math import *
from StopsDilepton.tools.mt2Calculator import mt2Calculator 
mt2Calc = mt2Calculator()
from StopsDilepton.tools.mtautau import mtautau as mtautau_
from StopsDilepton.tools.helpers import getChain, getChunks, getObjDict, getEList, getVarValue
from StopsDilepton.tools.objectSelection import getLeptons, getMuons, getElectrons, getGoodMuons, getGoodElectrons, getGoodLeptons, getJets, getGoodBJets, getGoodJets 

from StopsDilepton.tools.localInfo import *

ROOT.gSystem.Load("libFWCoreFWLite.so")
ROOT.AutoLibraryLoader.enable()

from StopsDilepton.samples.xsec import xsec
from StopsDilepton.samples.cmgTuples_Data50ns_1l import *
from StopsDilepton.samples.cmgTuples_Spring15_25ns import *
from StopsDilepton.samples.cmgTuples_Spring15_50ns import *

target_lumi = 1000 #pb-1 Which lumi to normalize to

defSampleStr = "MuonEG_Run2015B_PromptReco"  #Which samples to run for by default (will be overritten by --samples option)

subDir = "/data/rschoefbeck/cmgTuples/postProcessed_Spring15_test" #Output directory -> The first path should go to localInfo (e.g. 'dataPath' or something)

#branches to be kept for data and MC
branchKeepStrings_DATAMC = ["run", "lumi", "evt", "isData", "rho", "nVert", 
#                     "nJet25", "nBJetLoose25", "nBJetMedium25", "nBJetTight25", "nJet40", "nJet40a", "nBJetLoose40", "nBJetMedium40", "nBJetTight40", 
#                     "nLepGood20", "nLepGood15", "nLepGood10", "htJet25", "mhtJet25", "htJet40j", "htJet40", "mhtJet40", "nSoftBJetLoose25", "nSoftBJetMedium25", "nSoftBJetTight25", 
                     "met*","Flag_*","HLT_*",
#                     "nFatJet","FatJet_*", 
                     "nJet", "Jet_*", 
                     "nLepGood", "LepGood_*", 
#                     "nLepOther", "LepOther_*", 
                     "nTauGood", "TauGood_*",
                     ] 

#branches to be kept for MC samples only
branchKeepStrings_MC = [ "nTrueInt", "genWeight", "xsec", "puWeight", 
#                     "GenSusyMScan1", "GenSusyMScan2", "GenSusyMScan3", "GenSusyMScan4", "GenSusyMGluino", "GenSusyMGravitino", "GenSusyMStop", "GenSusyMSbottom", "GenSusyMStop2", "GenSusyMSbottom2", "GenSusyMSquark", "GenSusyMNeutralino", "GenSusyMNeutralino2", "GenSusyMNeutralino3", "GenSusyMNeutralino4", "GenSusyMChargino", "GenSusyMChargino2", 
#                     "ngenLep", "genLep_*", 
#                     "nGenPart", "GenPart_*",
                     "ngenPartAll","genPartAll_*" ,
#                     "ngenTau", "genTau_*", 
#                     "ngenLepFromTau", "genLepFromTau_*"
                      ]

#branches to be kept for data only
branchKeepStrings_DATA = [
            ]

from optparse import OptionParser
parser = OptionParser()
parser.add_option("--samples", dest="allSamples", default=defSampleStr, type="string", action="store", help="samples:Which samples.")
parser.add_option("--inputTreeName", dest="inputTreeName", default="treeProducerSusySingleLepton", type="string", action="store", help="samples:Which samples.")
parser.add_option("--targetDir", dest="targetDir", default=subDir, type="string", action="store", help="target directory.")
parser.add_option("--skim", dest="skim", default="dilep", type="string", action="store", help="any skim condition?")
parser.add_option("--small", dest="small", default = False, action="store_true", help="Just do a small subset.")

(options, args) = parser.parse_args()
assert options.skim in ['none', 'dilep'], "Unknown skim: %s"%options.skim
skimCond = "(1)"

if options.skim.lower()=='dilep':
  skimCond += "&&Sum$(LepGood_pt>20&&abs(LepGood_eta)<2.5)>=2"

if sys.argv[0].count('ipython'):
  options.small=False

def getTreeFromChunk(c, skimCond, iSplit, nSplit):
  if not c.has_key('file'):return
  rf = ROOT.TFile.Open(c['file'])
  assert not rf.IsZombie()
  rf.cd()
  tc = rf.Get("tree")
  nTot = tc.GetEntries()
  fromFrac = iSplit/float(nSplit)
  toFrac   = (iSplit+1)/float(nSplit)
  start = int(fromFrac*nTot)
  stop  = int(toFrac*nTot)
  ROOT.gDirectory.cd('PyROOT:/')
  print "Copy tree from source: total number of events found:",nTot,"Split counter: ",iSplit,"<",nSplit,"first Event:",start,"nEvents:",stop-start
  t = tc.CopyTree(skimCond,"",stop-start,start)
  tc.Delete()
  del tc
  rf.Close()
  del rf
  return t
   
exec('allSamples=['+options.allSamples+']')
for isample, sample in enumerate(allSamples):
  #chunks, sumWeight = getChunks(sample, options.inputTreeName)
  maxN = 1 if options.small else -1
  chunks, sumWeight = getChunks(sample, maxN=maxN)
  #chunks, nTotEvents = getChunksFromDPM(sample, options.inputTreeName)
#  print "Chunks:" , chunks 
  outDir = options.targetDir+'/'+"/".join([options.skim, sample['name']])
  tmpDir = outDir+'/tmp/'
  os.system('mkdir -p ' + outDir) 
  os.system('mkdir -p '+tmpDir)
  os.system('rm -rf '+tmpDir+'/*')
  
  if sample['isData']: 
    lumiScaleFactor=1
    branchKeepStrings = branchKeepStrings_DATAMC + branchKeepStrings_DATA 
  else:
    lumiScaleFactor = xsec[sample['dbsName']]*target_lumi/float(sumWeight)
    branchKeepStrings = branchKeepStrings_DATAMC + branchKeepStrings_MC

  readVariables = ['met_pt/F', 'met_phi/F']
  newVariables = ['weight/F']
  aliases = [ "met:met_pt", "metPhi:met_phi"]

  readVectors = [\
    {'prefix':'LepGood',  'nMax':8, 'vars':['pt/F', 'eta/F', 'phi/F', 'pdgId/I', 'charge/I', 'relIso03/F', 'tightId/I', 'miniRelIso/F','mass/F','sip3d/F','mediumMuonId/I', 'mvaIdPhys14/F','lostHits/I', 'convVeto/I', 'dxy/F', 'dz/F']},
    {'prefix':'Jet',  'nMax':100, 'vars':['pt/F', 'eta/F', 'phi/F', 'id/I','btagCSV/F', 'btagCMVA/F', 'mcMatchFlav/I', 'partonId/I']},
  ]
  if not sample['isData']: 
    aliases.extend(['genMet:met_genPt', 'genMetPhi:met_genPhi'])
  if options.skim.lower() in ['dilep']:
    newVariables.extend( ['dl_pt/F', 'dl_eta/F', 'dl_phi/F', 'dl_mass/F' ] )
    newVariables.extend( ['dl_mt2ll/F', 'dl_mt2bb/F', 'dl_mt2blbl/F', 'dl_mtautau/F', 'dl_alpha0/F',  'dl_alpha1/F' ] )
    newVariables.extend( ['l1_pt/F', 'l1_eta/F', 'l1_phi/F', 'l1_mass/F', 'l1_pdgId/I', 'l1_index/I' ] )
    newVariables.extend( ['l2_pt/F', 'l2_eta/F', 'l2_phi/F', 'l2_mass/F', 'l2_pdgId/I', 'l2_index/I' ] )
    newVariables.extend( ['isEE/I', 'isMuMu/I', 'isEMu/I' ] )

  newVars = [readVar(v, allowRenaming=False, isWritten = True, isRead=False) for v in newVariables]
  
  readVars = [readVar(v, allowRenaming=False, isWritten=False, isRead=True) for v in readVariables]
  for v in readVectors:
    readVars.append(readVar('n'+v['prefix']+'/I', allowRenaming=False, isWritten=False, isRead=True))
    v['vars'] = [readVar(v['prefix']+'_'+vvar, allowRenaming=False, isWritten=False, isRead=True) for vvar in v['vars']]

  printHeader("Compiling class to write")
  writeClassName = "ClassToWrite_"+str(isample)
  writeClassString = createClassString(className=writeClassName, vars= newVars, vectors=[], nameKey = 'stage2Name', typeKey = 'stage2Type')
#  print writeClassString
  s = compileClass(className=writeClassName, classString=writeClassString, tmpDir='/tmp/')

  readClassName = "ClassToRead_"+str(isample)
  readClassString = createClassString(className=readClassName, vars=readVars, vectors=readVectors, nameKey = 'stage1Name', typeKey = 'stage1Type', stdVectors=False)
  printHeader("Class to Read")
#  print readClassString
  r = compileClass(className=readClassName, classString=readClassString, tmpDir='/tmp/')

  filesForHadd=[]
  if options.small: chunks=chunks[:1]
  #print "CHUNKS:" , chunks
  for chunk in chunks:
    sourceFileSize = os.path.getsize(chunk['file'])
    nSplit = 1+int(sourceFileSize/(200*10**6)) #split into 200MB
    if nSplit>1: print "Chunk too large, will split into",nSplit,"of appox 200MB"
    for iSplit in range(nSplit):
      t = getTreeFromChunk(chunk, skimCond, iSplit, nSplit)
      if not t: 
        print "Tree object not found:", t
        continue
      t.SetName("Events")
      nEvents = t.GetEntries()
      for v in newVars:
#        print "new VAR:" , v
        v['branch'] = t.Branch(v['stage2Name'], ROOT.AddressOf(s,v['stage2Name']), v['stage2Name']+'/'+v['stage2Type'])
      for v in readVars:
#        print "read VAR:" , v
        t.SetBranchAddress(v['stage1Name'], ROOT.AddressOf(r, v['stage1Name']))
      for v in readVectors:
        for var in v['vars']:
          t.SetBranchAddress(var['stage1Name'], ROOT.AddressOf(r, var['stage1Name']))
      for a in aliases:
        t.SetAlias(*(a.split(":")))
      print "File: %s Chunk: %s nEvents: %i (skim: %s) condition: %s lumiScaleFactor: %f"%(chunk['file'],chunk['name'], nEvents, options.skim, skimCond, lumiScaleFactor)
      
      for i in range(nEvents):
        if (i%10000 == 0) and i>0 :
          print i,"/",nEvents  , "name:" , chunk['name']
        s.init()
        r.init()
        t.GetEntry(i)
        genWeight = 1 if sample['isData'] else t.GetLeaf('genWeight').GetValue()
        s.weight = lumiScaleFactor*genWeight
#  if options.skim.lower() in ['dilep']:
#    newVariables.extend( ['dl_pt/F', 'dl_eta/F', 'dl_phi/F', 'dl_m/F' ] )
#    newVariables.extend( ['dl_mt2ll/F', 'dl_mt2bb/F', 'dl_mt2blbl/F', 'dl_mtautau/F' ] )
#    newVariables.extend( ['l1_pt/F', 'l1_eta/F', 'l1_phi/F', 'l1_E/F', 'l1_pdgId/I', 'l1_index/I' ] )
#    newVariables.extend( ['l2_pt/F', 'l2_eta/F', 'l2_phi/F', 'l2_E/F', 'l2_pdgId/I', 'l2_index/I' ] )
#    newVariables.extend( ['isEE/I', 'isMuMu/I', 'isEMu/I' ] )

        if options.skim.lower()=='dilep':
          leptons = getGoodLeptons(r)
#          print "Leptons", leptons 
          if len(leptons)>=2:# and leptons[0]['pdgId']*leptons[1]['pdgId']<0 and abs(leptons[0]['pdgId'])==abs(leptons[1]['pdgId']): #OSSF choice
            mt2Calc.reset()
            s.l1_pt  = leptons[0]['pt'] 
            s.l1_eta = leptons[0]['eta']
            s.l1_phi = leptons[0]['phi']
            s.l1_mass   = leptons[0]['mass']
            s.l1_pdgId   = leptons[0]['pdgId']
            s.l1_index   = leptons[0]['index']
            s.l2_pt  = leptons[1]['pt'] 
            s.l2_eta = leptons[1]['eta']
            s.l2_phi = leptons[1]['phi']
            s.l2_mass   = leptons[1]['mass']
            s.l2_pdgId   = leptons[1]['pdgId']
            s.l2_index   = leptons[1]['index']

            l_pdgs = [abs(leptons[0]['pdgId']), abs(leptons[1]['pdgId'])]
            l_pdgs.sort()
            s.isMuMu = l_pdgs==[13,13] 
            s.isEE = l_pdgs==[11,11] 
            s.isEMu = l_pdgs==[11,13] 

            l1 = ROOT.TLorentzVector()
            l1.SetPtEtaPhiM(leptons[0]['pt'], leptons[0]['eta'], leptons[0]['phi'], 0 )
            l2 = ROOT.TLorentzVector()
            l2.SetPtEtaPhiM(leptons[1]['pt'], leptons[1]['eta'], leptons[1]['phi'], 0 )
            dl = l1+l2
            s.dl_pt  = dl.Pt()
            s.dl_eta = dl.Eta()
            s.dl_phi = dl.Phi()
            s.dl_mass   = dl.M() 
            mt2Calc.setMet(r.met_pt,r.met_phi)
            mt2Calc.setLeptons(s.l1_pt, s.l1_eta, s.l1_phi, s.l2_pt, s.l2_eta, s.l2_phi)
            s.dl_mt2ll = mt2Calc.mt2ll()
            s.dl_mtautau, s.dl_alpha0, s.dl_alpha1 = mtautau_(r.met_pt,r.met_phi, s.l1_pt, s.l1_eta, s.l1_phi, s.l2_pt, s.l2_eta, s.l2_phi, retAll=True)

            bjets = getGoodBJets(r)
            if len(bjets)>=2:
              mt2Calc.setBJets(bjets[0]['pt'], bjets[0]['eta'], bjets[0]['phi'], bjets[1]['pt'], bjets[1]['eta'], bjets[1]['phi'])
              s.dl_mt2bb   = mt2Calc.mt2bb()
              s.dl_mt2blbl = mt2Calc.mt2blbl()

        for v in newVars:
          v['branch'].Fill()
      newFileName = sample['name']+'_'+chunk['name']+'_'+str(iSplit)+'.root'
      filesForHadd.append(newFileName)
      if True or  not options.small:
      #if options.small:
        f = ROOT.TFile(tmpDir+'/'+newFileName, 'recreate')
        t.SetBranchStatus("*",0)
        for b in branchKeepStrings + [v['stage2Name'] for v in newVars] +  [v.split(':')[1] for v in aliases]:
          t.SetBranchStatus(b, 1)
        t2 = t.CloneTree()
        t2.Write()
        f.Close()
        print "Written",tmpDir+'/'+newFileName
        del f
        del t2
        t.Delete()
        del t
      for v in newVars:
        del v['branch']

  print "Event loop end"
  if not options.small: 
    size=0
    counter=0
    files=[]
    for f in filesForHadd:
      size+=os.path.getsize(tmpDir+'/'+f)
      files.append(f)
      if size>(0.5*(10**9)) or f==filesForHadd[-1] or len(files)>300:
        ofile = outDir+'/'+sample['name']+'_'+str(counter)+'.root'
        print "Running hadd on", tmpDir, files
        os.system('cd '+tmpDir+';hadd -f '+ofile+' '+' '.join(files))
        print "Written", ofile
        size=0
        counter+=1
        files=[]
    os.system("rm -rf "+tmpDir)

