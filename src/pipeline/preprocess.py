import logging

import coloredlogs
from utoolbox.data import SPIMDataset

from denoise import train, predict
from utils import find_dataset_dir

logging.getLogger("pandas").setLevel(logging.ERROR)
logging.getLogger("tifffile").setLevel(logging.ERROR)

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

dataset_name = "c6_raw"
path = find_dataset_dir(dataset_name)
dataset = SPIMDataset(path)

if False:
    train(dataset["0"], name=dataset_name)
else:
    predict(dataset_name, dataset["0"])
