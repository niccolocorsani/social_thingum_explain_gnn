import os
import torch
import defensive_programming
import neo4j_queries
from MySQL_to_BigQuery import trasferisci_mysql_a_big_query
from generate_csv_json_mysql_from_log import run_all_pipeline_to_update_json_and_my_sql
from model_ml import allAlberto
from montecarlo import MonteCarlo, get_index_starting_from_nodes
from utility import read_data

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



if __name__ == '__main__':


  prediction_index = 67

  number_of_brothers = 2

  ## Cose da preprocessing
  device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
  data, edge_index = read_data()
  data['user','rates','item'].edge_label_index =  data['user','rates','item'].edge_index
  print('Tutto edge_index: ')
  print(len(data['user', 'rates', 'item'].edge_index[0]))
  user = edge_index[0][int(prediction_index)]
  edge_index, _ = neo4j_queries.get_subgraph_from_neo4j_to_explainability(user_number=str(user.item()),
                                                                          number_of_brothers=int(number_of_brothers))
  data_clone = data.clone()
  final_hetero_data, final_predictions, model = allAlberto(data_clone)


#### Da rimuovere assolutamente in produzione
  # defensiveProgramming = defensive_programming.DefensiveProgramming()
  # data['user', 'rates', 'item'].edge_label_index = data['user', 'rates', 'item'].edge_index
  # defensiveProgramming.evaluate(test_data=data, model=model)
#### Da rimuovere assolutamente in produzione

  edge = [edge_index[0][int(prediction_index)], edge_index[1][int(prediction_index)]]

  prediction_index = get_index_starting_from_nodes(edge_index, edge)
  print(edge)

  deepnes = 2
  min_edges = 4

  for i in range(60):
    print(i)
    deepnes = deepnes + 5
    #min_edges = min_edges + i

    monte_carlo = MonteCarlo(heterodata=data, edge_index=edge_index, deepnes_of_node_expansion=int(deepnes),
                             min_graph_number_of_edges=int(min_edges), model=model,
                              edge=edge,
                             number_of_brother=number_of_brothers)
    print('istanza montecarlo creata')
    win_dic, list_of_final_dic = monte_carlo.search()

  run_all_pipeline_to_update_json_and_my_sql()
  trasferisci_mysql_a_big_query()   ## Queste due righe che sono la fine della pipeline totale non possono ancora essere eseguite, perchè errore biguery table not found

  print('Fine')
