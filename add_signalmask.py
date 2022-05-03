import os, argparse, re

import numpy as np
from matplotlib import pyplot as plt
from tqdm import tqdm
import sparse

def load_nd_fd(entry_nd, dir_fd, only_nd=False):
    arr_nd = sparse.load_npz(entry_nd.path).todense()

    if only_nd:
        return arr_nd

    num = re.match("([0-9]+)", entry_nd.name)[0]
    fd_name = str(num) + 'fd.npy'
    arr_fd = np.load(os.path.join(dir_fd, fd_name))

    return arr_nd, arr_fd

def get_nd_mask(arr_nd, max_tick_shift, max_ch_shift):
    nd_mask = np.copy(arr_nd)

    for tick_shift in range(1, max_tick_shift + 1):
        nd_mask[:, tick_shift:] += arr_nd[:, :-tick_shift]
        nd_mask[:, :-tick_shift] += arr_nd[:, tick_shift:]
    
    for ch_shift in range(1, max_ch_shift + 1):
        nd_mask[ch_shift:, :] += nd_mask[:-ch_shift, :]
        nd_mask[:-ch_shift, :] += nd_mask[ch_shift:, :]

    return nd_mask

def main(INPUT_DIR_ND, INPUT_DIR_FD, COLLECTION, PLOT):
    for entry_nd in tqdm(os.scandir(INPUT_DIR_ND)):
        if PLOT:
            arr_nd, arr_fd = load_nd_fd(entry_nd, INPUT_DIR_FD)
        else:
            arr_nd = load_nd_fd(entry_nd, INPUT_DIR_FD, True)

        if COLLECTION:
            nd_mask = get_nd_mask(arr_nd[0], 15, 1)
        else: # induction signal lingers for longer so use a larger signal mask
            nd_mask = get_nd_mask(arr_nd[0], 25, 2)

        nd_mask = nd_mask.astype(bool).astype(float)

        if PLOT:
            fig, ax = plt.subplots(1, 2)
            
            ax[0].imshow(nd_mask.T, cmap=plt.cm.gray, interpolation='none', aspect='auto')
            ax[1].imshow(arr_fd[0].T, cmap='seismic', interpolation='none', aspect='auto', vmin=-np.max(np.abs(arr_fd)), vmax=np.max(np.abs(arr_fd)))
            # ax[1].imshow(np.ma.masked_where(arr_nd[0] == 0, arr_nd[0]).T, cmap='viridis', aspect='auto', interpolation='none')
            fig.tight_layout()

            plt.show()
            
            continue

        arr_nd_mask = np.concatenate((arr_nd, np.expand_dims(nd_mask, axis=0)), 0)

        S_nd_mask = sparse.COO.from_numpy(arr_nd_mask)
        sparse.save_npz(entry_nd.path, S_nd_mask)
    
def parse_arguments():
    parser = argparse.ArgumentParser(description="add a signal mask made with the nd packets")

    parser.add_argument("input_dir_nd")
    parser.add_argument("input_dir_fd")

    parser.add_argument("--plot", action='store_true')

    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument("--induction", action='store_true')
    group1.add_argument("--collection", action='store_true')

    args = parser.parse_args()

    return (args.input_dir_nd, args.input_dir_fd, args.collection, args.plot)

if __name__ == "__main__":
    arguments = parse_arguments()
    main(*arguments)

