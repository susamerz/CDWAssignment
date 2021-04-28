import numpy as np
from pathlib import Path

from utils import BrainData


def main(input_files, output_file):
    # Read first file
    fpath = input_files[0]
    print(f'Reading data from {fpath}')
    bd = BrainData.from_npz_file(fpath)

    # Read remaining files and collect average to bd object
    for fpath in input_files[1:]:
        print(f'Reading data from {fpath}')
        bd2 = BrainData.from_npz_file(fpath)
        assert bd.data.shape == bd2.data.shape
        bd.data += bd2.data
        bd.mask = np.logical_or(bd.mask, bd2.mask)
    bd.data /= len(input_files)

    print(f'Writing average data to {output_file}')
    bd.write(output_file)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('input_files', type=Path, nargs='+')
    parser.add_argument('output_file', type=Path)
    args = parser.parse_args()

    kwargs = vars(args)
    main(**kwargs)
