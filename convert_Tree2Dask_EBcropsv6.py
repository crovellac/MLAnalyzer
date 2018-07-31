import numpy as np
import ROOT
from root_numpy import tree2array, root2array
from dask.delayed import delayed
import dask.array as da
import glob

eosDir='/eos/uscms/store/user/mba2012/IMGs/DoublePi0Pt50To60'
#eosDir='/eos/uscms/store/user/mba2012/IMGs/DoublePi0Pt50To60_r9gt07'
#decays = ['DoublePi0Pt30To90_pythia8_m000_2016_25ns_Moriond17MC_PoissonOOTPU']
decays = [
'DoublePhotonPt50To60_pythia8_2016_25ns_Moriond17MC_PoissonOOTPU',
'DoublePi0Pt50To60_m000_pythia8_2016_25ns_Moriond17MC_PoissonOOTPU',
'DoublePi0Pt50To60_m0To1600_pythia8_2016_25ns_Moriond17MC_PoissonOOTPU'
#'DoublePhotonPt50To60_r9gt07_pythia8_2016_25ns_Moriond17MC_PoissonOOTPU',
#'DoublePi0Pt50To60_m000_r9gt07_pythia8_2016_25ns_Moriond17MC_PoissonOOTPU',
#'DoublePi0Pt50To60_m0To1600_r9gt07_pythia8_2016_25ns_Moriond17MC_PoissonOOTPU'
]

#neffs = [244, 244, (nevts//1000)] 
neffs = [1, 1, 1] 
chunk_size_ = 500
scale = 1.

@delayed
def load_X(tree, start_, stop_, branches_, readouts, scale):
    X = tree2array(tree, start=start_, stop=stop_, branches=branches_) 
    #X = root2array(tree, treename='fevt/RHTree', start=start_, stop=stop_, branches=branches_) 
    # Convert the object array X to a multidim array:
    # 1: for each event x in X, concatenate the object columns (branches) into a flat array of shape (readouts*branches)
    # 2: reshape the flat array into a stacked array: (branches, readouts)
    # 3: embed each stacked array as a single row entry in a list via list comprehension
    # 4: convert this list into an array with shape (events, branches, readouts) 
    X = np.array([np.concatenate(x).reshape(len(branches_),readouts[0]*readouts[1]) for x in X])
    #print "X.shape:",X.shape
    X = X.reshape((-1,len(branches_),readouts[0],readouts[1]))
    X = np.transpose(X, [0,2,3,1])

    # Rescale
    X /= scale 
    return X

@delayed
def load_single(tree, start_, stop_, branches_):
    X = tree2array(tree, start=start_, stop=stop_, branches=branches_) 
    #X = root2array(tree, treename='fevt/RHTree', start=start_, stop=stop_, branches=branches_) 
    if len(branches_) > 1:
      X = np.array([np.concatenate(x).reshape(len(branches_),1) for x in X])
      X = X.reshape((-1,len(branches_)))
    else:
      X = np.array([x[0] for x in X])

    return X

def get_weight(m0, m0_edges, lhood):
    # m0
    if m0 >= m0_edges[-1]:
        idx_m0 = len(m0_edges)-1
    else:
        idx_m0 = np.argmax(m0 < m0_edges)-1
    return lhood[idx_m0]

def get_weight_2d(m0, pt, m0_edges, pt_edges, lhood):
    # m0
    if m0 >= m0_edges[-1]:
        idx_m0 = len(m0_edges)-1
    else:
        idx_m0 = np.argmax(m0 < m0_edges)-1
    # pt
    if pt >= pt_edges[-1]:
        idx_pt = len(pt_edges)-1
    else:
        idx_pt = np.argmax(pt < pt_edges)-1
    return lhood[idx_m0, idx_pt]

