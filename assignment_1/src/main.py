import numpy as np
from pathlib import Path

from utils import BrainData
from preprocess import preprocess_data
from searchlight import build_searchlight_indices
from rdm import build_rdm, build_model_rdm, calculate_rsa_score


def main(data_dpath, tmp_fpath, rsa_fpath, radius):
    if not tmp_fpath.exists():
        print(f'Preprocessing data from {data_dpath}')
        bd = BrainData.from_directory(data_dpath, apply_mask=False)
        data = preprocess_data(bd)
        bd.data = data
        print(f'Writing data to {tmp_fpath}')
        bd.write(tmp_fpath)

    print(f'Loading preprocessed data from {tmp_fpath}')
    bd = BrainData.from_npz_file(tmp_fpath)
    bd.sort_by_labels()
    model_rdm = build_model_rdm(bd.labels)

    print('Starting searchlight analysis')
    sl_points_iv = build_searchlight_indices(radius=radius)
    print(f'Searchlight has radius {radius} '
          f'and {sl_points_iv.shape[0]} points')

    data_gt = bd.data
    Ng_v = data_gt.shape[:-1]
    rsa_data_g = np.zeros(Ng_v)
    points_iv = np.argwhere(bd.mask == 1)
    Ni = points_iv.shape[0]
    for i, origin_v in enumerate(points_iv):
        # XXX This is a terribly slow loop. Vectorizing should help

        # Index list without out-of-bounds indices
        indices_iv = (origin_v + sl_points_iv)
        flt_i = np.logical_and(np.all(indices_iv >= 0, axis=1),
                               np.all(indices_iv < Ng_v, axis=1))
        indices_iv = indices_iv[flt_i]

        # Process data inside the searchlight
        sl_data_gt = data_gt[tuple(indices_iv.T)]
        rdm = build_rdm(sl_data_gt)
        rsa = calculate_rsa_score(rdm, model_rdm)
        rsa_data_g[origin_v] = rsa

        print(f'\r{(i + 1) / Ni * 100:.2f}% done', end='')

    print()
    print(f'Writing RSA data to {rsa_fpath}')
    rsa_bd = BrainData(data=rsa_data_g[..., np.newaxis], mask=bd.mask,
                       labels=np.array(['']), chunks=np.array([0]),
                       affine=bd.affine)
    rsa_bd.write(rsa_fpath)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dpath', type=Path, default='subj1')
    parser.add_argument('--tmp_fpath', type=Path, default='tmp.npz')
    parser.add_argument('--rsa_fpath', type=Path, default='rsa.npz')
    parser.add_argument('--radius', type=int, default=2)
    args = parser.parse_args()

    kwargs = vars(args)
    main(**kwargs)
