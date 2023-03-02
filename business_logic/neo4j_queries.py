import os
import torch
from neo4j import GraphDatabase
import defensive_programming
import utility

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_data(data):
  rows = []
  cols = []
  labels = []
  for item in data:
    rows.append(int(item['u1']['name']))
    labels.append(float(item['r1.rating']))
    cols.append(int(item['m1']['name']))
    rows.append(int(item['u2']['name']))
    labels.append(float(item['r2.rating']))
    cols.append(int(item['m1']['name']))
    rows.append(int(item['u2']['name']))
    labels.append(float(item['r3.rating']))
    cols.append(int(item['m2']['name']))
  return torch.tensor([rows, cols]), torch.tensor(labels)


def remove_duplicate_columns(tensor_indices, tensor_label):
  tensor_t = tensor_indices.t()
  unique_tensor, indices = torch.unique(tensor_t, return_inverse=True, dim=0)
  unique_tensor = unique_tensor.t()
  repeated_elements = []
  new_tensor_label = []

  for i, element in enumerate(indices):
    if element not in repeated_elements:
      new_tensor_label.append(tensor_label[element])
      repeated_elements.append(element)
    else:
      continue

  return unique_tensor, new_tensor_label


class MyNeo4j:

  def __init__(self, uri, user, password):
    self.uri = uri
    self.user = user
    self.password = password
    self.driver = GraphDatabase.driver(uri, auth=(user, password))

  def close(self):
    # Don't forget to close the driver connection when you are finished with it
    self.driver.close()

  def run_query(self, query):
    with self.driver.session() as session:
      result = session.run(query)
      return result.data()


def get_subgraph_from_neo4j_to_explainability(user_number, number_of_brothers):

  uri = "bolt://localhost:7687"
  user = "neo4j"
  password = "3X1fJlNK_hQ2qIM8yn-Iz4tcOhsQNHgR7W8TVkatKwA"
  myNeo4j = MyNeo4j(uri, user, password)

  query_retrive_users = f'MATCH (u:User {{name: "{user_number}"}})-[r:RATES]->(n)<-[:RATES]-(u1) RETURN u1.name'



  results = myNeo4j.run_query(query_retrive_users)



  users = []
  for element in results:
    # if users contain element['u1.name'] then continue
    if element['u1.name'] in users:
      continue
    users.append(element['u1.name'])



  ## eliminate the last 55 users of 57 total users
  users = users[:-(len(users)-number_of_brothers)]

  ## Una soluzione può essere calcolare tutti gli user che si trovano a 2 hop di distanza e successivamente porvare a limitare il numero di user dopo

  #query = f'MATCH (u1)-[r1:RATES]->(m1)<-[r2:RATES]-(u2:User {{name: "{user_number}"}})-[r3:RATES]->(m2) RETURN u1, r1.rating, m1, r2.rating, u2, m2, r3.rating limit ' + limit
  #query = f'MATCH (u1)-[r1:RATES]->(m1)<-[r2:RATES]-(u2:User {{name: "{user_number}"}})-[r3:RATES]->(m2) WHERE toInteger(m2.name) < 30 RETURN u1, r1.rating, m1, r2.rating, u2, m2, r3.rating'

  user_filter = ' OR '.join([f'u2.name = "{name}"' for name in users])
  #query = f'MATCH (u1:User {{name: "{user_number}"}})-[r1:RATES]->(m1)<-[r2:RATES]-(u2)-[r3:RATES]->(m2) RETURN u1, r1.rating, m1, r2.rating, u2, m2, r3.rating limit ' + limit

  query = f'MATCH (u1:User {{name: "{user_number}"}})-[r1:RATES]->(m1)<-[r2:RATES]-(u2)-[r3:RATES]->(m2) WHERE {user_filter} RETURN u1, r1.rating, m1, r2.rating, u2, m2, r3.rating'

  print(query)
  results = myNeo4j.run_query(query)
  edge_index, edge_label = parse_data(results)
  edge_index, edge_label = remove_duplicate_columns(edge_index, edge_label)
  utility.write_to_graph_format(edge_index, ROOT_DIR + '/winner_graph' + '.txt')
  print('Fine caricamento dati da neo4j')

  return edge_index, edge_label


if __name__ == "__main__":
  get_subgraph_from_neo4j_to_explainability("0")
