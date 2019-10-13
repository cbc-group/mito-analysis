import logging
import os
from pprint import pprint

import coloredlogs
from utoolbox.data import SPIMDataset

from utils import find_dataset_dir

logging.getLogger("pandas").setLevel(logging.ERROR)
logging.getLogger("tifffile").setLevel(logging.ERROR)

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

dataset_name = "analysis/graph/segments"
path = find_dataset_dir(dataset_name)
pprint(path)
