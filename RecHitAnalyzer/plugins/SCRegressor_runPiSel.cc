#include "MLAnalyzer/RecHitAnalyzer/interface/SCRegressor.h"

// Initialize branches _____________________________________________________//
void SCRegressor::branchesPiSel ( TTree* tree, edm::Service<TFileService> &fs )
{
  //hSC_pT = fs->make<TH1F>("SC_pT", "Pt", 65, 30., 160.);
  //hSC_mass = fs->make<TH1F>("SC_mass", "m_{SC};m_{SC}",50, 0., 0.5);
  //hdR = fs->make<TH1F>("dR_seed_subJet", "#DeltaR(seed,subJet);#DeltaR",50, 0., 50.*0.0174);
  //hdEta = fs->make<TH1F>("dEta_seed_subJet", "#Delta#eta(seed,subJet);#Delta#eta",50, 0., 50.*0.0174);
  //hdPhi = fs->make<TH1F>("dPhi_seed_subJet", "#Delta#phi(seed,subJet);#Delta#phi",50, 0., 50.*0.0174);
  hdPhidEtaM = fs->make<TH3F>("dPhidEta_GG", "#Delta(#phi,#eta,m);#Delta#phi(#gamma,#gamma);#Delta#eta(#gamma,#gamma);m",
      6, 0., 6.*0.0174, 6, 0., 6.*0.0174, 16., 0.,1.6);
  hnPho = fs->make<TH2F>("nPho", "N(m_{#pi},p_{T,#pi})_{reco};m_{#pi^{0}};p_{T,#pi^0}",
      16, 0., 1.6, 17, 15., 100.);
  hMinDRgenRecoPho = fs->make<TH1F>("minDRgenRecoPho", "#DeltaR(#gamma_{gen},#gamma_{reco})_{min};#DeltaR;N", 100, 0., 25*0.0174);
  hMinDRrecoPtoGenPt = fs->make<TH1F>("minDRrecoPtoGenPt", "#DeltaR(#gamma_{gen},#gamma_{reco})_{min}, p_{T,reco}/p_{T,gen};p_{T,reco}/p_{T,gen};N", 60, -10., 10.);

  tree->Branch("SC_mass",   &vSC_mass_);
  tree->Branch("SC_DR",     &vSC_DR_);
  tree->Branch("SC_E",      &vSC_E_);
  tree->Branch("SC_pT",     &vSC_pT_);
  tree->Branch("SC_eta",    &vSC_eta_);
  tree->Branch("SC_phi",    &vSC_phi_);
  tree->Branch("SC_vtx",    &vSC_vtx_);
  tree->Branch("SC_vtxT",    &vSC_vtxT_);
  tree->Branch("SC_vtxZ",    &vSC_vtxZ_);
  tree->Branch("SC_dvtx",   &vSC_dvtx_);
  tree->Branch("SC_recoIdx",   &vSC_recoIdx_);
  tree->Branch("SC_boost",   &vSC_boost_);

}

// Define struct to handle mapping for gen pi0<->matched reco photons<->matched presel photons
struct pi0_map {
  unsigned int idx;
  std::vector<unsigned int> matchedRecoPhoIdxs;
  std::vector<unsigned int> matchedPreselPhoIdxs;
};
std::vector<pi0_map> vPi0s;

// Calculate magnitude of distance vector from prodn vtx iGen to prodn vtx iGenPho
float dv( reco::GenParticleRef iGen, const reco::Candidate* iGenPho ) {
  float dx = abs(iGen->vx()-iGenPho->vx());
  float dy = abs(iGen->vy()-iGenPho->vy());
  float dz = abs(iGen->vz()-iGenPho->vz());
  float dvtx_ = sqrt(dx*dx + dy*dy + dz*dz);
  return dvtx_;
}

