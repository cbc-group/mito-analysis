import logging

import cupy as cp
import imageio
import numpy as np
from skimage import filters, morphology
from scipy.ndimage.morphology import binary_fill_holes

from utoolbox.filters import median as median_filter

__all__ = ["extract_boundary", "feature_adaptive_filter"]

logger = logging.getLogger(__name__)


def extract_boundary(raw, deconv, diameter=3):
    """
    Extract cellular bondary using fluorescence background in the cytoplasm.

    Args:
        raw (ndarray): original data
        deconv (ndarray): deconvolved data
        diameter (int): median filter kernel diameter
    """

    # median filter
    # selem = morphology.cube(3)
    for i in range(10):
        logger.debug(f"iter {i}")
        # raw = filters.median(raw, selem)
        raw = median_filter(raw)
    raw = cp.asnumpy(raw)

    # determine threshold
    means = []
    for layer in raw:
        means.append(layer.mean())
    means = np.array(means)

    mean, median = means.mean(), np.median(means)
    logger.info(f"mean: {mean:.1f}, median: {median:.1f}")

    # threshold
    mask = filters.apply_hysteresis_threshold(raw, mean, median)
    mask = binary_fill_holes(mask)
    mask, n_features = morphology.label(mask, background=0, return_num=True)
    logger.info(f"found {n_features} object(s)")

    # keep relevant objects
    #   0: background (ignored), [1, N) features
    volumes = [(index, (mask == index).sum()) for index in range(1, n_features + 1)]
    volumes.sort(key=lambda x: x[1], reverse=True)
    logger.debug(volumes)

    # 1st: background
    vol_lim = volumes[0][1] // 2
    logger.info(f"vol_lim: {vol_lim}")

    mask2 = np.zeros_like(mask)
    # keep objects above threshold
    for index, volume in volumes:
        if volume > vol_lim:
            mask2[mask == index] = 1

    return mask2.astype(np.bool)


def feature_adaptive_filter(image, mask, pct=0.9, method="sqrt"):
    """
    TBA

    Args:
        image (ndarray): original data
        mask (ndarray): rough data mask
        pct (float, optional): cutoff percentage
        methods (str, optional): binning method
    """
    # select target pixels
    pixels = image[mask]

    hist, edge = np.histogram(pixels, bins=method)

    # normalize density function
    pdf = hist / hist.sum()
    cdf = pdf.cumsum()

    n_bins = len(hist)
    print(f"n_bins: {n_bins}")

    # determine cutoff lookup position
    index = np.interp(pct, cdf, np.arange(0, n_bins))
    print(f"cut index: {index}")
    # reverse lookup actual threshold
    int_lut = (edge[:-1] + edge[1:]) / 2
    threshold = np.interp(index, np.arange(0, n_bins), int_lut)
    print(f"threshold: {threshold}")

    image[~mask] = 0
    image = image > threshold

    return image
