from builtins import range

import numpy as np
import random

from batchgenerators.augmentations.noise_augmentations import augment_rician_noise, augment_gaussian_noise


def rician_noise_generator(generator, noise_variance=(0, 0.1)):
    '''
    Adds rician noise with the given variance.

    '''
    for data_dict in generator:
        assert "data" in list(
            data_dict.keys()), "your data generator needs to return a python dictionary with at least a 'data' key value pair"

        data_dict["data"] = augment_rician_noise(data_dict['data'], noise_variance=noise_variance)
        yield data_dict


def gaussian_noise_generator(generator, noise_variance=(0, 0.1)):
    '''
    Adds gaussian noise with the given variance.

    '''
    for data_dict in generator:
        assert "data" in list(
            data_dict.keys()), "your data generator needs to return a python dictionary with at least a 'data' key value pair"

        data_dict["data"] = augment_gaussian_noise(data_dict['data'], noise_variance=noise_variance)
        yield data_dict


def rician_noise_generator_dipy(generator, snr_range=(1, 10)):
    '''
    Adds rician noise to produce a image with the specified SNR.

    Uses a dipy function which is fast.
    '''
    from dipy.sims.voxel import add_noise

    for data_dict in generator:
        assert "data" in list(
            data_dict.keys()), "your data generator needs to return a python dictionary with at least a 'data' key value pair"

        data = data_dict['data']
        for sample_idx in range(data.shape[0]):
            sample = data[sample_idx]
            sample = np.nan_to_num(sample)  # needed otherwise add_noise() not working if NaNs in image
            shape = sample.shape

            brain = sample[sample > 1e-8]  # roughly select only brain, no background
            brain = brain if len(brain) > 0 else [0]  # add 0 element if list is empty (slices without brain)

            snr = random.uniform(snr_range[0], snr_range[1])
            sample = add_noise(sample.flatten(), snr, np.mean(brain), noise_type='rician')
            data[sample_idx] = np.reshape(sample, (shape[0], shape[1], shape[2]))
        data_dict["data"] = data
        yield data_dict