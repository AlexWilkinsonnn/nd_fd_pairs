import os, argparse, csv

import numpy as np
from matplotlib import pyplot as plt

def main(INPUT_DIR, N):
  for i, entry in enumerate(os.scandir(INPUT_DIR)):
    if N and i >=N:
      break
    
    print(entry.name, end='\r')

    arr = np.zeros((1, 512, 4608))
    with open(entry.path, 'r') as f:
      f_reader = csv.reader(f)
      for line in f_reader:
        arr[0, int(line[0]) + 16, int(line[1]) + 58] = float(line[2])

    plt.imshow(arr[0].T, interpolation='none', aspect='auto', cmap='viridis')
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

