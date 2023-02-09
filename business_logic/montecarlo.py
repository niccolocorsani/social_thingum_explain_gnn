import os
import random
from math import sqrt, log
import torch

import utility
from utility import write_to_graph_format, removeFilesFromFolder
from model_ml import predict_with_GNN

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def remove_random_column(tensor, index_to_not_remove):
  num_columns = tensor.shape[1]
  random_index = random.randint(0, num_columns - 1)
  while random_index == index_to_not_remove:
    random_index = random.randint(0, num_columns - 1)
  return torch.cat((tensor[:, :random_index], tensor[:, random_index + 1:]), dim=1), random_index


def back_propagate(dictionary, win, visited):
  for key in dictionary:
    if type(dictionary[key]) == dict:
      back_propagate(dictionary[key], win, visited)
    else:
      if key == "win":
        dictionary[key] += win
      if key == "visited":
        dictionary[key] += visited

  return dictionary


class MonteCarlo:
  def __init__(self, heterodata, edge_index, deepnes, model, prediction_to_evaluate_index):

    self.prediction_to_evaluate_index = prediction_to_evaluate_index
    self.model = model
    self.data = heterodata
    self.edge_index = edge_index
    self.deepnes = deepnes
    self.tree = {}  ## uso dizionario che è più veloce della lista
    self.list_of_final_graph_with_30_edges = []

  def select_child(self, node):
    """Select a child node using the Upper Confidence Bound for Trees (UCT) formula."""
    return max(node.children, key=lambda child: child.wins / child.visits +
                                                sqrt(2 * log(node.visits) / child.visits))

  def search(self):
    removeFilesFromFolder(ROOT_DIR + "/edge_index_of_final_graph_30_edges/")

    for level in range(0, self.deepnes):
      self.edge_index, _ = remove_random_column(self.edge_index, self.prediction_to_evaluate_index)
      #print("\033[1;35m" + str(self.edge_index.shape) + "\033[0m")
      ## ROOT
      for i in range(self.edge_index.shape[1] - 1, -1, -1):
        root_node_id = str(level) + '_' + str(i)
        if (self.edge_index.shape[1] <= 30): break
        self.simulation_montecarlo(data=self.data, node_id=root_node_id,
                                   edge_index=self.edge_index)

    win_dic = min(self.list_of_final_graph_with_30_edges,
                  key=lambda x: x['win'])  ## il vincitore dei sottografi di dimensione 30
    utility.write_to_graph_format(win_dic['edge_index'] , ROOT_DIR + '/edge_index_of_final_graph_30_edges/' + str(i) + '.txt')


    return win_dic

  def simulation_montecarlo(self, data, node_id, edge_index):

    tree = {}
    tree[node_id] = {'win': 0, 'visited': 0}

    while (edge_index.shape[1] > 30):
      edge_index, index = remove_random_column(edge_index, self.prediction_to_evaluate_index)
      child_id = node_id + '_' + str(index)
      node_id = child_id
      tree[node_id] = {'win': 0, 'visited': 0}

      data_rotto_usabile_solo_una_volta = data.subgraph({
        'user': torch.tensor(edge_index[0]),
        'movie': torch.tensor(edge_index[1]),
      })
      data_rotto_usabile_solo_una_volta['user', 'rates', 'movie'].edge_label_index = data_rotto_usabile_solo_una_volta[
        'user', 'rates', 'movie'].edge_index

    predictions = predict_with_GNN(data_rotto_usabile_solo_una_volta, self.model)
    win = abs(predictions[self.prediction_to_evaluate_index] - \
              data_rotto_usabile_solo_una_volta['user', 'rates', 'movie'].edge_label[
                self.prediction_to_evaluate_index])
    self.list_of_final_graph_with_30_edges.append({'edge_index': edge_index, 'win': win})

    tree = back_propagate(tree, win, 1)
    self.tree.update(tree)

    # if win < 0.1:
    #   utility.write_to_graph_format(edge_index, ROOT_DIR + '/edge_index_of_final_graph_30_edges/' + str(
    #     node_id) + '.txt')
    return

  def expand_node(self, node, state):
    """Expand the node by adding a random child node."""
    new_state = state.get_random_successor()
    new_node = MonteCarlo.Node(new_state)
    node.children.append(new_node)
    return new_node


class Node:
  def __init__(self, id, visits, wins, child_node):
    self.id = id
    self.child_node = child_node
    self.visits = visits
    self.wins = wins


if __name__ == '__main__':
  pass
