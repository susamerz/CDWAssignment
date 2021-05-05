"""
Preprocess the BOLD data.

Detrends and z-scores the signal. Data will be processed chunk-by-chunk.
"Chunks" are recording sessions between which the subject took a short break.
"""
import warnings
import argparse

# Basic scientific libs
import numpy as np
import pandas as pd

# Some algorithms we will need
from scipy.signal import detrend
from scipy.stats import zscore

# Neuroscience package for loading data
import nibabel as nib

# Nice progress bar
from tqdm import tqdm

# Sibling modules
import config

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('subject', type=int, help='The subject to process')
args = parser.parse_args()

# Load fMRI data
bold = nib.load(config.input_data_path / f'subj{args.subject}' / 'bold.nii.gz')

# This is the metadata of the experiment. What stimulus was shown when etc.
meta = pd.read_csv(config.input_data_path / f'subj{args.subject}' / 'labels.txt', sep=' ')

# Process the data chunk-by-chunk
for chunk in tqdm(np.unique(meta.chunks), desc='Preprocessing', unit='chunks'):
    chunk_mask = meta.chunks == chunk
    chunk_data = bold.get_fdata()[..., chunk_mask]
    chunk_data = detrend(chunk_data, type='linear', axis=3, overwrite_data=True)

    # For z-scoring, we need to deal with voxels that remain zero at all
    # times.  We ignore the divide-by-zero warning and later backfill the
    # resulting NaN's with zeros.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        chunk_data = zscore(chunk_data, axis=3)
    chunk_data[np.isnan(chunk_data)] = 0

    bold.get_fdata()[..., chunk_mask] = chunk_data

# Drop classes and sort images by class.
# We must ensure that all times, the metadata and the bold images are in sync.
# Hence, we first perform the operations on the `meta` pandas DataFrame. Then,
# we can use the DataFrame's index to repeat the operations on the BOLD data.
meta = meta[~meta.labels.isin(['rest', 'scrambledpix'])]
meta = meta.sort_values('labels')
bold = nib.Nifti1Image(bold.get_fdata()[..., meta.index],
                       bold.affine, bold.header)

# Save the result
output_dir = config.output_data_path / f'subj{args.subject}'
output_dir.mkdir(parents=True, exist_ok=True)
nib.save(bold, output_dir / 'bold_preprocessed.nii.gz')
meta.to_csv(output_dir / 'labels_preprocessed.txt', sep=' ', index=False)
