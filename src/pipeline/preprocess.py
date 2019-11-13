import logging
import os

import click
import coloredlogs
from utoolbox.data import SPIMDataset

from denoise import train, predict
from utils import find_dataset_dir

logging.getLogger("tifffile").setLevel(logging.ERROR)

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

logger = logging.getLogger(__name__)

@click.command()
@click.argument('name')
@click.option(
    "-s",
    "--suffix",
    "n2v_suffix",
    type=str,
    default="_n2v",
    help="suffix of the filtered dataset folder",
)
@click.option("-c", "--channel", "ch_name", help="channel to apply the filter")
def main(name, n2v_suffix, ch_name):
    path = find_dataset_dir(name)
    logger.info(f'loading original data from "{path}"')
    ds = SPIMDataset(path)
    
    if ch_name is None:
        ch_name = list(ds.keys())[0]
        logger.warning(f'channel not specified, using "{ch_name}"')

    ds = ds[ch_name]

    # train...
    logger.info('start training N2V model')
    train(ds, name=name)

    # create output directory
    try:
        parent, src_dir = os.path.split(path)
        dst_dir = os.path.join(parent, f'{src_dir}{n2v_suffix}')
        os.makedirs(dst_dir)
    except FileExistsError:
        pass

    # ... predict
    logger.info(f'start inference using N2V model ({name})')
    for name, result in zip(ds.keys(), predict(name, ds)):
        print(name)
        result_path = os.path.join(dst_dir, f'{name}.tif')
        imageio.volwrite(result_path, result)

if __name__ == '__main__':
    main()