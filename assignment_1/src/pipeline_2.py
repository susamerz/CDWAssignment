import re
import numpy as np
import pandas as pd

from scipy.signal import detrend
from scipy.stats import zscore
from scipy.spatial.distance import cdist, pdist, squareform
from scipy.stats.stats import spearmanr

import nibabel as nib
from nilearn import plotting
from tqdm import tqdm

import warnings
import argparse
from os.path import join

warnings.filterwarnings("ignore")


class Subject:
    """Class for Subject that stores data and performs RSA analysis.

    Parameters
    ----------
    subject_name : any
        Name identifying the subject
    data_folder : Path or str
        Folder path where data for the Subject is
    """

    def __init__(self, subject_name, data_folder):
        self.subject_name = str(subject_name)
        self.data_folder = data_folder
        self.data_loaded = False

    def load_data(self):
        """Using self.data_folder, create all props that will contain data needed for RSA.
        """
        self.bold = nib.load(join(self.data_folder, "bold.nii.gz"))
        self.bold_data = self.bold.get_fdata()
        self.bold_affine = self.bold.affine
        del self.bold

        self.mask_data = nib.load(
            join(self.data_folder, "mask4_vt.nii.gz")).get_fdata()
        labels = pd.read_csv(join(self.data_folder, "labels.txt"), sep=' ')
        self.labels = labels[~labels.labels.isin(["rest", "scrambledpix"])].sort_values([
            'chunks', 'labels'])
        self.model_rdm = self._get_model_rdm()
        self.data_loaded = True

    def perform_analysis(self, radius=2):
        """Computes and stores RSA values using searchlight.

         Parameters
        ----------
        radius : int, default=2
            Radius for searchlight grid calculation.

        """

        if not self.data_loaded:
            self.load_data()
        self.bold_preprocessed = self._get_preprocessed_data()
        self.voxel_rsa = np.zeros_like(self.mask_data.flatten())
        self.mask_indices = self.mask_data.flatten().nonzero()[0]

        spatial_indices = list(np.ndindex(*self.bold_data.shape[:3]))

        searchlight_grid = cdist(np.array(self.mask_data.nonzero()).T,
                                 spatial_indices) <= radius  # (n_roi_voxels, n_total_voxels)
        print(f"Computing RSA for subject {self.subject_name}...")
        for i in tqdm(list(range(searchlight_grid.shape[0]))):
            # (n_roi_voxels, n_images)
            images = self.bold_preprocessed[searchlight_grid[i].nonzero(
            )][:, self.labels.index]
            # (n_images, n_images)
            corr = squareform(pdist(images.T, metric='correlation'))
            self.voxel_rsa[self.mask_indices[i]] = spearmanr(
                corr.flatten(), self.model_rdm.flatten())[0]

        print(
            f"Finished. {self.voxel_rsa.shape}, Mean, std: {self.voxel_rsa.mean(), self.voxel_rsa.std()}")

    def _get_preprocessed_data(self):
        """Apply detrending and z-scoring operations.

        Returns
        -------
        res_matrix: (40*64*64, n_images) np.ndarray
            Detrended and z-scored bold images

        """
        res_matrix = self.bold_data.copy()
        group_indices = self.labels.groupby('chunks').indices
        print(f"Preprocessing subject {self.subject_name}...")
        for _, indices in tqdm(group_indices.items()):
            res_matrix[:, :, :, indices] = zscore(detrend(self.bold_data[:, :, :, indices]),
                                                  axis=-1)
        return res_matrix.reshape(-1, res_matrix.shape[-1])

    def _get_model_rdm(self):
        sim = []
        for i in range(len(self.labels)):
            for j in range(i+1, len(self.labels)):
                sim.append(
                    int(self.labels.iloc[i].labels != self.labels.iloc[j].labels))
        return squareform(sim)


def plot_result(means, affine, output_file="assignment2.jpg"):
    means_pl = means.reshape(40, 64, 64)
    result = nib.Nifti1Image(means_pl, affine)
    plotting.plot_glass_brain(result, output_file=output_file)
    print(f"Success; plot saved into {output_file}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', type=str)
    args = parser.parse_args()

    subjects_folder = args.folder

    num_subjects = 6

    subjects = []

    for i in range(1, num_subjects+1):
        # Calculating RSA for each Subject
        s = Subject(i, join(subjects_folder, f"subj{i}"))
        s.perform_analysis()
        subjects.append(s)

    rsa_values = np.zeros((len(subjects), len(subjects[0].voxel_rsa)))

    for i, subj in enumerate(subjects):  # creating a matrix (n_subjects, 40*64*64)
        rsa_values[i, :] = subjects[i].voxel_rsa

    # computing mean signal across subjects
    rsa_means = rsa_values.mean(axis=0)

    # Plot
    plot_result(rsa_means, s.bold_affine)
