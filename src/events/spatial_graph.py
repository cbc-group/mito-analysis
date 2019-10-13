import logging

import networkx as nx
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
        graph = nx.Graph()

        nodes = self.parse_nodes_file(nodes)
        for nid, row in nodes.iterrows():
            coord = (row["Z Coord"], row["Y Coord"], row["X Coord"])
            graph.add_node(nid, coord=coord)

        segments = self.parse_segments_file(segments)
        points = self.parse_points_file(points)
        for _, row in segments.iterrows():
            point_coords = []
            for pid in row["Point IDs"]:
                point_coords.append(
                    (
                        points["Z Coord"][pid],
                        points["Y Coord"][pid],
                        points["X Coord"][pid],
                    )
                )
            graph.add_edge(row["Node ID #1"], row["Node ID #2"], points=point_coords)

        self.graph = nx.freeze(graph)

        self._rebuild_mito_relationship()

    def preview(self):
        from itertools import count
        import matplotlib.pyplot as plt

        g = self.graph
        mapping = dict(zip(sorted(self.mito.nodes), count()))
        colors = [mapping[g.nodes[n]["mid"]] for n in g.nodes]
        labels = {n: self.graph.nodes[n]["mid"] for n in g.nodes}

        pos = nx.spring_layout(g)
        nx.draw_networkx_edges(g, pos, alpha=0.2)
        nx.draw_networkx_nodes(
            g,
            pos,
            nodelist=g.nodes,
            node_color=colors,
            node_size=100,
            with_labels=False,
            cmap=plt.cm.jet,
        )
        nx.draw_networkx_labels(g, pos, labels, font_size=12)
        plt.axis("off")
        plt.show()

    ##

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

    ##

    def _rebuild_mito_relationship(self):
        # condensation requires directed graph
        mito = nx.condensation(nx.DiGraph(self.graph))

        attrs = dict()
        for mid, members in mito.nodes(data="members"):
            attrs.update({nid: {"mid": mid} for nid in members})
        nx.set_node_attributes(self.graph, attrs)

        logger.info(f"{len(mito)} (grouped) mitochondria")
        self.mito = nx.freeze(mito)
