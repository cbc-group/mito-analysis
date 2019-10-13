import logging

import numpy as np
import pandas as pd

__all__ = ["SpatialGraph"]

logger = logging.getLogger(__name__)


class SpatialGraph(object):
    """
    Args:
        nodes (str): nodes in a frame
        segments (str): edges between nodes
        points (str): raster voxels that describe an edge
    """

    def __init__(self, nodes, segments, points):
        nodes = self.parse_nodes_file(nodes)
        segments = self.parse_segments_file(segments)
        points = self.parse_points_file(points)

    @classmethod
    def parse_nodes_file(cls, path):
        """
        Parse Amira generated nodes file.

        1st row is the identifier, 2nd row is the actual header.

        Args:
            path (str): path to the CSV file
        """
        df = pd.read_csv(
            path,
            sep=",",
            quotechar='"',
            dtype={
                "Node ID": int,
                "X Coord": np.float32,
                "Y Coord": np.float32,
                "Z Coord": np.float32,
                "Coordination Number": int,
            },
            header=1,
            index_col="Node ID",
        )
        logger.info(f".. {len(df)} nodes loaded")
        return df

    @classmethod
    def parse_segments_file(cls, path):
        df = pd.read_csv(
            path,
            sep=",",
            quotechar='"',
            dtype={"Segment ID": int, "Node ID #1": int, "Node ID #2": int},
            converters={"Point IDs": lambda x: [int(_x) for _x in x.split(",")]},
            header=1,
            index_col="Segment ID",
        )
        logger.info(f".. {len(df)} segments loaded")
        return df

    @classmethod
    def parse_points_file(cls, path):
        df = pd.read_csv(
            path,
            sep=",",
            quotechar='"',
            dtype={
                "Point ID": int,
                "X Coord": np.float32,
                "Y Coord": np.float32,
                "Z Coord": np.float32,
            },
            header=1,
            index_col="Point ID",
        )
        logger.info(f".. {len(df)} points loaded")
        return df
