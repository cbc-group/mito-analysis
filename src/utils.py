import os


def root():
    return os.path.dirname(os.path.dirname(__file__))


def data_dir():
    return os.path.join(root(), "data")


def model_dir():
    return os.path.join(root(), "model")

