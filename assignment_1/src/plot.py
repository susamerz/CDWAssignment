from pathlib import Path
import matplotlib.pyplot as plt
from utils import BrainData


def main(data_fpath, plot_fpath):
    bd = BrainData.from_npz_file(data_fpath)
    bd.plot_brain()
    plt.savefig(plot_fpath)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('data_fpath', type=Path)
    parser.add_argument('plot_fpath', type=Path)
    args = parser.parse_args()

    kwargs = vars(args)
    main(**kwargs)
