===============================================================
The assignment, part 1: Implementation of the analysis pipeline
===============================================================

In this first part, we will work with data from a single subject only.
The data can be downloaded from: http://data.pymvpa.org/datasets/haxby2001/subj1-2010.01.14.tar.gz

Recommended Python packages are:

 - `nibabel <https://nipy.org/nibabel/>`_ for loading the fMRI data.
 - `nilearn <https://nilearn.github.io/>`_ for plotting the fMRI data.
 - `pandas <https://pandas.pydata.org/>`_ for reading CSV/TSV files and all your tabular data manipulation needs.
 - `numpy <https://numpy.org/>`_ for all your array data manipulation needs.
 - `scipy <https://www.scipy.org/>`_ for many, many useful signal processing functions (e.g. detrending and z-scoring)
 - `matplotlib <https://matplotlib.org/>`_ for all your plotting needs not served by nilearn.

Loading MRI data
================

The BOLD signal (``bold.nii.gz``) can be loaded using `nibabel.load <https://nipy.org/nibabel/reference/nibabel.html#quickstart>`_::

    import nibabel as nib
    bold = nib.load('subj1/bold.nii.gz')
    
The resulting `Nifti1Image
<https://nipy.org/nibabel/reference/nibabel.nifti1.html#nibabel.nifti1.Nifti1Image>`_
class contains a 4D image, where the 4th dimension represents time.
To access the data as a NumPy array, use the ``get_fdata()`` method.
For example, to extract the timecourse of the voxel at coordinates (20, 30, 30), you would do::

   import nibabel as nib
   bold = nib.load('subj1/bold.nii.gz')
   data = bold.get_fdata()
   voxel_timecourse = data[20, 30, 30, :]

The anatomical MRI (``anat.nii.gz``) can be loaded in the same manner, but will be a 3D image::

   import nibabel as nib
   anat = nib.load('subj1/anat.nii.gz')
   # Take a slice at j=20
   anat_slice = anat.get_fdata()[:, :, 20]

Loading the labels
==================

The file ``labels.txt`` contains for each MRI image:

1. The object category of the stimulus that was presented, or "rest" meaning no stimulus was presented.
   There is also a "scrambled pix" category that we don't use for the analysis.
2. The "chunk" the image was recorded in. Chunks start at 0. Pre-processing of the data should be done for each chunk separately.

This data can be loaded with `Pandas <https://pandas.pydata.org>`_::

    import pandas as pd
    labels = pd.read_csv('subj1/labels.txt', sep=' ')
    # Print first 5 rows of the labels
    print(labels.head(5))

Loading the ROI mask
====================
We will restrict the analysis to an ROI defined by the authors of the dataset in ``subj1/mask4_vt.nii.gz``. This ROI is also defined in the form of a ``Nifti1Image``, with ones at voxels that are part of the ROI and zeros otherwise::

    import nibabel as nib
    bold = nib.load('subj1/bold.nii.gz')
    # Select all voxels in the ROI
    mask = nib.load('subj1/mask4_vt.nii.gz')
    voxels_in_roi = bold.get_fdata()[mask.get_fdata() == 1, :]


Plotting MRI data
=================

The `nilearn <https://nilearn.github.io/>`_ module contains some useful plotting functions.
These functions operate on ``Nifti1Image`` objects as created by ``nibabel``, for example::

   import nibabel as nib
   from nilearn import plotting

   # Plot anatomy
   anat = nib.load('subj1/anat.nii.gz')
   plotting.plot_anat(anat)

   # Plot data using a "glass brain"
   bold = nib.load('subj1/bold.nii.gz')
   some_data = bold.slicer[:, :, :, 0]  # First BOLD image
   plotting.plot_glass_brain(some_data)

This means that when you have data in the form of a NumPy array, you have to pack it inside a ``Nifti1Image`` object first.
To do this, you need the ``affine`` transform from the original ``Nifti1Image``::

   import numpy as np
   import nibabel as nib
   from nilearn import plotting

   # This is the original BOLD image that is used during the analysis
   bold = nib.load('subj1/bold.nii.gz')

   # Some exciting new data derived from the BOLD image
   some_new_data = np.random.rand(40, 64, 64)

   # Pack the new data inside a Nift1Image using the same affine transform as
   # the original BOLD image
   some_new_data = nib.Nifti1Image(some_new_data, bold.affine)

   # Now we can plot it
   plotting.plot_glass_brain(some_new_data)

Submitting your analysis code
=============================

Please submit your analysis code by making a pull request to this repository.
Code review will happen inside your pull request on GitHub.

Implementation Tips
===================
Here are some tips which may come in useful when implementing the analysis.

Preprocessing the data
----------------------
You will find ``scipy.signal.detrend`` and ``scipy.stats.zscore`` helpful when pre-processing the data.

Syncing labels and MRI images
-----------------------------
Note that the index of a ``DataFrame`` object is tied to the rows.
Initially the index will be: ``0, 1, 2, 3, 4, etc.``
But as you select rows from the table, for example if you drop rows 1 and 2, the index is selected likewise, so would become in this case: ``0, 3, 4, etc.``
Likewise, if you sort the table, the index is sorted alongside the rows.
This is super useful for carrying over operations on the table to operations on the MRI image array.

Selecting MRI images based on rows in the labels table::

    # Select all BOLD images in chunk 4
    labels_chunk4 = labels.query('chunks == 4')
    bold_chunk4 = bold.get_fdata()[:, :, :, labels_chunk4.index]

Sorting MRI images based on the labels table::

    # Sort images by object category
    labels_sorted = labels.sort_values('labels')
    bold_sorted = bold.get_fdata()[:, :, :, labels_sorted.index]

Make sure that your labels and images are always in the same order!

Making a spherical searchlight
------------------------------

An effective strategy for computing a spherical searchlight surrounding a voxel is the following:

1. Create a grid of points corresponding to each voxel using ``numpy.ndindex`` (see image below).
2. Pick the point corresponding to the center voxel of the searchlight 
3. Compute the distance between the center point and all other points using ``scipy.spatial.distance.cdist`` or (faster, but more complicated) ``scipy.spatial.cKDTree``.
4. Find the indices of the points with a distance smaller or equal to the searchlight radius
5. Use the indices from step 4 to select the voxels from the BOLD images

.. image:: images/searchlight_creation.png
    :alt: Grid of points corresponding to the voxels
