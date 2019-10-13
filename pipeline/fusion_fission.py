import glob
import logging
import os
from pprint import pprint

import coloredlogs
from utoolbox.data import SPIMDataset

from events import SpatialGraph
from utils import find_dataset_dir

logging.getLogger("pandas").setLevel(logging.ERROR)
logging.getLogger("tifffile").setLevel(logging.ERROR)

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

dataset = {
    "nodes": "analysis/graph/nodes",
    "segments": "analysis/graph/segments",
    "points": "analysis/graph/points",
}

# lookup absolute path
for key, path in dataset.items():
    path = find_dataset_dir(path)
    paths = glob.glob(os.path.join(path, "*.csv"))
    dataset[key] = sorted(paths)

# rebuild spatial graph
# NOTE: dict keeps its key order in 3.7
graphs = []
for i, paths in enumerate(zip(*list(dataset.values()))):
    print(i)
    g = SpatialGraph(*paths)
    graphs.append(g)

    # DEBUG
    break

# overlay plot
import vispy

path = find_dataset_dir("raw")
raw = SPIMDataset(path)

from utoolbox.apps.viewer.main import viewer

for datastore in raw.values():
    for data in datastore.values():
        print(data)

        data = (data - data.min()) / (0.5 * (data.max() - data.min())) * 255
        viewer(data)

        raise RuntimeError()

# find isolates
import networkx as nx

for graph in graphs:
    isolates = list(nx.isolates(graph.graph))
    if len(isolates) > 0:
        print(f"found {len(isolates)} isolates, halt!")
        graphs[-1].preview()
        break
else:
    print("not isolate found")
