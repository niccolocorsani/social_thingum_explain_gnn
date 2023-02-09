import math
from argparse import ArgumentParser, Namespace
from collections import Counter
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from typing_extensions import Literal

import ipywidgets as widgets
import matplotlib.pyplot as plt
import networkx as nx
import networkx.algorithms.isomorphism as iso
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from easydict import EasyDict as edict
from ipywidgets import interact
from ogb.graphproppred import PygGraphPropPredDataset
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
from torch import FloatTensor, LongTensor, Tensor
from torch_geometric.data import Batch, Data, InMemoryDataset
from torch_geometric.datasets import TUDataset
from torch_geometric.loader import DataLoader
from torch_geometric.nn import GCNConv, GINConv, global_max_pool
from torch_geometric.nn.conv import MessagePassing
from torch_geometric.nn.models import GIN
from torch_geometric.utils import k_hop_subgraph, remove_self_loops, to_networkx
from tqdm.notebook import trange, tqdm



@dataclass
class Args:
    """A class containing arguments used for setting up the dataset and model."""
    batch_size: int = 32  # Batch size for the training loop.
    num_workers: int = 2  # Number of workers to use for the data loader.
    learning_rate: float = 0.001  # Learning rate.
    weight_decay: float = 5e-4  # Weight decay.
    num_epochs: int = 300  # Number of training epochs.
    num_layers: int = 3  # Number of message passing layers in the GNN model.
    hidden_features: int = 32  # Dimensionality of the hidden layers in the GNN.
    dropout: float = 0.2  # Dropout probability.
    seed: int = 42  # Random seed.

args = Args()




if __name__ == '__main__':
  # Load MUTAG dataset (graph classification)
  mutag_dataset = edict()
  mutag_dataset.ds = TUDataset(
    './dataset/mutag/',
    name='MUTAG',
    use_node_attr=True,
    use_edge_attr=True
  )
  mutag_dataset.ds.shuffle()
  mutag_size = len(mutag_dataset.ds)
  mutag_dataset.train_ds = mutag_dataset.ds[:int(0.8 * mutag_size)]
  mutag_dataset.valid_ds = mutag_dataset.ds[int(0.8 * mutag_size): int(0.9 * mutag_size)]
  mutag_dataset.test_ds = mutag_dataset.ds[int(0.9 * mutag_size):]

  # Since MUTAG has multiple graphs, we use DataLoaders to load the graphs
  mutag_train_loader = DataLoader(
    dataset=mutag_dataset.train_ds,
    batch_size=args.batch_size,
    num_workers=args.num_workers,
    shuffle=True
  )
  mutag_valid_loader = DataLoader(
    dataset=mutag_dataset.valid_ds,
    batch_size=args.batch_size,
    num_workers=args.num_workers,
    shuffle=False
  )
  mutag_test_loader = DataLoader(
    dataset=mutag_dataset.test_ds,
    batch_size=args.batch_size,
    num_workers=args.num_workers,
    shuffle=False
  )
  device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
  print(device)

  for i, mutag_data in enumerate(mutag_dataset.ds[:5]):

    print(type(mutag_data))

    print(mutag_data)