for j,decay in enumerate(decays):

    if j != 2:
        pass
        #continue

    tfile_str = '%s/%s_IMGcrop.root'%(eosDir,decay)
    tfile = ROOT.TFile(tfile_str)
    tree = tfile.Get('fevt/RHTree')
    nevts = tree.GetEntries()

    #tfiles = glob.glob('%s/%s_IMGcrop*.root'%(eosDir,decay))
    #print " >> %d files found."%len(tfiles)
    #tree = ROOT.TChain("fevt/RHTree")
    #for f in tfiles:
    #  tree.Add(f)
    #nevts = tree.GetEntries()
    #tree = tfiles

    neff = (nevts//1000)*1000
    #neff = int(nevts)
    #neff = 500
    #neff = neffs[j]*1000
    chunk_size = chunk_size_
    #chunk_size = int(nevts)
    if neff > nevts:
        neff = int(nevts)
        chunk_size = int(nevts)
    #neff = 1000 
    #neff = 233000
    print " >> Doing decay:", decay
    #print " >> Input file[0]:", tfiles[0]
    print " >> Total events:", nevts
    print " >> Effective events:", neff

    # EB
    readouts = [170,360]
    branches = ["EB_energy"]
    X = da.concatenate([\
                da.from_delayed(\
                    load_X(tree,i,i+chunk_size, branches, readouts, scale),\
                    shape=(chunk_size, readouts[0], readouts[1], len(branches)),\
                    dtype=np.float32)\
                for i in range(0,neff,chunk_size)])
    print " >> Expected shape:", X.shape

    # SC0
    readouts = [32,32]
    branches = ["SC_energy0"]
    X_crop0 = da.concatenate([\
                da.from_delayed(\
                    load_X(tree,i,i+chunk_size, branches, readouts, scale),\
                    shape=(chunk_size, readouts[0], readouts[1], len(branches)),\
                    dtype=np.float32)\
                for i in range(0,neff,chunk_size)])
    print " >> Expected shape:", X_crop0.shape

    # SC1
    readouts = [32,32]
    branches = ["SC_energy1"]
    X_crop1 = da.concatenate([\
                da.from_delayed(\
                    load_X(tree,i,i+chunk_size, branches, readouts, scale),\
                    shape=(chunk_size, readouts[0], readouts[1], len(branches)),\
                    dtype=np.float32)\
                for i in range(0,neff,chunk_size)])
    print " >> Expected shape:", X_crop1.shape
    X_crop0 = da.concatenate([X_crop0, X_crop1], axis=0)

    # SC0
    readouts = [32,32]
    branches = ["SC_energyT0", "SC_energyZ0"]
    X_crop_stack0 = da.concatenate([\
                da.from_delayed(\
                    load_X(tree,i,i+chunk_size, branches, readouts, scale),\
                    shape=(chunk_size, readouts[0], readouts[1], len(branches)),\
                    dtype=np.float32)\
                for i in range(0,neff,chunk_size)])
    print " >> Expected shape:", X_crop_stack0.shape

    # SC1
    readouts = [32,32]
    branches = ["SC_energyT1", "SC_energyZ1"]
    X_crop_stack1 = da.concatenate([\
                da.from_delayed(\
                    load_X(tree,i,i+chunk_size, branches, readouts, scale),\
                    shape=(chunk_size, readouts[0], readouts[1], len(branches)),\
                    dtype=np.float32)\
                for i in range(0,neff,chunk_size)])
    print " >> Expected shape:", X_crop_stack1.shape
    X_crop_stack0 = da.concatenate([X_crop_stack0, X_crop_stack1], axis=0)

    # SC_mass0 
    branches = ["SC_mass0"]
    y_mass0 = da.concatenate([\
                da.from_delayed(\
                    load_single(tree,i,i+chunk_size, branches),\
                    shape=(chunk_size,),\
                    dtype=np.float32)\
                for i in range(0,neff,chunk_size)])
    print " >> Expected shape:", y_mass0.shape

    # SC_pT0 
    branches = ["SC_pT0"]
    y_pT0 = da.concatenate([\
                da.from_delayed(\
                    load_single(tree,i,i+chunk_size, branches),\
                    shape=(chunk_size,),\
                    dtype=np.float32)\
                for i in range(0,neff,chunk_size)])
    print " >> Expected shape:", y_pT0.shape

    # SC_mass1 
    branches = ["SC_mass1"]
    y_mass1 = da.concatenate([\
                da.from_delayed(\
                    load_single(tree,i,i+chunk_size, branches),\
                    shape=(chunk_size,),\
                    dtype=np.float32)\
                for i in range(0,neff,chunk_size)])
    print " >> Expected shape:", y_mass1.shape
    y_mass0 = da.concatenate([y_mass0, y_mass1], axis=0)

    # SC_pT1 
    branches = ["SC_pT1"]
    y_pT1 = da.concatenate([\
                da.from_delayed(\
                    load_single(tree,i,i+chunk_size, branches),\
                    shape=(chunk_size,),\
                    dtype=np.float32)\
                for i in range(0,neff,chunk_size)])
    print " >> Expected shape:", y_pT1.shape
    y_pT0 = da.concatenate([y_pT0, y_pT1], axis=0)

    # Likelihood weights
    nbins = 12
    if j == 2:
      h_, xs, ys = np.histogram2d(y_mass0.compute(), y_pT0.compute(), bins=nbins, range=([0.,1.6], [50., 60.])) 
      #print(h_)
      h = 1.*h_/h_.sum()
      #print(h)
      lhood = 1./h
      lhood = lhood/(nbins*nbins) # ensures sum_massBin_i(h*lhood) = h.sum()
      #print(lhood)
      print('sum(h_norm*lhood):',(1.*h*lhood).sum())
      #wgt = da.from_array(np.array([get_weight(m, xs[:-1], lhood) for m in y_mass0.compute()]), chunks=(chunk_size,))
      wgt = da.from_array(np.array([get_weight_2d(m, pt, xs[:-1], ys[:-1], lhood) for m,pt in zip(y_mass0.compute(),y_pT0.compute())]), chunks=(chunk_size,))
    else:
      h_, xs = np.histogram(y_pT0.compute(), bins=nbins, range=[50., 60.]) 
      h = 1.*h_/h_.sum()
      #print(h)
      lhood = 1./h
      lhood = lhood/nbins # ensures sum_massBin_i(h*lhood) = h.sum()
      #print(lhood)
      print('sum(h_norm*lhood):',(1.*h*lhood).sum())
      wgt = da.from_array(np.array([get_weight(pt, xs[:-1], lhood) for pt in y_pT0.compute()]), chunks=(chunk_size,))
      #wgt = da.from_array(np.ones_like(y_mass0), chunks=(chunk_size,))*1.652721

    # SC_DR0 
    branches = ["SC_DR0"]
    y_DR0 = da.concatenate([\
                da.from_delayed(\
                    load_single(tree,i,i+chunk_size, branches),\
                    shape=(chunk_size,),\
                    dtype=np.float32)\
                for i in range(0,neff,chunk_size)])
    print " >> Expected shape:", y_DR0.shape

    ## SC1
    #readouts = [32,32]
    #branches = ["SC_energy1"]
    #X_crop1 = da.concatenate([\
    #            da.from_delayed(\
    #                load_X(tree,i,i+chunk_size, branches, readouts, scale),\
    #                shape=(chunk_size, readouts[0], readouts[1], len(branches)),\
    #                dtype=np.float32)\
    #            for i in range(0,neff,chunk_size)])
    #print " >> Expected shape:", X_crop1.shape

    # pho_pT0 
    branches = ["pho_pT0"]
    pho_pT0 = da.concatenate([\
                da.from_delayed(\
                    load_single(tree,i,i+chunk_size, branches),\
                    shape=(chunk_size,),\
                    dtype=np.float32)\
                for i in range(0,neff,chunk_size)])
    print " >> Expected shape:", pho_pT0.shape

    # pho_E0 
    branches = ["pho_E0"]
    pho_E0 = da.concatenate([\
                da.from_delayed(\
                    load_single(tree,i,i+chunk_size, branches),\
                    shape=(chunk_size,),\
                    dtype=np.float32)\
                for i in range(0,neff,chunk_size)])
    print " >> Expected shape:", pho_E0.shape

    # pho_eta0 
    branches = ["pho_eta0"]
    pho_eta0 = da.concatenate([\
                da.from_delayed(\
                    load_single(tree,i,i+chunk_size, branches),\
                    shape=(chunk_size,),\
                    dtype=np.float32)\
                for i in range(0,neff,chunk_size)])
    print " >> Expected shape:", pho_eta0.shape

    # eventId
    branches = ["eventId"]
    eventId = da.concatenate([\
                da.from_delayed(\
                    load_single(tree,i,i+chunk_size, branches),\
                    shape=(chunk_size,),\
                    dtype=np.int32)\
                for i in range(0,neff,chunk_size)])
    print " >> Expected shape:", eventId.shape

    ## Kinematics
    #branches = ["pho_pT", "pho_E", "pho_eta", "pho_phi"]
    #X_p4 = da.concatenate([\
    #            da.from_delayed(\
    #                load_single(tree,i,i+chunk_size, branches),\
    #                shape=(chunk_size,len(branches)),\
    #                dtype=np.float32)\
    #            for i in range(0,neff,chunk_size)])
    #print " >> Expected shape:", X_p4.shape

    # Class label
    label = j
    label = 0
    print " >> Class label:",label
    y = da.from_array(\
            np.full(X.shape[0], label, dtype=np.float32),\
            chunks=(chunk_size,))

    #file_out_str = "%s/%s_IMG_RH%d_n%dk_label%d.hdf5"%(eosDir,decay,int(scale),neff//1000.,label)
    file_out_str = "%s/%s_IMGcropV4_RH%d_n%dkx2_wgt.hdf5"%(eosDir,decay,int(scale),neff//1000.)
    #file_out_str = "test.hdf5"
    print " >> Writing to:", file_out_str
    #da.to_hdf5(file_out_str, {'/X': X, '/y': y, 'eventId': eventId, 'X_crop0': X_crop0, 'X_crop1': X_crop1}, compression='lzf')
    da.to_hdf5(file_out_str, {
                              #'/X': X,
                              '/y': y,
                              #'eventId': eventId,
                              'X_crop0': X_crop0,
                              'X_crop_stack0': X_crop_stack0,
                              #'X_crop1': X_crop1
                              #'X_p4': X_p4
                              'y_mass': y_mass0,
                              'y_pT': y_pT0,
                              #'y_DR': y_DR0,
                              #'pho_pT0': pho_pT0,
                              #'pho_E0': pho_E0,
                              #'pho_eta0': pho_eta0
                              'wgt': wgt
                              }, compression='lzf')

    print " >> Done.\n"
