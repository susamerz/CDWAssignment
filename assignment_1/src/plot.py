from pathlib import Path
import matplotlib.pyplot as plt
from utils import BrainData


def main(data_fpath):
    bd = BrainData.from_npz_file(data_fpath)
    bd.plot_brain()
    plt.show()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('data_fpath', type=Path)
    args = parser.parse_args()

    kwargs = vars(args)
    main(**kwargs)
