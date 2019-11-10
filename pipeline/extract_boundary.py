import logging

import coloredlogs
import imageio
import numpy as np
from skimage import transform
from utoolbox.data  import SPIMDataset

from segmentation import extract_boundary, feature_adaptive_filter
from utils import find_dataset_dir, data_dirs

logging.getLogger("tifffile").setLevel(logging.ERROR)

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

dataset_name = 'predict'
path = find_dataset_dir(dataset_name)
print(path)
dataset = SPIMDataset(path)

dataset_name_decon = 'GPUdecon'
path_decon = find_dataset_dir(dataset_name_decon)
print(path_decon)
dataset_decon = SPIMDataset(path_decon)

try:
    import os
    os.mkdir('_boundary')
except FileExistsError:
    pass

# filter out keys
target_keys = []
for i, target_key in enumerate(zip(dataset['0'].keys(), dataset_decon['0'].keys())):
    if i not in (0, 1, 800, 1000):
        continue
    target_keys.append((i, ) + target_key)

for i, image, image_decon in target_keys:
    print(f'.. {image}')

    # load data
    image, image_decon = dataset['0'][image], dataset_decon['0'][image_decon]

    # match data size
    image_decon2 = transform.resize(image_decon, image.shape)
    mask = extract_boundary(image, image_decon2)
    
    # upsample
    shape = tuple(s*2  for s in image.shape)
    mask = transform.resize(mask, shape).astype(np.bool)
    
    path = os.path.join('_boundary', f'boundary_{i:04d}.tif')
    imageio.volwrite(path, mask.astype(np.uint8)*255)
