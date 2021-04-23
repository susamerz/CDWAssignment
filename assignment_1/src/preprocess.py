import numpy as np
from scipy.signal import detrend
from scipy.stats import zscore


def preprocess_data(bd, zero_nan=False):
    data = bd.data
    processed_data = np.empty_like(data)
    chunks = bd.chunks
    assert data.shape[-1] == len(chunks)
    for chunk in set(chunks):
        chunk_flt = chunks == chunk
        data_chunk = data[..., chunk_flt]
        data_chunk = detrend(data_chunk, axis=-1)
        data_chunk = zscore(data_chunk, axis=-1)
        processed_data[..., chunk_flt] = data_chunk
    if zero_nan:
        processed_data[np.isnan(processed_data)] = 0.0
    return processed_data


if __name__ == '__main__':
    from utils import BrainData

    bd = BrainData.from_directory('subj1')
    data = preprocess_data(bd)
    bd.data = data
    bd.write('preprocessed.npz')
