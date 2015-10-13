from StopsDilepton.tools.puReweighting import getReweightingFunction
#Get the PU reweighting function
era = "Run2015D_205pb"
puReweightingFunc = getReweightingFunction(era=era)

n=17
w=puReweightingFunc(n)
print "Found %i vertices, reweighting according to %s is %f"%(n,era,w)
