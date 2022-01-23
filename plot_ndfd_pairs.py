import os, argparse, sys

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

plt.rc('font', family='serif')

def main(INPUT_DIR, N):
  diffs = []
  for i, entry in enumerate(os.scandir(INPUT_DIR)):
    if not entry.name.endswith(".npy"):
      continue
    if N and i >=N:
      break
    
    print(entry.name, end='\r')

    arr_ndfd = np.load(entry.path)
    arr_nd = arr_ndfd[0, :, :4608]
    arr_fd = arr_ndfd[0, :, 4608:]

    arr_nd = arr_nd[16:-16, 58:-58]
    arr_fd = arr_fd[16:-16, 58:-58]
    
    # Looking at tick shift (coming from somewhere inside WireCell that can de accessed in LArSoft so stuck with for now)
    # for i, (row_nd, row_fd) in enumerate(zip(arr_nd, arr_fd)):
    #   if row_nd.sum() > 100:
    #     if (np.max(np.argwhere(row_nd > 0)) - np.min(np.argwhere(row_nd > 0))) > 10:
    #       continue
    #     if np.abs(np.argmax(row_fd) - np.argmax(row_nd)) > 52:
    #       continue
    #     if np.abs(np.argmax(row_fd) - np.argmax(row_nd)) < 47:
    #       continue
    #     diffs.append(np.argmax(row_fd) - np.argmax(row_nd))
    # # if entry.name != "20ndfd.npy":
    # #   continue
    # continue

    # Manipulate array
    # arr_fd = np.flip(arr_fd, 1)
    # # arr_fd = np.roll(arr_fd, 103, 1)
    # arr_nd_newres = np.zeros((480, 8984))
    # for i_ch, col in enumerate(arr_nd):
    #   for i_tick, adc in enumerate(col):
    #     if adc != 0:
    #       # arr_nd_newres[i_ch, int(2*i_tick) - 4:int(2*i_tick)] += adc
    #       arr_nd_newres[i_ch, int(2*i_tick)] = adc
    # # for i_tick, row in enumerate(arr_nd_newres.T):
    # #   if arr_nd_newres[:, i_tick].sum() != 0: 
    # #     print('\n')
    # #     print(i_tick)
    # #     break
    # arr_nd = arr_nd_newres[:, 3251:3251 + 4492]

    fig, ax = plt.subplots(1, 2)

    ax[0].imshow(np.ma.masked_where(arr_nd == 0, arr_nd).T, cmap='viridis', aspect='auto', interpolation='none', origin='lower')
    ax[0].set_title("ND")

    ax[1].imshow(arr_fd.T, cmap='viridis', aspect='auto', interpolation='none', origin='lower')
    ax[1].set_title("FD")

    fig.tight_layout()
    plt.show()

    ch = (0, 0)
    for i, col in enumerate(arr_nd):
      if np.abs(col).sum() > ch[1]:
        ch = (i, np.abs(col).sum())
    ch = ch[0]

    ticks_nd = arr_nd[ch, :]
    ticks_fd = arr_fd[ch, :]
    ticks = np.arange(1, arr_nd.shape[1] + 1)

    fig, ax = plt.subplots(tight_layout=True)

    ax.hist(ticks, bins=len(ticks), weights=ticks_nd, histtype='step', linewidth=0.7, color='b', label='ND')
    ax.hist(ticks, bins=len(ticks), weights=ticks_fd, histtype='step', linewidth=0.7, color='r', label='FD')
    ax.set_ylabel("ADC", fontsize=14)
    ax.set_xlabel("tick", fontsize=14)

    plt.title("Channel {} in ROP".format(ch), fontsize=16)

    handles, labels = ax.get_legend_handles_labels()
    new_handles = [Line2D([], [], c=h.get_edgecolor()) for h in handles]
    plt.legend(handles=new_handles, labels=labels, prop={'size': 12})

    plt.show()

  # Looking at tick shift  
  # print(diffs)
  # print("{} +- {}".format(np.mean(diffs), np.std(diffs)))

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

