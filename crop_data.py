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

def main(ND_INPUT_DIR, ND_OUTPUT_DIR, FD_INPUT_DIR, FD_OUTPUT_DIR, TICKSCALEDOWN, REMOVE_MASK):
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

        if TICKSCALEDOWN:
            arr_fd = remove_padding(arr_fd)

            arr_nd = arr_nd[:, 560:1440, 17500:22500]
            arr_fd = arr_fd[:, 140:360, 1750:2250]

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

    parser.add_argument("--tickscaledown", action='store_true')
    parser.add_argument("--remove_mask", action='store_true')

    args = parser.parse_args()

    return (args.nd_input_dir, args.nd_output_dir, args.fd_input_dir, args.fd_output_dir, args.tickscaledown, args.remove_mask)

if __name__ == "__main__":
    arguments = parse_arguments()
    main(*arguments)

