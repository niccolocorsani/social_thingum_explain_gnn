import os

import torch

import neo4j_queries
from model_ml import allAlberto
from montecarlo import MonteCarlo
from utility import read_data, removeFilesFromFolder

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':



  prediction_index = 90
  number_of_brothers = 4

  ## Cose da preprocessing
  device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
  data, edge_index = read_data()
  print('Tutto edge_index: ')
  print(len(data['user', 'rates', 'movie'].edge_index[0]))
  user = edge_index[0][int(prediction_index)]
  edge_index, _ = neo4j_queries.get_subgraph_from_neo4j_to_explainability(user_number=str(user.item()),
                                                                          number_of_brothers=int(number_of_brothers))
  data_clone = data.clone()
  final_hetero_data, final_predictions, model = allAlberto(data_clone)
  edge = [edge_index[0][int(prediction_index)], edge_index[1][int(prediction_index)]]

  print(edge)


  deepnes = 2
  min_edges = 4

  for i in range(100):

    print(i)

    deepnes = deepnes + 1
  #  min_edges = min_edges + i

    monte_carlo = MonteCarlo(heterodata=data, edge_index=edge_index, deepnes_of_node_expansion=int(deepnes),
                             min_graph_number_of_edges=int(min_edges), model=model,
                             prediction_to_evaluate_index=int(prediction_index), edge=edge, number_of_brother=number_of_brothers)
    win_dic, list_of_final_dic = monte_carlo.search()
