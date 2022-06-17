import os, argparse

import numpy as np
from tqdm import tqdm
import sparse

def remove_padding(wireplane_arr):
    if wireplane_arr.shape[1] == 512:
        wireplane_arr = wireplane_arr[:, 16:-16, :]
    elif wireplane_arr.shape[1] == 1024:
        wireplane_arr = wireplane_arr[:, 112:-112, :]

    if wireplane_arr.shape[2] == 4608:
        wireplane_arr = wireplane_arr[:, :, 58:-58]

    return wireplane_arr

def main(ND_INPUT_DIR, ND_OUTPUT_DIR, FD_INPUT_DIR, FD_OUTPUT_DIR, REMOVE_MASK):
    num_skipped = 0

    sorted_scandir = lambda dir : sorted(os.scandir(dir), key=lambda entry: entry.name)
    sorted_nd_dir_paths = [ entry.path for entry in list(sorted_scandir(ND_INPUT_DIR)) ]
    sorted_fd_dir_paths = [ entry.path for entry in list(sorted_scandir(FD_INPUT_DIR)) ]

    for entry_nd_path, entry_fd_path in tqdm(zip(sorted_nd_dir_paths, sorted_fd_dir_paths)):
        entry_nd_name, entry_fd_name = os.path.basename(entry_nd_path), os.path.basename(entry_fd_path)
        id_fd = int(entry_fd_name.split('fd')[0])
        id_nd = int(entry_nd_name.split('nd')[0])
        if id_fd != id_nd:
          print("WARNING: mismatching indices: {} and {}".format(id_fd, id_nd))
          raise Exception

        arr_nd = sparse.load_npz(entry_nd_path).todense()
        arr_fd = np.load(entry_fd_path)

        if REMOVE_MASK:
            arr_nd = arr_nd[:-1] 

        arr_fd = remove_padding(arr_fd)

        # for (4,10) upresolution
        # arr_nd = arr_nd[:, 560:1440, 17500:22500]
        # arr_fd = arr_fd[:, 140:360, 1750:2250]

        # for (8,8) upresolution
        arr_avg_weights = np.zeros((arr_fd.shape[1]))
        for ch, ch_vec in enumerate(arr_fd[0]):
            arr_avg_weights[ch] = ((np.abs(ch_vec) > 20) * np.abs(ch_vec)).sum()
        ch_cm = int(np.average(np.arange(0, arr_fd.shape[1]), weights=arr_avg_weights))

        if ch_cm + 60 >= arr_fd.shape[1]:
            ch_high = arr_fd.shape[1] - 1
            ch_low = ch_high - 120
        elif ch_cm - 60 < arr_fd.shape[1]:
            ch_low = 0
            ch_high = ch_low + 120
        else:
            ch_low = ch_cm - 60
            ch_high = ch_cm + 60

        arr_fd = arr_fd[:, ch_low:ch_high, 1750:2250]
        if not REMOVE_MASK:
            arr_fd = np.concatenate((arr_fd, arr_nd[-1:, ch_low:ch_high, 1750:2250]), 0)
            arr_nd = arr_nd[:-1]
        arr_nd = arr_nd[:, ch_low*8:ch_high*8, 14000:18000]

        # from matplotlib import pyplot as plt
        # fig, ax = plt.subplots(1, 2)
        # ax[0].imshow(arr_fd[0].T, aspect='auto', interpolation='none')
        # ax[1].imshow(arr_fd[1].T, aspect='auto', interpolation='none', cmap='Greys')
        # plt.show()

        if arr_nd[0].sum() < 60:
            num_skipped += 1
            continue

        S = sparse.COO.from_numpy(arr_nd)
        sparse.save_npz(os.path.join(ND_OUTPUT_DIR, entry_nd_name), S)

        np.save(os.path.join(FD_OUTPUT_DIR, entry_fd_name), arr_fd)

    print("Skipped {} events".format(num_skipped))

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("nd_input_dir")
    parser.add_argument("nd_output_dir")
    parser.add_argument("fd_input_dir")
    parser.add_argument("fd_output_dir")

    parser.add_argument("--remove_mask", action='store_true')

    args = parser.parse_args()

    return (args.nd_input_dir, args.nd_output_dir, args.fd_input_dir, args.fd_output_dir, args.remove_mask)

if __name__ == "__main__":
    arguments = parse_arguments()
    main(*arguments)

