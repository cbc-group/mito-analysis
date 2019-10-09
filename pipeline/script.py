import logging
import os
from pprint import pprint

import coloredlogs
from utoolbox.data import SPIMDataset

from denoise import train, predict
from utils import data_dir

logging.getLogger("pandas").setLevel(logging.ERROR)
logging.getLogger("tifffile").setLevel(logging.ERROR)

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

dataset_name = "c6_raw"

path = os.path.join(data_dir(), dataset_name)
dataset = SPIMDataset(path)

if False:
    train(dataset["0"], name=dataset_name)
else:
    predict(dataset_name, dataset["0"])
