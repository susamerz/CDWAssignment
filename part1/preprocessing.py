import warnings

# Scientific libs
import numpy as np
from scipy.signal import detrend
from scipy.stats import zscore

# Nice progress bar
from tqdm import tqdm


def preprocess(bold, chunks=None, overwrite_data=False):
    """Preprocess some BOLD data.

    Detrends and z-scores the signal. Optionally, data can be processed
    chunk-by-chunk. "Chunks" are recording sessions between which the subject
    took a short break.

    Parameters
    ----------
    bold : Nifty1Image
        The BOLD images to preprocess
    chunks : ndarray, shape (n_images,) | None
        When specified, preprocessing will be performed for each chunk
        separately. This parameter should contain for each image in
        ``bold``, a value which indicates to which chunk the item
        belongs. Defaults to None.
    overwrite_data : bool
        Whether to overwrite the data to save memory (True), or copy the data
        (False). Defaults to False.

    ------
    bold_preproc : Nifty1Image
        The preprocessed BOLD images
    """
    if chunks is None:
        # Assign all BOLD images to the same chunk.
        chunks = np.ones(bold.shape[3])

    if not overwrite_data:
        bold = bold.copy()

    # Start up a progress bar
    pbar = tqdm(desc='Preprocessing', total=len(np.unique(chunks)),
                unit='chunks')

    # Process the data chunk-by-chunk
    for chunk in np.unique(chunks):
        chunk_mask = chunks == chunk
        chunk_data = bold.get_fdata()[..., chunk_mask]
        chunk_data = detrend(chunk_data, type='linear', axis=3,
                             overwrite_data=True)

        # For z-scoring, we need to deal with voxels that remain zero at all
        # times.  We ignore the divide-by-zero warning and later backfill the
        # resulting NaN's with zeros.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            chunk_data = zscore(chunk_data, axis=3)
        chunk_data[np.isnan(chunk_data)] = 0

        bold.get_fdata()[..., chunk_mask] = chunk_data
        pbar.update(1)

    pbar.close()
    return bold
