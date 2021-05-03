"""
Script for analysing which areas of the brain are activated when identifying different pictures.
NOTE: This script is an exercise version and should NOT be used in actual analysis.
"""

import nibabel as nib
import pandas as pd
from nilearn import plotting
from tools import *  # make sure namespace doesn't get messed up!
from matplotlib.pyplot import matshow, savefig
import argparse

parser = argparse.ArgumentParser(description='Run RSA analysis for BOLD data for selected subjects.')
parser.add_argument('subjects', type=int, nargs='+', help='Subject indentifiers (int) used to select subjects.')
args = parser.parse_args()

# Input params
searchlight_radius = 2

subject_list = args.subjects  # number identificators for test subjects to be used in analysis


def single_sub_pipeline(subj_no):
    """This highly context specific function executes analysis pipeline
    for a single subject at a time. It contains data filtering, preprocessing,
    RDM anc RSA calculations for a single subject."""

    # Load original data
    bold = nib.load(f'data/subj{subj_no}/bold.nii.gz') # loads dataset of BOLD images in Nifti1Image format
    mask = nib.load(f'data/subj{subj_no}/mask4_vt.nii.gz')
    labels = pd.read_csv(f'data/subj{subj_no}/labels.txt', sep=' ')

    data = bold.get_fdata()
    mask_data = mask.get_fdata()

    # Remove unwanted images from data
    wanted_data, wanted_labels = remove_rows(data, labels, ['rest', 'scrambledpix'])

    # Preprocessing
    print("Pre-processing...")
    chunk_id = wanted_labels.chunks.to_numpy()
    processed_bold_data = preprocess_bold_data(wanted_data, chunk_id)

    print("Sorting...")
    labels_sorted = wanted_labels.sort_values('labels')
    voxels_sorted = processed_bold_data[:, :, :, labels_sorted.index]

    # Create Model RDM
    # just in case different subjects have different label data.
    # If not, then this could be done just once.
    print("Creating model RDM")
    model_RDM = create_model_RDM(labels_sorted.labels.to_numpy())
    model_RDM_pic = matshow(model_RDM)
    savefig(f"model_RDM_subject{subj_no}.png")

    # create voxel index
    print("Creating voxel index...")
    data_shape = voxels_sorted.shape
    voxel_shape = data_shape[0:3]
    voxel_index_grid = list(np.ndindex(voxel_shape))


    # Create list of ROI voxel locations:
    ROI_locs = list(map(tuple, np.argwhere(mask_data == 1)))


    # create BOLD RDMs for all center voxels:
    ROI_RSAs  = {}
    ROI_RDM_progress_bar = Bar('Computing RDMs for ROIs', max=len(ROI_locs))

    # create a searchlight generator for returning search locations per single center voxel
    searchlight_gen = searchlight_generator(ROI_locs, searchlight_radius, voxel_index_grid)

    for loc in ROI_locs:
        searchlight_locs = next(searchlight_gen)
        ROI_RDM = create_bold_RDM(voxels_sorted, searchlight_locs)
        ROI_RSAs[loc], RSAp = spearmanr(ROI_RDM.flatten(), model_RDM.flatten())
        if np.isnan(ROI_RSAs[loc]):
            print(ROI_RDM)
            raise ValueError("RSA value was nan")
            break
        ROI_RDM_progress_bar.next()

    ROI_RDM_progress_bar.finish()


    # create an RSA image:
    print("Creating a Nifti1Image")
    plot_data = np.zeros(data.shape[0:3])
    for ROI_loc in ROI_RSAs:
        plot_data[ROI_loc] = ROI_RSAs[ROI_loc]

    print("Plotting RSA figures")
    img = nib.Nifti1Image(plot_data, bold.affine)
    plotting.plot_glass_brain(img, output_file=f"RSA_plot_glass_brain_subj{subj_no}.png")

    return plot_data

##########################
# Multi-subject pipeline #
##########################


# finds out the shape of data based on first subject in list
# assumes all subjects have same shape
first_bold = nib.load(f'data/subj{subject_list[0]}/bold.nii.gz')
bold_data_shape = first_bold.get_fdata().shape[0:3]

all_ROIs = []

RSAs = []

# Following averages over individual RSA plots by adding them one by one into avg_RSA and
# dividing by number of subjects in the end.

for subj_no in subject_list:
    print(f"analysing subject {subj_no}")
    subject_RSAs = single_sub_pipeline(subj_no)
    RSAs.append(subject_RSAs)

avg_RSA = np.mean(RSAs, axis=0)

print("Creating plot")
avg_img = nib.Nifti1Image(avg_RSA, first_bold.affine)
plotting.plot_glass_brain(avg_img, output_file=f"RSA_plot_all_subject_avg.png")

print("Finished.")

