import torch
from torch_geometric.nn import GATConv, Linear, to_hetero
import torch.nn as nn
import torch_geometric.transforms as T

from utility import read_data
class GAT1(torch.nn.Module):
  def __init__(self, hidden_channels, out_channels):
    super().__init__()
    self.conv1 = GATConv((-1, -1), hidden_channels, add_self_loops=False)
    self.lin1 = Linear(-1, hidden_channels)
    self.conv2 = GATConv((-1, -1), out_channels, add_self_loops=False)
    self.lin2 = Linear(-1, out_channels)

  def forward(self, x, edge_index):
    x = self.conv1(x, edge_index) + self.lin1(x)  ## x è embedding user e item
    x = x.relu()
    x, alpha = self.conv2(x, edge_index, return_attention_weights=True)
    # x = self.conv2(x, edge_index)
    return x, alpha  # x è il nuovo embedding
class EdgeDecoderGAT(torch.nn.Module):
  def __init__(self, hidden_channels):
    super().__init__()
    self.lin1 = Linear(2 * hidden_channels, hidden_channels)
    self.relu = nn.ReLU()
    self.lin2 = Linear(hidden_channels, 1)
    self.sigmoid = nn.Sigmoid()

  def forward(self, z_dict, edge_label_index, alpha):
    row, col = edge_label_index  ## è il collegamento tra nodi
    # concat user and movie embeddings
    z = torch.cat([z_dict['user'][row], z_dict['item'][col]], dim=-1)
    # concatenated embeddings passed to linear layer
    z = self.lin1(z)
    z = self.relu(z)
    z = self.lin2(z)
    z = self.sigmoid(z)  ## z è il rating predetto, tra 0 e 1 perchè sigmoide
    return z.view(-1), alpha  ## z.view(-1) serve per avere una rappresentazione in scalare anziche vettore
class ModelGAT1(torch.nn.Module):
  def __init__(self, hidden_channels, data):
    super().__init__()
    self.data = data
    self.encoder = GAT1(hidden_channels, hidden_channels)
    self.encoder = to_hetero(self.encoder, data.metadata(), aggr='sum')
    self.decoder = EdgeDecoderGAT(hidden_channels)

  def forward(self, x_dict, edge_index_dict, edge_label_index):
    # z_dict contains dictionary of movie and user embeddings returned from GraphSage
    z_dict, alpha = self.encoder(x_dict, edge_index_dict)
    return self.decoder(z_dict, edge_label_index, alpha)
def allAlberto(data):
  device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

  # Perform a link-level split into training, validation, and test edges.
  # train_data, val_data, test_data = T.RandomLinkSplit(
  #   num_val=0.1,
  #   num_test=0.1,
  #   neg_sampling_ratio=0,
  #   edge_types=[('user', 'rates', 'item')],
  #   rev_edge_types=[('item', 'rev_rates', 'user')],
  # )(data)
  # weight = torch.bincount((train_data['user', 'item'].edge_label * 5).int())
  # weight = weight.max() / weight
  # # ricardo: per normalizzare i pesi
  # weight = weight / 5

  def weighted_mse_loss(pred, target, weight=None):
    weight = 1. if weight is None else weight[target].to(pred.dtype)
    return (weight * (pred - target.to(pred.dtype)).pow(2)).mean()

  #train_data['item', 'user'].edge_index.dtype

  # model and train/val/test data is on cuda:0
  model = ModelGAT1(hidden_channels=32, data=data).to(device)
  loss_fn = nn.MSELoss()
  optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

  def loss_custom(pred, target):
    loss = 0

    for i in range(0, len(pred)):
      loss += loss_fn(pred[i], target[i])
    return loss / len(pred)

  def train():
    model.train()
    optimizer.zero_grad()
    pred, alpha = model(data.x_dict, data.edge_index_dict,  ## Questo alpha è quello dell'attenzione
                        data['user', 'item'].edge_label_index)


    target = data['user', 'item'].edge_label

    loss = loss_custom(pred, target)
    loss.backward()
    optimizer.step()

    return float(loss)

  @torch.no_grad()
  def test(data):
    predictions = []
    model.eval()
    pred, alpha = model(data.x_dict, data.edge_index_dict,
                        data['user', 'item'].edge_label_index)
    predictions = pred[:]
    target = data['user', 'item'].edge_label  # .float()
    mse = loss_custom(pred, target)
    return float(mse), predictions

  # Due to lazy initialization, we need to run one model step so the number
  # of parameters can be inferred:
  # with torch.no_grad():
  #   model.encoder(train_data.x_dict, train_data.edge_index_dict)
  loss_train = []
  loss_val = []
  epochs_n = 50
  # early stopping
  patience = 1000
  trigger = 0
  for epoch in range(epochs_n):
    if trigger < patience:
      loss = train()
      # train_rmse, pred_train = test(train_data)
      # val_rmse, pred_val = test(val_data)
      # test_rmse, pred_test = test(test_data)
      # loss_train.append(train_rmse)
      # loss_val.append(val_rmse)
      # if loss_val[epoch] > loss_val[epoch - 1]:
      #   trigger += 1

  return None, None, model
def predict_with_GNN(data, model):
  loss_fn = nn.MSELoss()

  def loss_custom(pred, target):
    loss = 0
    for i in range(0, len(pred)):
      loss += loss_fn(pred[i], target[i])
    return loss / len(pred)

  @torch.no_grad()
  def test_attention(data, model):
    model.eval()
    pred, alpha = model(data.x_dict, data.edge_index_dict,
                        data['user', 'item'].edge_label_index)
    target = data['user', 'item'].edge_label  # .float()
    mse = loss_custom(pred, target)
    predList = []
    predL = list(pred)
    for i in predL:
      predList.append(float(i))
    return float(mse), target.float().tolist(), predList, alpha

  mse, target, pred, alpha = test_attention(data, model)
  return pred


if __name__ == '__main__':
  data, edge_index = read_data()
  allAlberto(data)
