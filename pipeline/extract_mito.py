import logging

import coloredlogs
import imageio
import numpy as np
from skimage import transform
from utoolbox.data import SPIMDataset

from segmentation import extract_boundary, feature_adaptive_filter
from utils import find_dataset_dir

logging.getLogger("tifffile").setLevel(logging.ERROR)

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)


if __name__ == "__main__":
    # load dataset
    dataset_name = "predict"
    path = find_dataset_dir(dataset_name)
    print(path)
    dataset = SPIMDataset(path)

    dataset_name_decon = "predict_deconv"
    path_decon = find_dataset_dir(dataset_name_decon)
    print(path_decon)
    dataset_decon = SPIMDataset(path_decon)

    # create target directory
    try:
        import os

        os.mkdir("F:/_debug")
    except FileExistsError:
        pass

    def run(i, name, image, image_decon):
        print(f".. {name}")

        # match data size
        image_decon2 = transform.resize(image_decon, image.shape)
        mask = extract_boundary(image, image_decon2)

        # upsample
        shape = tuple(s * 2 for s in image.shape)
        mask = transform.resize(mask, shape).astype(np.bool)
        image_decon = transform.resize(image_decon, shape)

        # final segmentation
        result = feature_adaptive_filter(image_decon, mask)

        path = os.path.join("F:/_debug", f"boundary_{i:04d}.tif")
        imageio.volwrite(path, mask.astype(np.uint8) * 255)

        path = os.path.join("F:/_debug", f"seg_{i:04d}.tif")
        imageio.volwrite(path, result.astype(np.uint8) * 255)

    for i, args in enumerate(
        zip(dataset["0"].keys(), dataset["0"].values(), dataset_decon["0"].values())
    ):
        run(i, *args)
