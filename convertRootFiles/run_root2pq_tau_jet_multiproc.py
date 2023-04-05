import os, glob, re
from multiprocessing import Pool

#print("ENVIRONMENT: ", os.environ)

def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [int(c) if c.isdigit() else c for c in re.split('([0-9]+)',s)]

def sort_nicely(l):
    """ Sort the given list in the way that humans expect.
    """
    l.sort(key=alphanum_key)

def run_process(process):
    os.system('python %s'%process)

decay='DYToTauTau_M-50_13TeV'

#xrootd='root://cmsxrootd.fnal.gov' # FNAL
#xrootd='root://eoscms.cern.ch' # CERN
local='/eos/uscms/store/group/lpcml/rchudasa/NTuples/DYToTauTau_M-50_13TeV-powheg_pythia8/DYToTauTau_ntuples/230327_062100/0000'

#Paths to input files
#rhFileList = '%s/%s/*.root'%(xrootd,local)
rhFileList = '%s/*.root'%(local)
print(" >> Input file list: %s"%rhFileList)
rhFileList = glob.glob(rhFileList)
assert len(rhFileList) > 0
print(" >> %d files found"%len(rhFileList))
#rhFileList = [('%s/%s'%(xrootd, rhFile)).replace('/eos/uscms','') for rhFile in rhFileList]
#print(' >> Input File[0]: %s'%rhFileList[0])
sort_nicely(rhFileList)

files_per_run =1 
#files_per_run = 5
# Output path
outDir='/eos/uscms/store/group/lpcml/rchudasa/NTuples/DYToTauTau_M-50_13TeV-powheg_pythia8/'
if not os.path.isdir(outDir):
    os.makedirs(outDir)
print(' >> Output directory: %s'%outDir)

proc_file = 'convert_root2pq_tau_jet.py'
#processes = []

for it,i in enumerate(range(0, len(rhFileList), files_per_run)):
    if(it>1): continue
    #if(it>2): continue
    rhFileList_batch = rhFileList[i:i+files_per_run]
    #processes.append('%s -i %s -o %s -d %s -n %d'%(proc_file, ' '.join(rhFileList_batch), outDir, decay, it))
    processes = ['%s -i %s -o %s -d %s -n %d'%(proc_file, ' '.join(rhFileList_batch), outDir, decay, it)]
    #print(processes[it])
    #print(' >> Process[0]: %s'%processes[0])
    
    #pool = Pool(processes=2)
    pool = Pool(processes=len(processes))
    pool.map(run_process, processes)