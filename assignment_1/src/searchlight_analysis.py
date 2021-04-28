import numpy as np
from pathlib import Path

from utils import BrainData
from preprocess import preprocess_data
from searchlight import build_searchlight_indices
from rdm import build_rdm, build_model_rdm, calculate_rsa_score


def main(data_dpath, output_fpath, radius):
    print(f'Reading data from {data_dpath}')
    bd = BrainData.from_directory(data_dpath, apply_mask=False)

    print('Preprocessing')
    bd = preprocess_data(bd)

    print('Starting searchlight analysis')
    bd.sort_by_labels()
    model_rdm = build_model_rdm(bd.labels)
    sl_points = build_searchlight_indices(radius=radius)
    print(f'Searchlight has radius {radius} '
          f'and {sl_points.shape[0]} points')

    grid_shape = bd.data.shape[:-1]
    rsa_data = np.zeros(grid_shape)
    # Grid points inside the mask
    grid_points = np.argwhere(bd.mask)
    for i, origin_point in enumerate(grid_points):
        # XXX This is a terribly slow loop. Vectorizing should help

        # Build index list without out-of-bounds indices
        points = (origin_point + sl_points)
        flt = np.logical_and(np.all(points >= 0, axis=1),
                             np.all(points < grid_shape, axis=1))
        points = points[flt]

        # Process data inside the searchlight points
        sl_data = bd.data[tuple(points.T)]
        rdm = build_rdm(sl_data)
        rsa = calculate_rsa_score(rdm, model_rdm)
        rsa_data[tuple(origin_point)] = rsa

        print(f'\r{(i + 1) / grid_points.shape[0] * 100:.2f}% done', end='')

    print()
    print(f'Writing RSA data to {output_fpath}')
    # Fill labels and chunks with dummy data
    rsa_bd = BrainData(data=rsa_data[..., np.newaxis], mask=bd.mask,
                       labels=np.array(['']), chunks=np.array([0]),
                       affine=bd.affine)
    rsa_bd.write(output_fpath)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('data_dpath', type=Path)
    parser.add_argument('output_fpath', type=Path)
    parser.add_argument('--radius', type=int, default=2)
    args = parser.parse_args()

    kwargs = vars(args)
    main(**kwargs)
