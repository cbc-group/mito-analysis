from collections.abc import Mapping
import os
import yaml

__all__ = ["find_dataset_dir", "model_dir", "root"]


def root():
    return os.path.dirname(os.path.dirname(__file__))


def model_dir():
    return os.path.join(root(), "model")


def default_data_dir():
    return os.path.join(root(), "data")


class DataDir(Mapping):
    def __init__(self, config=None):
        self.data_dirs = [default_data_dir()]

        if isinstance(config, str):
            config = yaml.safe_load(config)
        else:
            if config is None:
                config = os.path.join(default_data_dir(), "config.yml")
            try:
                with open(config, "r") as fd:
                    config = yaml.safe_load(fd)
            except FileNotFoundError:
                config = dict()

        try:
            self.data_dirs += config["data_dir"]
        except KeyError:
            # ignore
            pass

    def __getitem__(self, key):
        for data_dir in self.data_dirs:
            path = os.path.join(data_dir, key)
            if os.path.exists(path):
                return path
        else:
            raise RuntimeError(f'unable to find dataset "{key}"')


data_dirs = DataDir()


def find_dataset_dir(dataset):
    return data_dirs[dataset]
