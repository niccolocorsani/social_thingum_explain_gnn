## Dipendenze di terzi
import pandas as pd
import requests
import torch
from torch_geometric.transforms import ToUndirected
from torch_geometric.data import HeteroData
from sklearn.preprocessing import LabelEncoder
import json
from sentence_transformers import SentenceTransformer
from requests.auth import HTTPBasicAuth
## Dipendenze mie
from model_ml import allAlberto
from montecarlo import MonteCarlo
from neo4j_queries import MyNeo4j

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def get_index_starting_from_nodes(edge_index, edge):
  for i in range(edge_index.shape[1]):
    if edge_index[:, i][0] == edge[0].item() and edge_index[:, i][1] == edge[1].item():
      return i
  return None


def Encoder(data, metadata):
  items = []
  for i in range(len(data)):
    items.append(data.iloc[i][metadata])

  unique_locs = set(items)
  print("Number of unqiue items we have:", unique_locs)
  mapping = {g: i for i, g in enumerate(unique_locs)}
  x = torch.zeros(len(items), len(mapping))
  for i, m_lang in enumerate(items):
    x[i, mapping[m_lang]] = 1
  return x.to(device)


## Gli passo lo userId dal frontend
def ottieni_etero_data(source_node_userID, target_node_itemID):
  request = requests.get(
    'https://whoteach-scraper-microservice-agpvmcasea-oc.a.run.app/user/ratingsData', auth=HTTPBasicAuth(
      'dbZjdqRpqCup@neo4j', '30bqlw8c325D1AtK'), headers={'Accept': 'application/json'})

  df = json.loads(request.content)
  df = pd.DataFrame(df)
  columns = ['title', 'difficulty', 'domain', 'format', 'type', 'language']
  for col in columns:
    df[col] = [df.iloc[i].article[col] for i in range(len(df))]
    df.dropna(inplace=True)
    df[col] = [df.iloc[i][col][col] for i in range(len(df))]
  df['itemId'] = [int(df.iloc[i].article['id']) for i in range(len(df))]
  df['url'] = [df.iloc[i].article['url'] for i in range(len(df))]

  df['encoding'] = [df.iloc[i].article['encoding'] for i in range(len(df))]
  df["encoding"] = pd.to_numeric(df["encoding"])

  df['min_age'] = [int(df.iloc[i].article['minAge']['minAge']) for i in range(len(df))]
  df['rate'] = [int(df.iloc[i]['rate']) for i in range(len(df))]
  df.rename(columns={'id': 'itemId'}, inplace=True)
  df = df[df.rate > 0]
  for i in range(0, len(df)):
    keywords = ""
    for x in df.iloc[i].article['keywords']:
      keywords += x["keywords"] + ','
    df.at[i, "keywords"] = keywords

  df = df[df.rate > 0]
  df.drop('article', axis=1, inplace=True)
  df.dropna(inplace=True)

  label_enc = LabelEncoder()

  df['enc_user'] = label_enc.fit_transform(df.userId)
  df['enc_item'] = label_enc.fit_transform(df.itemId)

  uri = "neo4j://34.154.222.156:7687"
  user = "neo4j"
  password = "Ontologia235g!"
  myNeo4j = MyNeo4j(uri, user, password)

  df = df[['enc_user', 'userId', 'enc_item', 'encoding', 'itemId', 'rate', 'title', 'difficulty', 'domain', 'min_age',
           'language', 'type', 'format', 'keywords']]

###### Codice per ottenere il sotto grafo e l'edge su cui fare explainability
  source_node_userID = '248734'  ## da eliminare questo mock in produzione
  target_node_itemID = 297100  ## da eliminare questo mock in produzione ## TODO attenzione ai controlli qui sotto perchè itemId è un float e non int, nell == ci sta dia problemi
  results = myNeo4j.run_query(
    'MATCH (u:User{userId:"https://www.merlot.org/merlot/viewMember.htm?id=' + source_node_userID + '"})-[r:HAS_RATED]-(a:Article) return u, id(a)')
  edge_index_level_1 = [[], []]
  for element in results:
    try:
      element['id(a)'] = int(element['id(a)'])
      edge_index_level_1[1].append(df[df.itemId == element['id(a)']]["enc_item"].iloc[0])
      edge_index_level_1[0].append(df[df.userId == element['u']['userId']]['enc_user'].iloc[0])
    except:
      continue
  source = int(
    df[df.userId == 'https://www.merlot.org/merlot/viewMember.htm?id=' + source_node_userID]["enc_user"].iloc[0].item())
  target = int(df[df.itemId == target_node_itemID]["enc_item"].iloc[0].item())
  edge = torch.tensor([source, target])
