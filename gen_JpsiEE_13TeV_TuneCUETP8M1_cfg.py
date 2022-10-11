# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: Configuration/Generator/python/JpsiMM_13TeV_TuneCUETP8M1_cfi.py --eventcontent RAWSIM --datatier GEN --fileout file:GEN_JpsiEE_13TeV_TuneCUETP8M1.root --conditions 106X_upgrade2018_realistic_v15_L1v1 --step GEN --geometry DB:Extended --beamspot Realistic25ns13TeVEarly2018Collision --era Run2_2018 --runUnscheduled --no_exec --mc -n 100 --python_filename gen_JpsiEE_13TeV_TuneCUETP8M1_cfg.py
import FWCore.ParameterSet.Config as cms

from Configuration.Eras.Era_Run2_2018_cff import Run2_2018

process = cms.Process('GEN',Run2_2018)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.Generator_cff')
process.load('IOMC.EventVertexGenerators.VtxSmearedRealistic25ns13TeVEarly2018Collision_cfi')
process.load('GeneratorInterface.Core.genFilterSummary_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(100000)
)

# Input source
process.source = cms.Source("EmptySource")

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('Configuration/Generator/python/JpsiMM_13TeV_TuneCUETP8M1_cfi.py nevts:100'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.RAWSIMoutput = cms.OutputModule("PoolOutputModule",
    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring('generation_step')
    ),
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(1),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('GEN'),
        filterName = cms.untracked.string('')
    ),
    eventAutoFlushCompressedSize = cms.untracked.int32(20971520),
    fileName = cms.untracked.string('file:GEN_JpsiEE_13TeV_TuneCUETP8M1.root'),
    outputCommands = process.RAWSIMEventContent.outputCommands,
    splitLevel = cms.untracked.int32(0)
)

# Additional output definition

# Other statements
process.genstepfilter.triggerConditions=cms.vstring("generation_step")
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '106X_upgrade2018_realistic_v15_L1v1', '')

process.oniafilter = cms.EDFilter("PythiaFilter",
    MaxEta = cms.untracked.double(2.4),
    MinEta = cms.untracked.double(-2.4),
    MinPt = cms.untracked.double(20.0),
    ParticleID = cms.untracked.int32(443),
    Status = cms.untracked.int32(2)
)

process.genJpsiToEleEleFilter = cms.EDFilter("GenJpsiToEleEleFilter",
    src       = cms.InputTag("genParticles"), #GenParticles collection as input
    nJpsis    = cms.double(1),    #Number of pdgID=25 candidates 
    elePtCut  = cms.double(1.0), #at least a GenTau with this minimum pT 
    eleEtaCut = cms.double(2.4),  #GenTau eta
    eledRCut  = cms.double(0.4)   #GenTauTau cut
)

process.generator = cms.EDFilter("Pythia8GeneratorFilter",
    PythiaParameters = cms.PSet(
        parameterSets = cms.vstring(
            'pythia8CommonSettings', 
            'pythia8CUEP8M1Settings', 
            'pythia8CharmoniumSettings', 
            'processParameters'
        ),
        processParameters = cms.vstring(
            'Charmonium:states(3S1) = 443', 
            '443:onMode = off', 
            '443:onIfAny = 11', 
            'PhaseSpace:pTHatMin = 10.'
        ),
        pythia8CUEP8M1Settings = cms.vstring(
            'Tune:pp 14', 
            'Tune:ee 7', 
            'MultipartonInteractions:pT0Ref=2.4024', 
            'MultipartonInteractions:ecmPow=0.25208', 
            'MultipartonInteractions:expPow=1.6'
        ),
        pythia8CharmoniumSettings = cms.vstring(
            'Charmonium:O(3S1)[3S1(1)] = 1.16', 
            'Charmonium:O(3S1)[3S1(8)] = 0.0119', 
            'Charmonium:O(3S1)[1S0(8)] = 0.01', 
            'Charmonium:O(3S1)[3P0(8)] = 0.01', 
            'Charmonium:gg2ccbar(3S1)[3S1(1)]g = on', 
            'Charmonium:gg2ccbar(3S1)[3S1(1)]gm = on', 
            'Charmonium:gg2ccbar(3S1)[3S1(8)]g = on', 
            'Charmonium:qg2ccbar(3S1)[3S1(8)]q = on', 
            'Charmonium:qqbar2ccbar(3S1)[3S1(8)]g = on', 
            'Charmonium:gg2ccbar(3S1)[1S0(8)]g = on', 
            'Charmonium:qg2ccbar(3S1)[1S0(8)]q = on', 
            'Charmonium:qqbar2ccbar(3S1)[1S0(8)]g = on', 
            'Charmonium:gg2ccbar(3S1)[3PJ(8)]g = on', 
            'Charmonium:qg2ccbar(3S1)[3PJ(8)]q = on', 
            'Charmonium:qqbar2ccbar(3S1)[3PJ(8)]g = on'
        ),
        pythia8CommonSettings = cms.vstring(
            'Tune:preferLHAPDF = 2', 
            'Main:timesAllowErrors = 10000', 
            'Check:epTolErr = 0.01', 
            'Beams:setProductionScalesFromLHEF = off', 
            'SLHA:keepSM = on', 
            'SLHA:minMassSM = 1000.', 
            'ParticleDecays:limitTau0 = on', 
            'ParticleDecays:tau0Max = 10', 
            'ParticleDecays:allowPhotonRadiation = on'
        )
    ),
    comEnergy = cms.double(13000.0),
    crossSection = cms.untracked.double(1256000.0),
    filterEfficiency = cms.untracked.double(0.138),
    maxEventsToPrint = cms.untracked.int32(0),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    pythiaPylistVerbosity = cms.untracked.int32(0)
)


process.mumugenfilter = cms.EDFilter("MCParticlePairFilter",
    MaxEta = cms.untracked.vdouble(2.5, 2.5),
    MinEta = cms.untracked.vdouble(-2.5, -2.5),
    MinP = cms.untracked.vdouble(2.7, 2.7),
    MinPt = cms.untracked.vdouble(0.5, 0.5),
    ParticleCharge = cms.untracked.int32(-1),
    ParticleID1 = cms.untracked.vint32(13),
    ParticleID2 = cms.untracked.vint32(13),
    Status = cms.untracked.vint32(1, 1)
)


process.ProductionFilterSequence = cms.Sequence(process.generator+process.oniafilter)

# Path and EndPath definitions
#process.generation_step = cms.Path(process.pgen)
process.generation_step = cms.Path(process.pgen+process.genJpsiToEleEleFilter)
process.genfiltersummary_step = cms.EndPath(process.genFilterSummary)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.RAWSIMoutput_step = cms.EndPath(process.RAWSIMoutput)

# Schedule definition
process.schedule = cms.Schedule(process.generation_step,process.genfiltersummary_step,process.endjob_step,process.RAWSIMoutput_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)
# filter all path with the production filter sequence
for path in process.paths:
	getattr(process,path).insert(0, process.ProductionFilterSequence)

#do not add changes to your config after this point (unless you know what you are doing)
from FWCore.ParameterSet.Utilities import convertToUnscheduled
process=convertToUnscheduled(process)


# Customisation from command line

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
