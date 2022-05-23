import os, argparse

import numpy as np
from tqdm import tqdm
import sparse

def main(ND_INPUT_DIR, ND_OUTPUT_DIR, FD_INPUT_DIR, FD_OUTPUT_DIR, TICKSCALEDOWN, REMOVE_MASK):
    num_skipped = 0

    for entry_nd, entry_fd in tqdm(zip(os.scandir(ND_INPUT_DIR), os.scandir(FD_INPUT_DIR))):
        arr_nd = sparse.load_npz(entry_nd.path).todense()
        arr_fd = np.load(entry_fd.path)

        if REMOVE_MASK:
            arr_nd = arr_nd[:-1] 

        if TICKSCALEDOWN:
            arr_nd = arr_nd[:, 560:1440, 17500:22500]
            arr_fd = arr_fd[:, 140:340, 1750:2250]

            if arr_nd[0].sum() < 60:
                num_skipped += 1
                continue

            S = sparse.COO.from_numpy(arr_nd)
            sparse.save_npz(os.path.join(ND_OUTPUT_DIR, entry_nd.name), S)

            np.save(os.path.join(FD_OUTPUT_DIR, entry_fd.name), arr_fd)

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

