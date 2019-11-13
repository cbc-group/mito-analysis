import logging
import os

import click
import coloredlogs
import imageio
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
    "-o",
    "dst_name",
    type=str,
    default="n2v",
    help="filtered dataset folder name",
)
@click.option("-c", "--channel", "ch_name", help="channel to apply the filter")
@click.option('-i', '--inference', is_flag=True, help="inference only")
def main(name, dst_name, ch_name, inference):
    path = find_dataset_dir(name)
    logger.info(f'loading original data from "{path}"')
    ds = SPIMDataset(path)
    
    if ch_name is None:
        ch_name = list(ds.keys())[0]
        logger.warning(f'channel not specified, using "{ch_name}"')

    ds = ds[ch_name]

    if not inference:
        # train...
        logger.info('start training N2V model')
        train(ds, name=name)
    else:
        logger.debug('... inference-only')

    # create output directory
    try:
        parent, _ = os.path.split(path)
        dst_dir = os.path.join(parent, dst_name)
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