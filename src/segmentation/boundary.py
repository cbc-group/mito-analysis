import logging

import imageio
import matplotlib.pyplot as plt
import numpy as np
from skimage import filters, transform
from skimage.morphology import cube
from scipy.ndimage.morphology import binary_fill_holes
from scipy.ndimage.measurements import label

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
    selem = cube(3)
    for i in range(10):
        print(f"iter {i}")
        raw = filters.median(raw, selem)

    # determine threshold
    means = []
    for layer in raw:
        means.append(layer.mean())
    means = np.array(means)

    mean, median = means.mean(), np.median(means)
    print(f"mean: {mean:.1f}, median: {median:.1f}")

    # threshold
    mask = filters.apply_hysteresis_threshold(raw, mean, median)
    mask = binary_fill_holes(mask)
    mask, n_features = label(mask)

    # keep relevant objects
    volumes = [(index, (mask == index).sum()) for index in range(n_features)]
    volumes.sort(key=lambda x: x[1])
    print(volumes)

    # 1st: background
    threshold = volumes[-2][1] // 2
    print(f"threshold: {threshold}")

    mask2 = np.zeros_like(mask)
    # keep objects above threshold
    for index, volume in volumes[:-1]:
        if volume > threshold:
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
