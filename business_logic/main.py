import os
import time
import model_ml
import utility
from defensive_programming import DefensiveProgramming
from model_ml import allAlberto
from montecarlo import MonteCarlo
from utility import read_data, removeFilesFromFolder
import torch
from torch_geometric.transforms import RemoveIsolatedNodes

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
torch.set_printoptions(threshold=100000)


def run_every_things():
  ## Cose da preprocessing
  torch.device('cuda' if torch.cuda.is_available() else 'cpu')
  data, edge_index = read_data()

  ## Riduco dimensione grafo
  print(edge_index.shape)

  edge_index = edge_index[:, :30]
  data_con_sub_graph = data.subgraph({
    'user': torch.tensor([0, 1]),
    'movie': torch.tensor([0, 1, 2, 3, 4, 30]),
  })

  data_con_sub_graph['user', 'rates', 'movie'].edge_label_index = data_con_sub_graph[
    'user', 'rates', 'movie'].edge_index

  data_con_edge_sub_graph = data.edge_subgraph({
    'rates': torch.tensor([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),
    'rev_rates': torch.tensor([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),
  })

  data_con_edge_sub_graph['user', 'rates', 'movie'].edge_label_index = data_con_edge_sub_graph[
    'user', 'rates', 'movie'].edge_index

  # transform = RemoveIsolatedNodes()
  # data_rotto_usabile_solo_una_volta = transform(data_rotto_usabile_solo_una_volta)

  utility.write_to_graph_format(data_con_edge_sub_graph['user', 'rates', 'movie'].edge_index,
                                ROOT_DIR + '/winner_graph' + '.txt')

  # print(torch.eq(data_rotto_usabile_solo_una_volta['user', 'rates', 'movie'].edge_index[0], edge_index[0]))

  final_hetero_data, final_predictions, model = allAlberto(data)

  data['user', 'rates', 'movie'].edge_label_index = data[
    'user', 'rates', 'movie'].edge_index

  ######################################

  start_time = time.time()
  prediction = model_ml.predict_with_GNN(data_con_edge_sub_graph, model)
  end_time = time.time()
  print(f"Execution time for edge_subgraph_data: {end_time - start_time} seconds")
  print(len(prediction))

  start_time = time.time()
  prediction = model_ml.predict_with_GNN(data_con_sub_graph, model)
  end_time = time.time()
  print(f"Execution time for subgraph_data: {end_time - start_time} seconds")
  print(len(prediction))

  start_time = time.time()
  prediction = model_ml.predict_with_GNN(data, model)
  end_time = time.time()
  print(f"Execution time for all data: {end_time - start_time} seconds")
  print(len(prediction))

  # Poichè quando viene fatto subgraph si rompe un po tutto, l'idea è che gli viene passato il data prinicpale e edge_index e non verrà modificato mai data, ma verrà creato new_data
  monte_carlo = MonteCarlo(heterodata=data, edge_index=edge_index, deepnes_of_node_expansion=10, model=model,
                           prediction_to_evaluate_index=1, min_graph_number_of_edges=6, number_of_brother=1000000, edge=[torch.tensor(0),torch.tensor(1)])
  monte_carlo.search()

  print('fine')


if __name__ == '__main__':
  run_every_things()
