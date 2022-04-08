import os, argparse

import ROOT
import numpy as np
from tqdm import tqdm

def main(INPUT_FILE, N, OUTPUT_DIR):
  f = ROOT.TFile.Open(INPUT_FILE, "READ")
  t = f.Get("exportdigits/digits")
  
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
    for ch, dig_vec in enumerate(event.digit_vecsZ):
      for tick, adc in enumerate(dig_vec):
        arrZ[0, ch + 16, tick + 58] = adc
      
    for ch, dig_vec in enumerate(event.digit_vecsU):
      for tick, adc in enumerate(dig_vec):
        arrU[0, ch + 112, tick + 58] = adc

    for ch, dig_vec in enumerate(event.digit_vecsV):
      for tick, adc in enumerate(dig_vec):
        arrV[0, ch + 112, tick + 58] = adc
        
    np.save(os.path.join(out_dir_Z, "FD_detsimZ_{}.npy".format(id)), arrZ)
    np.save(os.path.join(out_dir_U, "FD_detsimU_{}.npy".format(id)), arrU)
    np.save(os.path.join(out_dir_V, "FD_detsimV_{}.npy".format(id)), arrV)

def parse_arguments():
  parser = argparse.ArgumentParser()

  parser.add_argument("input_file") 

  parser.add_argument("-n", type=int, default=0)
  parser.add_argument("-o", type=str, default='', help='output folder name')
  parser.add_argument("--plot", action='store_true')

  args = parser.parse_args()

  return (args.input_file, args.n, args.o)

if __name__ == '__main__':
  arguments = parse_arguments()

  if arguments[2] == '':
    raise Exception("Specify output directory")

  main(*arguments)

