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
    rdm : ndarray, shape (n_images, n_images)
        The RDM matrix.
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
    plt.figure()
    plt.imshow(distance.squareform(rdm), cmap='magma')
    plt.xticks(n_items_per_class * np.arange(n_classes) + n_items_per_class / 2, classes, rotation=90)
    plt.yticks(n_items_per_class * np.arange(n_classes) + n_items_per_class / 2, classes)
    plt.colorbar()
    plt.title(title)
    plt.tight_layout()

    if output_file is not None:
        plt.savefig(output_file)
