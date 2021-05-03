
import numpy as np
import scipy
from scipy.spatial.distance import pdist, squareform
from scipy.stats import spearmanr
from progress.bar import Bar


def preprocess_chunk(chunk_data):
    """This function preprocesses a chunk of data by first removing linear trend and the
    z-scoring the data. Operations are performed on the last axis in data.

    Parameters
    ----------
    chunk_data : array-like
        NOTE: operations will be performed on the last axis.

    Returns
    -------
    array-like
        A preprocessed version of chunk data in same shape and format"""

    detrended = scipy.signal.detrend(chunk_data)
    z_scored = scipy.stats.zscore(detrended, axis=-1)

    return z_scored

def preprocess_bold_data(bold_data, chunk_id):
    """Wrapper for handling preprocessing for a whole dataset comprised of chunks.

    Parameters
    ----------
    bold_data : array-like
        (NumPy) array containing neural image data

    chunk_id : list or array
        Must have same length than there are rows in bold_data. Contains chunk identifier for each
        row in bold_data

    Returns
    -------
    array-like
        A chunk-wise preprocessed version of bold_data in same shape and format
    """


    processed_bold_np = np.zeros(bold_data.shape)
    chunks = np.unique(chunk_id)

    chunk_bar = Bar('Preprocessing chunks', max=len(chunks))
    for chunk in chunks:
        chunk_indices = np.where(chunk_id==chunk)[0]
        bold_chunk = bold_data[:, :, :, chunk_indices]
        preprocessed_chunk = preprocess_chunk(bold_chunk)
        processed_bold_np[:, :, :, chunk_indices] = preprocessed_chunk
        chunk_bar.next()

    chunk_bar.finish()
    return processed_bold_np


def searchlight(center_voxel, radius, search_grid):
    """This is a searchlight function that returns an array for each center voxel corresponding to
    all search_grid locations that are within radius (euclidean distance) from the center voxel

    Parameters
    ----------
    center_voxels : list
        a list or array of voxel locations around which seearch is performed
    radius: float
        search radius: locations within this radius from each center voxel are included in return
    search_grid: list
        all possible locations in 3D coordinates, in list format

    Returns
    -------
    dict
        dictionary of lists, where each key is a center voxel and items are lists of locations inside
        the search radius from that center voxel in 2D array format: line is a voxel, columns are coordinates.

    """

    distances = scipy.spatial.distance.cdist(search_grid, np.array([center_voxel]))
    found_locations = np.array(search_grid)[distances.flatten() < radius]

    return found_locations

def searchlight_generator(center_voxels, radius, search_grid):
    """ Creates a generator that yields searchlight locations around center_voxel

    Parameters
    ----------
    center_voxels : list
        center voxels around which searchlight is shone

    radius : int
        radius of the searchlight: locations that are closer than this radius from
        each individual center voxel are included in the reeturned locations

    search_grid : list or array
        A list or array of all possible locations as tuple coordinates"""


    return (searchlight(center_voxel, radius, search_grid) for center_voxel in center_voxels)

def remove_rows(data, labels, labels_to_remove):
    """Removes 'rest' labeled data.

    Parameters
    ----------
    data : array-like
        data to be cleaned

    labels : Pandas dataframe
        labels corresponding to last axis in data

    Returns
    -------
    array-like
        data that has been cleaned of data corresponding to 'rest' labels

    Pandas dataframe
        labels that correspond to returned data

    """
    for label in labels_to_remove:
        n_orig_images = len(data[0, 0, 0, :])
        data = data[:, :, :, labels.query('labels != @label').index]
        labels = labels[labels.labels != label]
        labels.reset_index(drop=True, inplace=True)  # makes index match row numbering in pic_voxels
        n_removed_images = n_orig_images - len(data[0, 0, 0, :])
        print(f"removed {n_removed_images} images with label {label}")
    return data, labels

def create_model_RDM(labels):
    """Creates a binary valued matrix from labels where value is 0 if row label equals column label
    and 1 otherwise.

    Parameters
    ----------
    labels : list or 1-D array of labels

    Returns
    -------
    ndarray
        binary valued 2-D matrix from labels where value is 0 if row label equals column label
        and 1 otherwise.
    """

    model_RDM = squareform([int(labels[i]!=labels[j]) for i in range(len(labels)) for j in range(i+1, len(labels))])

    return model_RDM

def create_bold_RDM(data, search_locs):
    """ Creates an RDM matrix from given data for each location listed in search_locs

    Parameters
    ----------
    data : numpy array
        Contains BOLD data in array format

    search_locs : list
        Contains the locations to be used in analysis as tuples (3D)"""

    search_locs_data = np.array([data[loc[0], loc[1], loc[2], :].flatten() for loc in search_locs]).T
    RDM = squareform(pdist(search_locs_data, metric='correlation'))  # Pearson distance <=> pairwise correlation

    return RDM