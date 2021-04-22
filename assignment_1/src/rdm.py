import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.stats import spearmanr


def build_rdm(bd):
    data = bd.data
    data_gt = data.reshape(-1, data.shape[-1])
    corr = pdist(data_gt.T, metric='correlation')
    corr_tt = squareform(corr)
    return corr_tt


def build_model_rdm(bd):
    label_t = bd.labels
    data_gt = label_t[np.newaxis]
    corr = pdist(data_gt.T, metric=lambda u, v: u != v)
    corr_tt = squareform(corr)
    return corr_tt


def calculate_rsa_score(rdm1, rdm2):
    corr, _ = spearmanr(rdm1.flatten(), rdm2.flatten())
    return corr


if __name__ == '__main__':
    from utils import BrainData

    bd = BrainData.from_npz_file('preprocessed.npz')
    bd.sort_by_labels()
    rdm = build_rdm(bd)
    model_rdm = build_model_rdm(bd)

    print(f'rdm vs rdm: {calculate_rsa_score(rdm, rdm)}')
    print(f'rdm vs model: {calculate_rsa_score(rdm, model_rdm)}')

    from matplotlib import pyplot as plt

    for matrix in [rdm, model_rdm]:
        fig, ax = plt.subplots()
        plt.imshow(matrix)
        plt.colorbar()
        ulabels, uindices = np.unique(bd.labels, return_index=True)
        plt.xticks(uindices, ulabels, rotation='vertical')
        plt.yticks(uindices, ulabels)
        plt.tight_layout()
    plt.show()
