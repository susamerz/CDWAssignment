"""
Functions for computing searchlight patches. A searchlight are all the voxels
within a given radius to a given center voxel.

Author: Marijn van Vliet <marijn.vanvliet@aalto.fi>
"""
import numpy as np
from scipy.spatial import distance

# Nice progress bar
from tqdm import tqdm


def searchlight(bold, radius, roi_mask=None):
    """Generate searchlight patches of the given radius.

    Parameters
    ----------
    bold : Nifti1Image
        The BOLD images to create searchlight patches for.
    radius : int
        The radius of the searchlight, in voxels. This radius excludes the
        "seed" voxel in the center of the searchlight.
    roi_mask : ndarray of shape (n_i, n_j, n_k) | None
        Mask containing non-zero values at all voxels within some region of
        interest. When given, the centers of the searchlight patches are
        restricted to lie inside this ROI. Note that the searchlight patch
        itself can extend beyond the ROI.

    Yields
    ------
    patch_data : ndarray of shape (n_points, n_times)
        The data within a single searchlight patch.
    center : tuple (i, j, k)
        The index of the center of the searchlight patch in the original data.
    """
    # Create (i, j, k) indices corresponding to all the voxels in the MRI image
    all_voxels = np.array(list(np.ndindex(bold.shape[:3])))

    # Select all voxels that are part of the ROI
    roi_voxels = roi_mask.get_fdata().nonzero()
    roi_voxels = np.array(roi_voxels).T

    # Create searchlight patches
    pbar = tqdm(desc='Searchlight', total=len(roi_voxels), unit='patches')
    for center_voxel in roi_voxels:
        # `cdist` wants both inputs to be lists, so we need to wrap
        # center_voxel in a list and unwrap the result.
        dist_to_center = distance.cdist([center_voxel], all_voxels)[0]
        patch = all_voxels[dist_to_center <= radius]

        # NumPy fancy indexing requires tuples
        patch_data = bold.get_fdata()[tuple(patch.T)]
        center_voxel = tuple(center_voxel)

        yield patch_data, center_voxel
        pbar.update(1)
    pbar.close()
