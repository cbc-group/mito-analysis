import logging
import os

import click
import coloredlogs
import imageio
import numpy as np
from skimage import transform
from utoolbox.data import SPIMDataset

from segmentation import extract_boundary, feature_adaptive_filter
from utils import find_dataset_dir

logging.getLogger("tifffile").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)


def run(im_ori, im_dec):
    # match data size
    im_dec = transform.resize(im_dec, im_ori.shape)
    mask = extract_boundary(im_ori, im_dec)

    # upsample
    shape = tuple(s * 2 for s in im_ori.shape)
    mask = transform.resize(mask, shape).astype(np.bool)
    im_dec = transform.resize(im_dec, shape)

    # final segmentation
    result = feature_adaptive_filter(im_dec, mask)

    return mask, result


@click.command()
@click.argument("name")
@click.argument("dst_dir", type=click.Path(file_okay=False, writable=True))
@click.option(
    "-s",
    "--suffix",
    "deconv_suffix",
    type=str,
    default="_deconv",
    help="suffix of the deconvolved dataset folder",
)
@click.option("-c", "--channel", "ch_name", help="channel to apply segmentation")
def main(name, dst_dir, deconv_suffix="_deconv", ch_name=None):
    """
    Automagically perform mitochondria segmentation on SPIM acquired dataset.
    """
    # source dataset
    ori = find_dataset_dir(name)
    logger.info(f'loading original data from "{ori}"')
    ori_ds = SPIMDataset(ori)

    # deconvolved dataset
    dec = find_dataset_dir(f"{name}{deconv_suffix}")
    logger.info(f'loading deconvolved data from "{dec}"')
    dec_ds = SPIMDataset(dec)

    for sub_dir in ('mask', 'mito_seg'):
        try:
            os.makedirs(os.path.join(dst_dir, sub_dir))
        except FileExistsError:
            pass

    if ch_name is None:
        ch_name = list(ori_ds.keys())[0]
        logger.warning(f'channel not specified, using "{ch_name}"')

    ori_ds, dec_ds = ori_ds[ch_name], dec_ds[ch_name]

    for i, (name, im_ori, im_dec) in enumerate(
        zip(ori_ds.keys(), ori_ds.values(), dec_ds.values())
    ):
        logger.info(f".. {name}")
        mask, seg = run(im_ori, im_dec)

        path = os.path.join(os.path.join(dst_dir, "mask"), f"mask_{i:04d}.tif")
        imageio.volwrite(path, mask.astype(np.uint8) * 255)

        path = os.path.join(os.path.join(dst_dir, "mito_seg"), f"seg_{i:04d}.tif")
        imageio.volwrite(path, seg.astype(np.uint8) * 255)


if __name__ == "__main__":
    main()
