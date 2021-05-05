"""
Create grand-average RSA result

Author: Marijn van Vliet <marijn.vanvliet@aalto.fi>
"""
# Basic scientific libs
import numpy as np
import matplotlib.pyplot as plt

# Neuroscience packages for loading and visualizing data
import nibabel as nib
from nilearn import plotting

# Sibling modules
import config


# Read in the data for each subject
rsa_data = [nib.load(config.output_data_path / f'subj{subject}' / 'rsa_result.nii.gz')
            for subject in config.subjects]

# Average across subjects
grand_average = np.mean([rsa_subject.get_fdata() for rsa_subject in rsa_data], axis=0)
grand_average = nib.Nifti1Image(grand_average, rsa_data[0].affine, rsa_data[0].header)

# Save data
config.output_data_path.mkdir(parents=True, exist_ok=True)
nib.save(grand_average, config.output_data_path / 'rsa_grand_average.nii.gz')

# Make plot
config.figure_path.mkdir(parents=True, exist_ok=True)
plotting.plot_glass_brain(grand_average)
plt.savefig(config.figure_path / 'rsa_grand_average.pdf')
