import pandas as pd
import requests
import torch
from torch_geometric.transforms import  ToUndirected
from torch_geometric.data import HeteroData
from sklearn.preprocessing import LabelEncoder
import json
from sentence_transformers import SentenceTransformer
from requests.auth import HTTPBasicAuth
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


def ottieni_etero_data():
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
  df['min_age'] = [int(df.iloc[i].article['minAge']['minAge']) for i in range(len(df))]
  df['rate'] = [int(df.iloc[i]['rate']) for i in range(len(df))]
  df.rename(columns={'id': 'itemId'}, inplace=True)
  df = df[
    df.rate > 0]  # df['rate'] = df['rate'].replace(0, 4)
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

############ Da levare
  # for each element of df['enc_user'] print element
  for i in range(len(df['enc_user'])):
    query = 'match(n:User {userId:"' + str(df['userId'][i]) + '"}) set n.user_id_enc="' + str(df['enc_user'][i]) + '"'
    print(query)
    myNeo4j.run_query(query)
############ Da levare

  df = df[['enc_user', 'userId', 'enc_item', 'itemId', 'rate', 'title', 'difficulty', 'domain', 'min_age', 'language', 'type','format', 'keywords']]

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
  item_x.shape
  edge_index = torch.tensor([list(df.enc_user), list(df.enc_item)], device=device)

  edge_label = torch.tensor(list(df.rate), device=device)
  edge_label = edge_label / 5
  data = HeteroData()
  data['user'].num_nodes = len(df.enc_user.unique())
  data['user'].x = torch.eye(data['user'].num_nodes, device=device)
  data['item'].x = torch.tensor(item_x, device=device, dtype=torch.float32)
  del data['user'].num_nodes
  data['user', 'rates', 'item'].edge_index = edge_index
  data[
    'user', 'rates', 'item'].edge_label = edge_label

  data[
    'user', 'rates', 'item'].edge_label_index = edge_index

  print(data[
    'user', 'rates', 'item'].edge_label_index)

  data = ToUndirected()(data)

  del data['item', 'rev_rates', 'user'].edge_label
  data = data.to(device)

  print(data[
          'user', 'rates', 'item'].edge_label_index)


  return data


if __name__ == '__main__':

  data = ottieni_etero_data()
  data_clone = data.clone()
  final_hetero_data, final_predictions, model = allAlberto(data_clone)

  edge = [torch.tensor(311),torch.tensor(872)]
  prediction_index = get_index_starting_from_nodes(data['user', 'rates', 'item'].edge_index , edge)
  print(prediction_index)




  montecarlo = MonteCarlo(heterodata=data, edge_index=data[
    'user', 'rates', 'item'].edge_index, deepnes_of_node_expansion=int(20),
                                        min_graph_number_of_edges=int(20), model=model,
                                        prediction_to_evaluate_index=int(prediction_index), edge=edge,
                                        number_of_brother=0)
  montecarlo.search()
