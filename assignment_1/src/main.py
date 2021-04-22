import numpy as np
from scipy.signal import detrend
from scipy.stats import zscore


def preprocess_data(bd):
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
    return processed_data


if __name__ == '__main__':
    from utils import BrainData
    from matplotlib import pyplot as plt

    bd = BrainData('subj1')
    data = preprocess_data(bd)
    fig, axs = plt.subplots(1, 2)
    axs[0].plot(bd.data[20, 30, 30])
    axs[1].plot(data[20, 30, 30])
    plt.show()

    data = preprocess_data(bd)