###### Codice per ottenere il sotto grafo e l'edge su cui fare explainability

  # results = myNeo4j.run_query(
  #   'MATCH (u:User{userId:"https://www.merlot.org/merlot/viewMember.htm?id=2 48734"})-[r:HAS_RATED]->(a:Article)<-[r1:HAS_RATED]-(u1:User)-[r2:HAS_RATED]->(a1:Article) return u.userId, id(a), u1.userId, id(a1)')
  #
  # edge_index_to_test = [[], []]

  # for element in results:
  #     element['id(a)'] = int(element['id(a)'])
  #     try :
  #       df[df.userId==element['u.userId']]["enc_user"].iloc[0]
  #     except:
  #       continue
  #
  #     try :
  #       df[df.itemId==element['id(a)']]["enc_item"].iloc[0]
  #     except:
  #       continue
  #     edge_index_to_test[0].append(df[df.userId==element['u.userId']]["enc_user"].iloc[0])
  #     edge_index_to_test[1].append(df[df.itemId==element['id(a)']]["enc_item"].iloc[0])
  #
  # for element in results:
  #   try:
  #     df[df.userId == element['u1.userId']]["enc_user"].iloc[0]
  #   except:
  #     continue
  #   try:
  #     df[df.itemId == element['id(a)']]["enc_item"].iloc[0]
  #   except:
  #     continue
  #     edge_index_to_test[0].append(df[df.userId==element['u1.userId']]["enc_user"].iloc[0])
  #     edge_index_to_test[1].append(df[df.itemId==element['id(a)']]["enc_item"].iloc[0])
  #
  # for element in results:
  #   try:
  #     df[df.userId == element['u1.userId']]["enc_user"].iloc[0]
  #   except:
  #     continue
  #   try:
  #     df[df.itemId == element['id(a1)']]["enc_item"].iloc[0]
  #   except:
  #     continue
  #     edge_index_to_test[0].append(df[df.userId==element['u1.userId']]["enc_user"].iloc[0])
  #     edge_index_to_test[1].append(df[df.itemId==element['id(a1)']]["enc_item"].iloc[0])

  df_items = df.groupby('enc_item').first()[
    ['title', 'language', 'domain', 'format', 'type', 'difficulty', 'min_age', 'keywords']]
  map_difficulty = {'undefined': 0.2, 'Medio Bassa': 0.4, 'Media': 0.6, 'Medio Alta': 0.8, 'Alta': 1}
  df_items.difficulty = df_items.difficulty.map(map_difficulty)
  ages = [df_items.iloc[i].min_age for i in range(len(df_items))]
  ages_enc = [(ages[i] - min(ages)) / (max(ages) - min(ages)) for i in range(len(ages))]
  df_items.min_age = ages_enc
  encoder = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')  # embedding up to 512 tokens
  title_embedding = encoder.encode(df_items['title'].to_list(), show_progress_bar=True, convert_to_tensor=True)
  keywords_embedding = encoder.encode(df_items['keywords'].to_list(), show_progress_bar=True, convert_to_tensor=True)
  encoded_languages = Encoder(df_items, 'language')
  encoded_formats = Encoder(df_items, 'format')
  encoded_types = Encoder(df_items, 'type')
  encoded_domains = Encoder(df_items, 'domain')



  age_encoded = torch.tensor(list(df_items.min_age), device=device).unsqueeze(1)
  difficulty_encoded = torch.tensor(list(df_items.difficulty), device=device).unsqueeze(1)
  item_x = torch.cat(
    [keywords_embedding, encoded_languages, difficulty_encoded, age_encoded, encoded_formats, encoded_types,
     encoded_domains], dim=-1)
  edge_index = torch.tensor([list(df.enc_user), list(df.enc_item)], device=device)
  edge_label = torch.tensor(list(df.rate), device=device)
  edge_label = edge_label / 5

  data = HeteroData()
  data['user'].num_nodes = len(df.enc_user.unique())
  data['user'].x = torch.eye(data['user'].num_nodes, device=device)
  data['item'].x = torch.tensor(item_x, device=device, dtype=torch.float32)
  del data['user'].num_nodes
  data['user', 'rates', 'item'].edge_index = edge_index
  data['user', 'rates', 'item'].edge_label = edge_label
  data['user', 'rates', 'item'].edge_label_index = edge_index

  data = ToUndirected()(data)

  del data['item', 'rev_rates', 'user'].edge_label
  data = data.to(device)

  print('Fine caricamento dati da ottieni_etero_data')

  return data, torch.tensor(edge_index_level_1), edge


if __name__ == '__main__':
  # print('Chiamato get_json_of_best_subgraph_level_1')
  #
  # ## http://127.0.0.1:8080/get_json_of_best_subgraph_level_1?source_node=311&target_node=872
  # source_node = None  ## TODO ripensare a discorso che primo edge dell'edge_index dava errore
  # target_node = None
  #
  # data, edge_index_test, edge = ottieni_etero_data(source_node, target_node)
  # edge_index_test = torch.tensor(edge_index_test)
  # data_clone = data.clone()
  # final_hetero_data, final_predictions, model = allAlberto(data_clone)
  #
  # montecarlo = MonteCarlo(heterodata=data, edge_index=edge_index_test, deepnes_of_node_expansion=int(1),
  #                         min_graph_number_of_edges=int(1), model=model,
  #                         edge=edge,
  #                         number_of_brother=0)
  # montecarlo.search()
  #
  print('Chiamato su tutto il grafo')

  ## http://127.0.0.1:8080/get_json_of_best_subgraph_level_1?source_node=311&target_node=872
  source_node = None
  target_node = None

  data, _ , edge = ottieni_etero_data(source_node, target_node)
  data_clone = data.clone()
  final_hetero_data, final_predictions, model = allAlberto(data_clone)

  montecarlo = MonteCarlo(heterodata=data, edge_index=None, deepnes_of_node_expansion=int(2),
                          min_graph_number_of_edges=int(5750), model=model,
                          edge=edge,
                          number_of_brother=0)
  montecarlo.search()

