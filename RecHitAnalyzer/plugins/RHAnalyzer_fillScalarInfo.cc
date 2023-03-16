#include "MLAnalyzer/RecHitAnalyzer/interface/RecHitAnalyzer.h"

// Fill Scalar information such as MET and primary vertex ////////////////////////////////

std::vector<float> vMET_sumET_;
std::vector<float> vMET_pt_;
std::vector<float> vMET_phi_;
std::vector<float> vMET_px_;
std::vector<float> vMET_py_;
std::vector<float> vMET_pz_;

// Initialize branches _____________________________________________________//
void RecHitAnalyzer::branchesScalarInfo ( TTree* tree, edm::Service<TFileService> &fs ) {

  // Branches for scalar information
  tree->Branch("MET_sumET", &vMET_sumET_);
  tree->Branch("MET_pt",   &vMET_pt_);
  tree->Branch("MET_phi",  &vMET_phi_);
  tree->Branch("MET_px",   &vMET_px_);
  tree->Branch("MET_py",   &vMET_py_);
  tree->Branch("MET_pz",   &vMET_pz_);

  // Histograms for monitoring


} // branchesScalar()

// Fill Scalar information _________________________________________________________________//
void RecHitAnalyzer::fillScalarInfo ( const edm::Event& iEvent, const edm::EventSetup& iSetup ) {

  edm::Handle<reco::PFMETCollection> pfmet;
  iEvent.getByToken(metCollectionT_, pfmet);

   vMET_sumET_.clear();
   vMET_pt_.clear();
   vMET_phi_.clear();
   vMET_px_.clear();
   vMET_py_.clear();
   vMET_pz_.clear();

   // Fill scalar information
    vMET_sumET_ .push_back((pfmet->front()).sumEt());
    vMET_pt_   .push_back((pfmet->front()).pt());
    vMET_phi_   .push_back((pfmet->front()).phi());
    vMET_px_    .push_back((pfmet->front()).px());
    vMET_py_    .push_back((pfmet->front()).py());
    vMET_pz_    .push_back((pfmet->front()).pz());
    
    std::cout << "Met sumet " << (pfmet->front()).sumEt() << std::endl;
    std::cout << "Met pt " << (pfmet->front()).pt() << std::endl;


} // fillScalarInfo()
