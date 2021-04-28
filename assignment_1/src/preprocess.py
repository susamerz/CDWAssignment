import numpy as np
from scipy.signal import detrend
from scipy.stats import zscore

from utils import BrainData


def preprocess_data(bd, zero_nan=False):
    """Preprocess brain data.

    Parameters
    ----------
    bd:
        BrainData object
    zero_nan:
        If true, replace NaNs in output with zeros

    Returns
    -------
    processed_bd:
       Corresponding BrainData object with processed data
    """
    processed_data = np.empty_like(bd.data)
    unique_chunks = set(bd.chunks)
    for uc in unique_chunks:
        chunk_flt = bd.chunks == uc
        data_chunk = bd.data[..., chunk_flt]
        data_chunk = detrend(data_chunk, axis=-1)
        data_chunk = zscore(data_chunk, axis=-1)
        processed_data[..., chunk_flt] = data_chunk
    if zero_nan:
        processed_data[np.isnan(processed_data)] = 0.0
    return BrainData(data=processed_data,
                     chunks=bd.chunks.copy(),
                     labels=bd.labels.copy(),
                     mask=bd.mask.copy(),
                     affine=bd.affine.copy(),
                     )


if __name__ == '__main__':
    bd = BrainData.from_directory('data/subj1')
    bd = preprocess_data(bd)
    bd.write('preprocessed.npz')
