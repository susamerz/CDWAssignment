from re import search
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm

from scipy.signal import detrend
from scipy.stats import zscore
from scipy.spatial.distance import cdist, pdist, squareform

import nibabel as nib
from nilearn import plotting
from scipy.stats.stats import spearmanr


def preprocessing(bold_matrix, labels):
    """Applies detrending and z-scoring to bold_matrix, according to chunks in labels
    """
    res_matrix = bold_matrix.copy()
    group_indices = labels.groupby('chunks').indices
    for chunk_n, indices in group_indices.items():
        res_matrix[:, :, :, indices] = zscore(detrend(bold_matrix[:, :, :, indices]),
                                              axis=-1)
    return res_matrix


def get_model_rdm(labels):
    """Produces model RDM.
    """
    cleaned_labels = labels
    sim = []
    for i in range(len(cleaned_labels)):
        for j in range(i+1, len(cleaned_labels)):
            sim.append(
                int(cleaned_labels.iloc[i].labels != cleaned_labels.iloc[j].labels))
    return squareform(sim)


bold_path = "subj1/bold.nii.gz"
mask_path = "subj1/mask4_vt.nii.gz"

labels = pd.read_csv('../subj1/labels.txt', sep=' ')
labels = labels[~labels.labels.isin(["rest", "scrambledpix"])].sort_values([
    'chunks', 'labels'])

bold = nib.load(bold_path)
bold_data = bold.get_fdata()
bold_preprocessed = preprocessing(
    bold_data, labels).reshape(-1, bold_data.shape[-1])  # (n_voxels, n_ponts)

RADIUS = 2

mask_data = nib.load(mask_path).get_fdata()

model_rdm = get_model_rdm(labels)
voxel_rse = np.zeros((mask_data == 1).sum())

spatial_indices = list(np.ndindex(*bold_data.shape[:3]))

searchlight_grid = cdist(np.array(mask_data.nonzero()).T,
                         spatial_indices) <= RADIUS  # (n_roi_voxels, n_points)


for i in tqdm(list(range(searchlight_grid.shape[0]))):
    # (n_roi_voxels, n_points)
    images = bold_preprocessed[searchlight_grid[i].nonzero()][:, labels.index]
    corr = squareform(pdist(images.T, metric='correlation'))
    voxel_rse[i] = spearmanr(corr.flatten(), model_rdm.flatten())[0]

print(
    f"Finished. {voxel_rse.shape}, Mean, std: {voxel_rse.mean(), voxel_rse.std()}")
