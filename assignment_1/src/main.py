from pathlib import Path

from utils import BrainData
from preprocess import preprocess_data
from searchlight import build_searchlight_indices


def main(data_dpath, tmp_fpath, radius):
    if not tmp_fpath.exists():
        print(f'Preprocessing data from {data_dpath}')
        bd = BrainData.from_directory(data_dpath, mask=False)
        data = preprocess_data(bd)
        bd.data = data
        print(f'Writing data to {tmp_fpath}')
        bd.write(tmp_fpath)

    print(f'Loading preprocessed data from {tmp_fpath}')
    bd = BrainData.from_npz_file(tmp_fpath)
    bd.sort_by_labels()

    print('Starting searchlight analysis')
    points = build_searchlight_indices(radius=radius)
    print(f'Searchlight has radius {radius} and {points.shape[0]} points')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dpath', type=Path, default='subj1')
    parser.add_argument('--tmp_fpath', type=Path, default='tmp.npz')
    parser.add_argument('--radius', type=int, default=2)
    args = parser.parse_args()

    kwargs = vars(args)
    main(**kwargs)
