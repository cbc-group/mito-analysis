import logging
import os

from csbdeep.utils import plot_history
import imageio
import numpy as np

from utils import model_dir

from .n2v.n2v.internals.N2V_DataGenerator import N2V_DataGenerator
from .n2v.n2v.models import N2VConfig, N2V

__all__ = ["train"]

logger = logging.getLogger(__name__)


def train(datastore, patch_shape=(16, 32, 32), ratio=0.7, name="untitled"):
    # create data generator object
    datagen = N2V_DataGenerator()

    # use the first stack as shape hint
    image = next(iter(datastore.values()))
    # TODO sample in between timeseries
    # patch additional axes
    image = image[np.newaxis, ..., np.newaxis]

    patches = datagen.generate_patches_from_list([image], shape=patch_shape)
    print(patches.shape)
    n_patches = patches.shape[0]
    logger.info(f"{n_patches} patches generated")

    # split training set and validation set
    i = int(n_patches * ratio)
    X, X_val = patches[:i], patches[i:]

    # create training config
    config = N2VConfig(
        X,
        unet_kern_size=3,
        train_steps_per_epoch=100,
        train_epochs=100,
        train_loss="mse",
        batch_norm=True,
        train_batch_size=4,
        n2v_perc_pix=1.6,
        n2v_patch_shape=patch_shape,
        n2v_manipulator="uniform_withCP",
        n2v_neighborhood_radius=5,
    )

    model = N2V(config=config, name=name, basedir=model_dir())

    # train and save the model
    history = model.train(X, X_val)
    model.export_TF()

    plot_history(history, ["loss", "val_loss"])


def predict(name, datastore):
    model = N2V(config=None, name=name, basedir=model_dir())

    root = datastore.root + "_predict"
    for key, data in datastore.items():
        path = os.path.join(root, f"{key}.tif")
        data_pred = model.predict(data, axes="ZYX")
        imageio.volwrite(path, data_pred)  # TODO switch to auto datastore writer