// Run event selection ___________________________________________________________________//
bool SCRegressor::runPiSel ( const edm::Event& iEvent, const edm::EventSetup& iSetup ) {

  edm::Handle<PhotonCollection> photons;
  iEvent.getByToken(photonCollectionT_, photons);

  edm::Handle<reco::GenParticleCollection> genParticles;
  iEvent.getByToken(genParticleCollectionT_, genParticles);

  ////////// Gen-level validation //////////

  // Identify valid gen pi0s decays from the event
  // (Assumed that event contains multiple pi0 guns)
  // WARNING: the MINIAODSIM prunedGenParticles collection clips particles with pt < 10 GeV from the truth table!
  float dR;
  float vtx, dvtx;
  std::vector<unsigned int> vGenPi0Idxs;
  for ( unsigned int iG = 0; iG < genParticles->size(); iG++ ) {

    reco::GenParticleRef iGen( genParticles, iG );
    // ID cuts
    //if ( debug ) std::cout << " >> pdgId:"<< iGen->pdgId() << " status:" << iGen->status() << " nDaughters:" << iGen->numberOfDaughters() << " vtx:" << vtx <<std::endl;
    if ( std::abs(iGen->pdgId()) != 111 ) continue;
    vtx = sqrt( iGen->vx()*iGen->vx() + iGen->vy()*iGen->vy() + iGen->vz()*iGen->vz() );
    if ( debug ) std::cout << " >> pdgId:111 nDaughters:" << iGen->numberOfDaughters() << " mass:" << iGen->mass() << " pt:" << iGen->pt() << " eta:" << iGen->eta() << " vtx:" << vtx << std::endl;
    for ( unsigned int iD = 0; iD < iGen->numberOfDaughters(); iD++ ) {
      const reco::Candidate* iGenPho = iGen->daughter(iD);
      vtx = sqrt( iGenPho->vx()*iGenPho->vx() + iGenPho->vy()*iGenPho->vy() + iGenPho->vz()*iGenPho->vz() );
      dvtx = dv( iGen, iGenPho );
      if ( debug ) std::cout << "  >> iD[" << iD <<"]: pdgId:" << iGenPho->pdgId() << " pt:" << iGenPho->pt() << " eta:" << iGenPho->eta() << " vtx:" << vtx << " dvtx:" << dvtx << std::endl;
    }
    if ( iGen->numberOfDaughters() != 2 ) continue;
    //if ( iGen->mass() < 0.8 ) continue;

    // Minimize producing images where second reco photon is out of image window
    // Work backwards from: image window size => reco DR requirement => gen DR requirement
    dR = reco::deltaR( iGen->daughter(0)->eta(),iGen->daughter(0)->phi(), iGen->daughter(1)->eta(),iGen->daughter(1)->phi() );
    if ( debug ) std::cout << "  >> dR(daughters,xtals):" << dR/0.0174 << std::endl;
    //if ( dR > 10*.0174 ) continue;

    vGenPi0Idxs.push_back( iG );

  } // genParticles
  if ( debug ) std::cout << " >> vGenPi0Idxs.size: " << vGenPi0Idxs.size() << std::endl;
  if ( vGenPi0Idxs.empty() ) return false;

  // Check that pi0s are well separated in event
  // Reject whole event otherwise
  bool isIsolated = true;
  for ( unsigned int i = 0; i < vGenPi0Idxs.size(); i++ ) {
    reco::GenParticleRef iGen( genParticles, vGenPi0Idxs[i] );
    for ( unsigned int j = i+1; j < vGenPi0Idxs.size(); j++ ) {
      if ( j <= i ) continue;
      reco::GenParticleRef jGen( genParticles, vGenPi0Idxs[j] );
      dR = reco::deltaR( iGen->eta(),iGen->phi(), jGen->eta(),jGen->phi() );
      if ( dR < 0.4 ) {
        isIsolated = false;
        //std::cout << "dR:" << dR << std::endl;
        break;
      }
    } // jGen
  } // iGen
  if ( !isIsolated ) return false;

  ////////// Build gen pi0-reco photon mapping //////////

  float ptCut = 15., etaCut = 1.44;
  //float ptCut = 10., etaCut = 1.44;

  // Create mapping between gen pi0<->matched reco photons<->matched presel photons
  // For each pi0, first find "reco" photons matched to pi0's daughter gen photons,
  // then check if that reco photon passes photon preselection criteria
  float minDR = 100.;
  float minDR_fpt = -10.;
  int minDR_idx = -1;
  vPi0s.clear();
  // Loop over valid gen pi0 idxs
  for ( auto& iPi0 : vGenPi0Idxs ) {

    reco::GenParticleRef iGen( genParticles, iPi0 );
    if ( debug ) std::cout << " >> pi0[" << iPi0 << "]" << " pt:" << iGen->pt() << " eta:" << iGen->eta() << std::endl;

    // Get gen photon daughters of pi0
    std::vector<unsigned int> vMatchedRecoPhoIdxs;
    std::vector<unsigned int> vMatchedPreselPhoIdxs;
    for ( unsigned int iD = 0; iD < iGen->numberOfDaughters(); iD++ ) {

      const reco::Candidate* iGenPho = iGen->daughter(iD);

      // For each gen photon daughter, do dR match to closest reco photon
      minDR = 100.;
      minDR_fpt = -10;
      minDR_idx = -1;
      if ( debug ) std::cout << "  >> iD[" << iD << "]" << " pt:" << iGenPho->pt() << " eta:" << iGenPho->eta() << std::endl;
      for ( unsigned int iP = 0; iP < photons->size(); iP++ ) {

        PhotonRef iPho( photons, iP );

        // Definition of a "reco" photon--highly subject to interpretation
        //if ( iPho->pt() < 5. ) continue;
        if ( iPho->pt() < 10. ) continue; // pat/miniaod threshold is pt > 10 GeV

        dR = reco::deltaR( iPho->eta(),iPho->phi(), iGenPho->eta(),iGenPho->phi() );
        if ( dR > minDR ) continue;

        minDR = dR;
        minDR_idx = iP;
        minDR_fpt = iPho->pt()/iGenPho->pt();
        if ( debug ) std::cout << "   >> minDR_idx:" << minDR_idx << " " << minDR << " pt:" << iPho->pt() << " eta:" << iPho->eta() << std::endl;

      } // reco photons
      hMinDRgenRecoPho->Fill( minDR );
      hMinDRrecoPtoGenPt->Fill( minDR_fpt );

      // Require minimum dR to declare match
      // Protects against matching to PU, although not a major issue since these will likely fail preselection
      // minDR only needs to be generous enough so that one of the gen photons match to a reco photon for analysis
      if ( debug && minDR > 0.04 && minDR < 0.08 ) std::cout << "   !!!! minDR > 0.04 && minDR < 0.08" << std::endl;
      if ( minDR > 2*0.04 ) continue;
      //if ( minDR > 2*0.08 ) continue;

      // Declare reco photon matching to gen pi0: only store unique reco idxs
      if ( std::find(vMatchedRecoPhoIdxs.begin(), vMatchedRecoPhoIdxs.end(), minDR_idx) != vMatchedRecoPhoIdxs.end() ) continue;
      vMatchedRecoPhoIdxs.push_back( minDR_idx );
      if ( debug ) std::cout << "   >> !minDR_idx:" << minDR_idx << " f_pt(reco/gen):" << minDR_fpt << std::endl;

      // Check if matched reco photon passes preselection:
      PhotonRef iPho( photons, minDR_idx );
      if ( std::abs(iPho->pt()) <= ptCut ) continue;
      if ( std::abs(iPho->eta()) >= etaCut ) continue;
      //if ( std::abs(iPho->eta()) > 2.4 ) continue;
      //if ( std::abs(iPho->eta()) < 1.7 ) continue;

      ///*
      if ( iPho->full5x5_r9() <= 0.5 ) continue;
      if ( iPho->hadTowOverEm() >= 0.08 ) continue;
      if ( iPho->hasPixelSeed() == true ) continue;
      //if ( iPho->passElectronVeto() == true ) continue;
      //if ( iPho->userFloat("phoChargedIsolation")/std::abs(iPho->pt()) > 0.3 ) continue;

      if ( iPho->full5x5_r9() <= 0.85 ) {
        if ( iPho->full5x5_sigmaIetaIeta() >= 0.015 ) continue;
        //if ( iPho->userFloat("phoPhotonIsolation") >= 4.0 ) continue;
        if ( iPho->photonIso() >= 4.0 ) continue;
        if ( iPho->trkSumPtHollowConeDR03() >= 6. ) continue;
        //if ( iPho->trackIso() >= 6. ) continue;
      }
      //*/
      vMatchedPreselPhoIdxs.push_back( minDR_idx );
      if ( debug ) std::cout << " >> presel photon: pT: " << iPho->pt() << " eta: " << iPho->eta() << std::endl;

    } // gen photon daughters of pi0
    dR = reco::deltaR( iGen->daughter(0)->eta(),iGen->daughter(0)->phi(), iGen->daughter(1)->eta(),iGen->daughter(1)->phi() );
    if ( debug ) std::cout << " >> gen dR:" << dR << std::endl;

    // Store this mapping
    pi0_map iPi0_obj = { iPi0, vMatchedRecoPhoIdxs, vMatchedPreselPhoIdxs };
    vPi0s.push_back( iPi0_obj );

  } // gen pi0s

  ////////// Apply selection criteria //////////

  // Ensure only 1 presel photon associated to each gen pi0
  // Missing here: a check if no other reco photons (e.g. PU photons) are around the presel photon
  // NOTE: only unique reco idxs are stored
  vPreselPhoIdxs_.clear();
  for ( auto const& iPi0 : vPi0s ) {

    if ( debug ) std::cout << " >> pi0[" << iPi0.idx
      << "], reco size:" << iPi0.matchedRecoPhoIdxs.size()
      << ", presel size:"<< iPi0.matchedPreselPhoIdxs.size()<< std::endl;

    // No presel OR >1 presel photon
    if ( iPi0.matchedPreselPhoIdxs.empty() || iPi0.matchedPreselPhoIdxs.size() > 1 ) continue;

    // 1 presel photon: if 2 reco photons i,j matched to same pi0, ensure dR(i,j) is within image window
    // Optionally: can reject photons when there is a *gen-matched* reco photon nearby
    //    NOTE: this implementation will NOT work for PU photons, or other photons which fail the gen matching.
    if ( iPi0.matchedRecoPhoIdxs.size() == 2 ) {
      PhotonRef iPho( photons, iPi0.matchedRecoPhoIdxs[0] );
      PhotonRef jPho( photons, iPi0.matchedRecoPhoIdxs[1] );
      dR = std::abs( reco::deltaR( iPho->eta(),iPho->phi(), jPho->eta(),jPho->phi() ) );
      if ( dR > 16*.0174 ) continue; // outside of image window
    }
    vPreselPhoIdxs_.push_back( iPi0.matchedPreselPhoIdxs[0] );

  }
  if ( debug ) std::cout << " >> PreselPhos.size: " << vPreselPhoIdxs_.size() << std::endl;
  if ( vPreselPhoIdxs_.empty() ) return false;

  // Photon gets passed to cropping routine.
  if ( debug ) std::cout << " >> Passed selection. " << std::endl;
  return true;

} // runPiSel()

