import os, argparse

import numpy as np
from tqdm import tqdm
import sparse

def main(INPUT_DIR, ND_CH0_ADC, ND_CH3_STACKED, ND_CH4_FIRSTTRIGGER):

  max_adcs, max_num_stacked, max_num_firsttriggers = [], [], []
  min_adcs, min_num_stacked, min_num_firsttriggers = [], [], []

  for entry in tqdm(os.scandir(INPUT_DIR)):
    arr = sparse.load_npz(entry.path).todense()

    if ND_CH0_ADC:
      max_adcs.append(np.max(arr[0]))
      min_adcs.append(np.min(arr[0]))

    if ND_CH3_STACKED:
      max_adcs.append(np.max(arr[3]))
      min_adcs.append(np.min(arr[3]))

    if ND_CH4_FIRSTTRIGGER:
      max_adcs.append(np.max(arr[4]))
      min_adcs.append(np.min(arr[4]))

  if ND_CH0_ADC:
    print("min adc = {}, max adc = {}".format(min(min_adcs), max(max_adcs)))

  if ND_CH3_STACKED:
    print("min num stacked = {}, max num stacked = {}".format(min(min_num_stacket), max(max_num_stacked)))

  if ND_CH4_FIRSTTRIGGER:
    print("min num first triggers = {}, max num first triggers = {}".format(min(min_num_stacket), max(max_num_firsttriggers)))

def parse_arguments():

  parser = argparse.ArgumentParser()

  parser.add_argument("input_dir")

  parser.add_argument("--nd_ch0_adc", action='store_true')
  parser.add_argument("--nd_ch3_stacked", action='store_true')
  parser.add_argument("--nd_ch4_firsttrigger", action='store_true')

  args = parser.parse_args()

  return (args.input_dir, args.nd_ch0_adc, args.nd_ch3_stacked, args.nd_ch4_firsttrigger)

if __name__ == "__main__":
  arguments = parse_arguments()
  main(*arguments)

