import os, argparse, csv

import numpy as np
from matplotlib import pyplot as plt

def main(INPUT_DIR, N):
  for i, entry in enumerate(os.scandir(INPUT_DIR)):
    if not entry.name.endswith(".npy"):
      continue
    if N and i >=N:
      break
    
    print(entry.name, end='\r')

    arr_ndfd = np.load(entry.path)
    arr_nd = arr_ndfd[0, :, :4608]
    arr_fd = arr_ndfd[0, :, 4608:]

    arr_nd = arr_nd[16:-16, 112:-112]
    arr_fd = arr_fd[16:-16, 112:-112]

    fig, ax = plt.subplots(1, 2)

    ax[0].imshow(np.ma.masked_where(arr_nd == 0, arr_nd).T, cmap='viridis', aspect='auto', interpolation='none', origin='lower')
    ax[0].set_title("ND")

    ax[1].imshow(arr_fd.T, cmap='viridis', aspect='auto', interpolation='none', origin='lower')
    ax[1].set_title("FD")

    fig.tight_layout()
    plt.show()
    
def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("input_dir")

    parser.add_argument("-n", type=int, default=0, dest='n')

    # group1 = parser.add_mutually_exclusive_group()
    # group1.add_argument("--induction", action='store_true')
    # group1.add_argument("--collection", action='store_true')

    args = parser.parse_args()

    return (args.input_dir, args.n)

if __name__ == "__main__":
    arguments = parse_arguments()
    main(*arguments)

