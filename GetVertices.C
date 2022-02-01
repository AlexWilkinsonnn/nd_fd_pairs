#include "TG4Event.h"

void GetVertices() {
  TFile* fileEvents = TFile::Open("/unix/dune/awilkinson/extrapolation/nd_fd_pairs/data/output_1-8_radi_numuCC/edepsim/edep_CC_numu.root");
  TTree* events = (TTree*)fileEvents->Get("EDepSimEvents");

  // TTree* events = (TTree*)gFile->Get("EdepSimEvents");

  TG4Event* event = new TG4Event();
  events->SetBranchAddress("Event", &event);

  ofstream outFile;
  outFile.open("output_1-8_radi_numuCC_edepsim_vertices.txt");
  
  int nEntries = events->GetEntries();
  for (int i = 0; i < nEntries; i++) {
    int n = events->GetEntry(i);
    if (n <= 0) {
      break;
    }

    // if (event->Primaries.size() != 1) {
    //   cout << "\n\n\n" <<  event->Primaries.size() << "\n\n\n";
    // }

    outFile << i << "," << event->Primaries[0].GetPosition().X() << "," << 
      event->Primaries[0].GetPosition().Y() << "," << 
      event->Primaries[0].GetPosition().Z() << "," << 
      event->Primaries[0].GetPosition().T() << "\n";

    // cout << i << "," << event->Primaries[0].GetPosition().X() << "," << 
    //   event->Primaries[0].GetPosition().Y() << "," << 
    //   event->Primaries[0].GetPosition().Z() << "," << 
    //   event->Primaries[0].GetPosition().T() << "\n";
  }
  outFile.close();
}

int main() {
  GetVertices();
}