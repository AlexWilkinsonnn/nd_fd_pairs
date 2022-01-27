import os, argparse, sys

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

def main(INPUT_DIR, N):
  # Play with auto masks to pick good one
  for entry in os.scandir(INPUT_DIR):
    arr_ndfd = np.load(entry.path)
    arr_fd = arr_ndfd[0, :, 4608:]

    arr_fd = arr_fd[16:-16, 58:-58]

    right_roll5 = np.roll(arr_fd, 5, 1)
    right_roll5[:, :5] = 5
    left_roll5 = np.roll(arr_fd, -5, 1)
    left_roll5[:, -5:] = 5
    peak_mask = arr_fd + right_roll5 + left_roll5
    right_roll10 = np.roll(arr_fd, 10, 1)
    right_roll10[:, :10] = 5
    left_roll10 = np.roll(arr_fd, -10, 1)
    left_roll10[:, -10:] = 5
    peak_mask = peak_mask + right_roll10 + left_roll10

    roll1 = np.roll(peak_mask, 1, 0)
    roll1[:1] = 5
    roll2 = np.roll(peak_mask, -1, 0)
    roll2[-1:] = 5
    peak_mask = peak_mask + roll1 + roll2
    
    peak_mask = (peak_mask > 65)

    fig, ax = plt.subplots(1, 2)

    ax[0].imshow(arr_fd.T, cmap='viridis', aspect='auto', interpolation='none', origin='lower')
    ax[0].set_title("FD")

    ax[1].imshow(peak_mask.T, cmap='viridis', aspect='auto', interpolation='none', origin='lower')
    ax[1].set_title("Mask")

    fig.tight_layout()
    plt.show()

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("input_dir")

    parser.add_argument("-n", type=int, default=0, dest='n')

    args = parser.parse_args()

    return (args.input_dir, args.n)

if __name__ == "__main__":
    arguments = parse_arguments()
    main(*arguments)

