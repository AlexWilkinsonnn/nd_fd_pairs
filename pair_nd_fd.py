import os, argparse, csv, re, sys

import numpy as np

def main(FD_DIR, ND_DIR, OUT_DIR): # Verify all is looking good then do matching
  N_fd = len(os.listdir(FD_DIR))
  N_nd = len(os.listdir(ND_DIR))
  if N_fd != N_nd:
    print("WARNING: fd_dir and nd_dir have a different number of files.")
    raise Exception

  if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

  sorted_scandir = lambda dir : sorted(os.scandir(dir), key=lambda entry: entry.name)
  for i, (entry_fd, entry_nd) in enumerate(zip(sorted_scandir(FD_DIR), sorted_scandir(ND_DIR))):
    print("[{}/{}]".format(i + 1, N_fd), end='\r')

    if not re.match("^FD_detsim_[0-9]+.csv$", entry_fd.name):
      print("WARNING: invalid filename: {}".format(entry_fd.name))
      raise Exception
    if not re.match("^ND_detsim_[0-9]+.npy$", entry_nd.name):
      print("WARNING: invalid filename: {}".format(entry_nd.name))
      raise Exception

    id_fd = int(entry_fd.name.split('_')[-1].split('.')[0])
    id_nd = int(entry_nd.name.split('_')[-1].split('.')[0])

    if id_fd != id_nd:
      print("WARNING: mismatching indices: {} and {}".format(id_fd, id_nd))
      raise Exception

    arrA = np.load(entry_nd.path)
    # Align ND packets with FD waveforms
    arrA = np.roll(arrA, 52, 1)
    arrA[:, :, (4492 + 58):(4492 + 58 + 52)] = 0

    arrB = np.zeros((1, 512, 4608))
    with open(entry_fd.path, 'r') as f:
      f_reader = csv.reader(f)
      for line in f_reader:
        arrB[0, int(line[0]) + 16, int(line[1]) + 112] = float(line[2])

    arr_aligned = np.concatenate([arrA, arrB], 2)
    np.save(os.path.join(OUT_DIR, "{}ndfd.npy".format(id_fd)), arr_aligned)

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("fd_dir")
    parser.add_argument("nd_dir")
    parser.add_argument("out_dir")

    # group1 = parser.add_mutually_exclusive_group()
    # group1.add_argument("--induction", action='store_true')
    # group1.add_argument("--collection", action='store_true')

    args = parser.parse_args()

    return (args.fd_dir, args.nd_dir, args.out_dir)

if __name__ == "__main__":
    arguments = parse_arguments()
    main(*arguments)
