import glob
import logging
import os
from pprint import pprint

import coloredlogs
from utoolbox.data import SPIMDataset

from events import SpatialGraph
from utils import find_dataset_dir

logging.getLogger("pandas").setLevel(logging.ERROR)
logging.getLogger("tifffile").setLevel(logging.ERROR)

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

dataset = {
    "nodes": "analysis/graph/nodes",
    "segments": "analysis/graph/segments",
    "points": "analysis/graph/points",
}

# lookup absolute path
for key, path in dataset.items():
    path = find_dataset_dir(path)
    paths = glob.glob(os.path.join(path, "*.csv"))
    dataset[key] = paths

# NOTE: dict keeps its key order in 3.7
for paths in zip(*list(dataset.values())):
    sg = SpatialGraph(*paths)
    sg.preview()
    break
