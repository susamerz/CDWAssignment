import numpy as np
from scipy.spatial.distance import pdist, squareform


def build_rdm(bd):
    data = bd.data
    labels = bd.labels

    # Ensure correct shape
    data_gt = data.reshape(-1, data.shape[-1])

    # Sort according to labels
    assert data_gt.shape[-1] == len(labels)
    s_t = np.argsort(labels)
    label_t = labels[s_t]
    data_gt = data_gt[:, s_t]

    # Calculate
    corr = pdist(data_gt.T, metric='correlation')
    corr_tt = squareform(corr)
    return label_t, corr_tt


def build_model_rdm(bd):
    labels = bd.labels

    # Sort according to labels
    s_t = np.argsort(labels)
    label_t = labels[s_t]

    data_gt = label_t[np.newaxis]
    corr = pdist(data_gt.T, metric=lambda u, v: u != v)
    corr_tt = squareform(corr)
    return label_t, corr_tt


if __name__ == '__main__':
    from utils import BrainData

    bd = BrainData.from_npz_file('preprocessed.npz')
    labels, rdm = build_rdm(bd)
    labels, model_rdm = build_model_rdm(bd)

    from matplotlib import pyplot as plt

    for matrix in [rdm, model_rdm]:
        fig, ax = plt.subplots()
        plt.imshow(matrix)
        plt.colorbar()
        ulabels, uindices = np.unique(labels, return_index=True)
        plt.xticks(uindices, ulabels, rotation='vertical')
        plt.yticks(uindices, ulabels)
        plt.tight_layout()
    plt.show()