// Fill branches ___________________________________________________________________//
void SCRegressor::fillPiSel ( const edm::Event& iEvent, const edm::EventSetup& iSetup )
{
  edm::Handle<PhotonCollection> photons;
  iEvent.getByToken(photonCollectionT_, photons);

  edm::Handle<reco::GenParticleCollection> genParticles;
  iEvent.getByToken(genParticleCollectionT_, genParticles);

  ////////// Store gen-level pi0 kinematics //////////

  vSC_DR_.clear();
  vSC_mass_.clear();
  vSC_E_.clear();
  vSC_pT_.clear();
  vSC_eta_.clear();
  vSC_phi_.clear();
  vSC_vtx_.clear();
  vSC_vtxT_.clear();
  vSC_vtxZ_.clear();
  vSC_dvtx_.clear();
  vSC_recoIdx_.clear();
  vSC_boost_.clear();
  float vtx, dvtx;
  float vtxT, vtxZ;
  float dEta, dPhi, dR, mPi0, ptPi0;
  float recoDR;
  int recoDR_idx;
  for ( auto const& iPi0 : vPi0s ) {

    // Skip pi0s which are not valid for regression
    if ( iPi0.matchedPreselPhoIdxs.empty() || iPi0.matchedPreselPhoIdxs.size() > 1 ) continue;
    if ( std::find(vRegressPhoIdxs_.begin(), vRegressPhoIdxs_.end(), iPi0.matchedPreselPhoIdxs[0]) == vRegressPhoIdxs_.end() ) continue;

    reco::GenParticleRef iGen( genParticles, iPi0.idx );
    mPi0 = iGen->mass();
    ptPi0 = iGen->pt();
    dR = std::abs( reco::deltaR( iGen->daughter(0)->eta(),iGen->daughter(0)->phi(), iGen->daughter(1)->eta(),iGen->daughter(1)->phi() ) );
    dEta = std::abs( iGen->daughter(0)->eta() - iGen->daughter(1)->eta() );
    dPhi = std::abs( reco::deltaPhi( iGen->daughter(0)->phi(), iGen->daughter(1)->phi() ) );
    //if ( debug ) std::cout << " >> m0:" << mPi0 << " dR:" << dR << " dPhi:" << dPhi << std::endl;
    //if ( debug ) std::cout << " >> m0:" << mPi0 << " eta:" << iGen->eta() << " dRxtal:" << dR/0.0174 << " dPhixtal:" << dPhi/0.0174 << " dEtaxtal:" << dEta/0.0174 << std::endl;
    //std::cout << " >> m0:" << mPi0 << " eta:" << iGen->eta() << " dX:" << std::abs(iGen->daughter(0)->x()-iGen->daughter(1)->x()) 
    //  << " dY:" << std::abs(iGen->daughter(0)->y()-iGen->daughter(1)->y()) << std::endl;

    vSC_DR_.push_back( dR );
    vSC_mass_.push_back( mPi0 );
    vSC_E_.push_back( iGen->energy() );
    vSC_pT_.push_back( iGen->pt() );
    vSC_eta_.push_back( iGen->eta() );
    vSC_phi_.push_back( iGen->phi() );

    // WARNING: vertex coords in cmssw are in units of cm
    // whereas in Pythia ctau units are in mm!
    for ( unsigned int iD = 0; iD < iGen->numberOfDaughters(); iD++ ) {
      const reco::Candidate* iGenPho = iGen->daughter(iD);
      // Get distance from IP(0,0,0) to diphoton prodn vtx (same as pi0 decay vtx)
      vtx = sqrt( iGenPho->vx()*iGenPho->vx() + iGenPho->vy()*iGenPho->vy() + iGenPho->vz()*iGenPho->vz() ); // cm
      vtxT = sqrt( iGenPho->vx()*iGenPho->vx() + iGenPho->vy()*iGenPho->vy() ); // cm
      vtxZ = sqrt( iGenPho->vz()*iGenPho->vz() ); // cm
      // Get distance from pi0 prod vtx to pi0 decay vtx -> actual pi0 decay length in lab frame cT = gamma*cTau
      // where gamma is the Lorentz gamma and Tau is the proper lifetime (i.e. lifetime of pi0 in its rest frame)
      dvtx = dv( iGen, iGenPho ); // cm
    }
    vSC_vtx_.push_back( vtx );
    vSC_vtxT_.push_back( vtxT );
    vSC_vtxZ_.push_back( vtxZ );
    vSC_dvtx_.push_back( dvtx );
    vSC_boost_.push_back( iGen->energy()/mPi0 ); // Lorentz gamma

    //hPt->Fill( ptPi0 );
    hdPhidEtaM->Fill( dPhi, dEta, mPi0 );
    //hnPho->Fill( mPi0, iGen->pt() );
    hnPho->Fill( mPi0, ptPi0 );
    //hSC_mass->Fill( mPi0 );

    // Get index to dR-matched preselected photon
    recoDR = 2*0.04;
    recoDR_idx = -1;
    // Want vA_recoIdx_ to store vector index in vRegressPhoIdxs_
    // i.e., vRegressPhoIdxs_[0]:leading reco pho, vRegressPhoIdxs_[1]:sub-leading reco pho
    // not position in original photon collection
    for ( unsigned int iP = 0; iP < vRegressPhoIdxs_.size(); iP++ ) {
      PhotonRef iPho( photons, vRegressPhoIdxs_[iP] );
      dR = std::abs( reco::deltaR(iGen->eta(),iGen->phi(), iPho->eta(),iPho->phi()) );
      if ( dR < recoDR ) {
        recoDR = dR;
        recoDR_idx = iP;
      }
    } // reco pho
    vSC_recoIdx_.push_back( recoDR_idx );

  } // gen pi0s

} // fillPiSel()
