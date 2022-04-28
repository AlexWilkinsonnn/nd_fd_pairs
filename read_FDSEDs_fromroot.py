import os, argparse

import ROOT
import numpy as np
from tqdm import tqdm

def main(INPUT_FILE, N, OUTPUT_DIR):
  f = ROOT.TFile.Open(INPUT_FILE, "READ")
  t = f.Get("exportdigits/seds")
  
  out_dir_Z = os.path.join(OUTPUT_DIR, 'Z')
  out_dir_U = os.path.join(OUTPUT_DIR, 'U')
  out_dir_V = os.path.join(OUTPUT_DIR, 'V')
  for dir in [out_dir_Z, out_dir_U, out_dir_V]:
    if not os.path.exists(dir):
      os.makedirs(dir)

  tree_len = N if N else t.GetEntries()
  for i, event in enumerate(tqdm(t, total=tree_len)):
    if N and i >= N:
      break

    id = event.eventid  

    arrZ = np.zeros((1, 512, 4608))
    arrU = np.zeros((1, 1024, 4608))
    arrV = np.zeros((1, 1024, 4608))
    for sed in event.sedsZ:
      arrZ[0, sed[0] + 16, sed[1] + 58] += sed[2]

    for sed in event.sedsU:
      arrU[0, sed[0] + 112, sed[1] + 58] += sed[2]

    for sed in event.sedsV:
      arrV[0, sed[0] + 112, sed[1] + 58] += sed[2]

    np.save(os.path.join(out_dir_Z, "ND_deposZ_{}.npy".format(id)), arrZ)
    np.save(os.path.join(out_dir_U, "ND_deposU_{}.npy".format(id)), arrU)
    np.save(os.path.join(out_dir_V, "ND_deposV_{}.npy".format(id)), arrV)

def parse_arguments():
  parser = argparse.ArgumentParser()

  parser.add_argument("input_file") 

  parser.add_argument("-n", type=int, default=0)
  parser.add_argument("-o", type=str, default='', help='output folder name')

  args = parser.parse_args()

  return (args.input_file, args.n, args.o)

if __name__ == '__main__':
  arguments = parse_arguments()

  if arguments[2] == '':
    raise Exception("Specify output directory")

  main(*arguments)

