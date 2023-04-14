import os
import numpy as np
import pandas as pd
import torch
import itertools
from torch_geometric.data import HeteroData
from torch_geometric.transforms import ToUndirected

import defensive_programming
from MySQL_to_BigQuery import trasferisci_mysql_a_big_query
from alberto import remove_duplicate_columns, find_sub_edge_positions
from generate_csv_json_mysql_from_log import run_all_pipeline_to_update_json_and_my_sql
from model_ml import allAlberto
from montecarlo_with_diff import MonteCarloWithDiff
from neo4j_carica_dati import Neo4jCRUD
import torch_geometric.transforms as T

from neo4j_queries import get_subgraph_from_neo4j_to_explainability

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def crea_grafo_su_neo4j():
  uri = "bolt://localhost:7687"
  user = 'neo4j'
  password = 'neo4jneo4j'
  neo4jCRUD = Neo4jCRUD(uri, user, password)

  df = pd.read_csv(ROOT_DIR + '/movielens_final.csv')

  edge_index = df[['userId', 'movieId']].values
  edge_index = torch.tensor(edge_index.T)
  edge_label = df['rating'].values
  edge_label = torch.tensor(edge_label)
  neo4jCRUD.delete_all_nodes_and_relationships()
  neo4jCRUD.load_data_to_neo4j(edge_index, edge_label)
  print('Fine caricamento dati')


def get_hetero_data():
  device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

  df = pd.read_csv(ROOT_DIR + '/movielens_final.csv', index_col=0)

  def GenresEncoder(data):
    gen = []
    for i in range(len(data)):
      gen.append(data.iloc[i]['genres'])

    unique_gen = set(list(itertools.chain(*gen)))
    print("Number of unqiue genres we have:", unique_gen)
    mapping = {g: i for i, g in enumerate(unique_gen)}
    x = torch.zeros(len(gen), len(mapping))
    for i, m_gen in enumerate(gen):
      for genre in m_gen:
        x[i, mapping[genre]] = 1
    return x.to(device)

  df_items = df.groupby('movieId').first()

  # scale release years
  years = [df_items.iloc[i]['release year'] for i in range(len(df_items))]
  years_enc = [(years[i] - min(years)) / (max(years) - min(years)) for i in range(len(years))]
  df_items['release year'] = years_enc

  from sentence_transformers import SentenceTransformer

  encoder = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')  # embedding up to 512 tokens

  title_embedding = encoder.encode(df_items['title'].to_list(), show_progress_bar=True, convert_to_tensor=True)
  df_items['directedBy'] = df_items['directedBy'].replace(np.nan, '')
  director_embedding = encoder.encode(df_items['directedBy'].to_list(), show_progress_bar=True, convert_to_tensor=True)
  genres_embedding = GenresEncoder(df_items)
  year_encoded = torch.tensor(list(df_items['release year']), device=device).unsqueeze(1)

  item_x = torch.cat([title_embedding, director_embedding, genres_embedding, year_encoded], dim=-1)

  edge_index = torch.tensor([list(df.userId), list(df.movieId)], device=device)
  edge_label = torch.tensor(list(df.rating), device=device)
  edge_label = edge_label / 5

  data = HeteroData()

  # define nodes and edges in graph
  data['user'].num_nodes = len(df.userId.unique())
  data['user'].x = torch.eye(data['user'].num_nodes, device=device)
  data['item'].x = torch.tensor(item_x, device=device, dtype=torch.float32)
  del data['user'].num_nodes
  data['user', 'rates', 'item'].edge_index = edge_index
  data['user', 'rates', 'item'].edge_label = edge_label

  # make the graph undirected so it can perform message passing
  data = ToUndirected()(data)
  del data['item', 'rev_rates', 'user'].edge_label

  data = data.to(device)

  print(data)

  return data


if __name__ == '__main__':

  data = get_hetero_data()

  edge_index, edge_label = get_subgraph_from_neo4j_to_explainability('1', 1)

  data_clone = data.clone()

  data_clone['user', 'rates', 'item'].edge_label_index = edge_index

  final_hetero_data, final_predictions, model = allAlberto(data_clone)

  edge_index = remove_duplicate_columns(edge_index)

  positions = find_sub_edge_positions(data_clone['user', 'rates', 'item'].edge_index, edge_index)

  new_data = data_clone.edge_subgraph({
    'rates': torch.tensor(positions),
    'rev_rates': torch.tensor(positions),
  })

  new_data['user', 'rates', 'item'].edge_label_index = new_data[
    'user', 'rates', 'item'].edge_index

  if not torch.eq(new_data['user', 'rates', 'item'].edge_index, edge_index).all():
    defensive_programming.DefensiveProgramming.launch_alert(None,
                                                            "I tensori new_data['user', 'rates', 'item'].edge_index e edge_index sono diversi.")

  edge = [torch.tensor(609), torch.tensor(6490)]
  #edge = [torch.tensor(1), torch.tensor(4607)]
  #edge = [torch.tensor(1), torch.tensor(5294)]
  #edge = [torch.tensor(1), torch.tensor(6235)]
  #edge = [torch.tensor(1), torch.tensor(6297)]
  #edge = [torch.tensor(1), torch.tensor(6692)]
  deepnes = 2

  for i in range(60):


    monte_carlo = MonteCarloWithDiff(heterodata=new_data, edge_index=None, deepnes_of_node_expansion=deepnes,
                                     min_graph_number_of_edges=5, model=model,
                                     edge=edge,
                                     number_of_brother=1)
    print('istanza montecarlo creata')
    win_dic, list_of_final_dic = monte_carlo.search()
    deepnes = deepnes + 60
    print('fine montecarlo')

  run_all_pipeline_to_update_json_and_my_sql()
  trasferisci_mysql_a_big_query()  ## Queste due righe che sono la fine della pipeline totale non possono ancora essere eseguite, perchè errore biguery table not found

  print('Fine')
