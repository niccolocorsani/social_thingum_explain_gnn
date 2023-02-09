# Import Library

import numpy as np
import pandas as pd
import os
import torch_geometric.transforms as T
from torch_geometric.datasets import Planetoid
import matplotlib.pyplot as plt
import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, GNNExplainer
import torch_geometric
from torch_geometric.loader import NeighborLoader
from torch_geometric.utils import to_networkx



if __name__ == '__main__':

  # Load the Planetoid dataset
  dataset = Planetoid(root='.', name="Pubmed")
  data = dataset[0]

  # Set the device dynamically
  device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

  # Create batches with neighbor sampling
  train_loader = NeighborLoader(
    data,
    num_neighbors=[5, 10],
    batch_size=16,
    input_nodes=data.train_mask,
  )


  # Define the GCN model
  class Net(torch.nn.Module):
    def __init__(self):
      super().__init__()

      self.conv1 = GCNConv(dataset.num_features, 16, normalize=False)
      self.conv2 = GCNConv(16, dataset.num_classes, normalize=False)
      self.optimizer = torch.optim.Adam(self.parameters(), lr=0.02, weight_decay=5e-4)

    def forward(self, x, edge_index):
      x = F.relu(self.conv1(x, edge_index))
      x = F.dropout(x, training=self.training)
      x = self.conv2(x, edge_index)
      return F.log_softmax(x, dim=1)


  model = Net().to(device)


  def accuracy(pred_y, y):
    """Calculate accuracy."""
    return ((pred_y == y).sum() / len(y)).item()


  # define the function to Train the model
  def train_nn(model, x, edge_index, epochs):
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = model.optimizer

    model.train()
    for epoch in range(epochs + 1):
      total_loss = 0
      acc = 0
      val_loss = 0
      val_acc = 0

      # Train on batches
      for batch in train_loader:
        optimizer.zero_grad()

        out = model(batch.x, batch.edge_index)
        loss = criterion(out[batch.train_mask], batch.y[batch.train_mask])

        total_loss += loss
        acc += accuracy(out[batch.train_mask].argmax(dim=1),
                        batch.y[batch.train_mask])
        loss.backward()
        optimizer.step()

        # Validation
        val_loss += criterion(out[batch.val_mask], batch.y[batch.val_mask])
        val_acc += accuracy(out[batch.val_mask].argmax(dim=1),
                            batch.y[batch.val_mask])

      # Print metrics every 10 epochs
      if (epoch % 10 == 0):
        print(f'Epoch {epoch:>3} | Train Loss: {total_loss / len(train_loader):.3f} '
              f'| Train Acc: {acc / len(train_loader) * 100:>6.2f}% | Val Loss: '
              f'{val_loss / len(train_loader):.2f} | Val Acc: '
              f'{val_acc / len(train_loader) * 100:.2f}%')


  # define the function to Test the model
  def test(model, data):
    """Evaluate the model on test set and print the accuracy score."""
    model.eval()
    out = model(data.x, data.edge_index)
    acc = accuracy(out.argmax(dim=1)[data.test_mask], data.y[data.test_mask])
    return acc


  # Train the Model
  train_nn(model, data.x, data.edge_index, 200)

  # Test
  print(f'\nGCN test accuracy: {test(model, data) * 100:.2f}%\n')

  # Explain the GCN for node
  node_idx = 20
  x, edge_index = data.x, data.edge_index
  # Pass the model to explain to GNNExplainer
  explainer = GNNExplainer(model, epochs=100, return_type='log_prob')
  # returns a node feature mask and an edge mask that play a crucial role to explain the prediction made by the GNN for node 20
  node_feat_mask, edge_mask = explainer.explain_node(node_idx, x, edge_index)
  ax, G = explainer.visualize_subgraph(node_idx, edge_index, edge_mask, y=data.y)
  plt.show()
  print("Ground Truth label for node: ", node_idx, " is ", data.y.numpy()[node_idx])
  out = torch.softmax(model(data.x, data.edge_index), dim=1).argmax(dim=1)
  print("Prediction for node ", node_idx, "is ", out[node_idx].cpu().detach().numpy().squeeze())
