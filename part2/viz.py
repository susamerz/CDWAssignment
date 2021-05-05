"""
Visualization functions for RDM matrices.

Author: Marijn van Vliet <marijn.vanvliet@aalto.fi>
"""
from matplotlib import pyplot as plt
from scipy.spatial import distance
import numpy as np


def plot_rdm(rdm, labels, title='RDM', output_file=None):
    """Plot an RDM matrix.

    Parameters
    ----------
    rdm : ndarray, shape (n, n) or (n * (n - 1) - n,)
        The RDM matrix, either in square form or in the optimized form as
        returned by pdist.
    labels : list of str
        For each image, a string label indicating what kind of photo was being
        shown.
    title : str
        Title for the plot. Defaults to 'RDM'
    output_file : path-like | None
        When specified, the image will be saved to the specified output file.
    """
    classes = set(labels)
    n_classes = len(classes)
    n_items_per_class = 108  # Hardcoded for now because life isn't perfect

    # Is the RDM in square form?
    if rdm.ndim == 1:
        rdm = distance.squareform(rdm)
    elif (rdm.ndim != 2) or (rdm.shape[0] != rdm.shape[1]):
        raise ValueError('RDM needs to be either in square form or '
                         'optimized form.')

    # Compute nice tick positions for the string labels
    tick_pos = n_items_per_class * np.arange(n_classes) + n_items_per_class / 2
    plt.figure()
    plt.imshow(rdm, cmap='magma')
    plt.xticks(tick_pos, classes, rotation=90)
    plt.yticks(tick_pos, classes)
    plt.colorbar()
    plt.title(title)
    plt.tight_layout()

    if output_file is not None:
        plt.savefig(output_file)
