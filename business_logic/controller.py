import os

import torch
from flask import Flask, request, send_file, render_template
from alberto import ottieni_etero_data, get_index_starting_from_nodes
from model_ml import allAlberto
from montecarlo import MonteCarlo
from neo4j_queries import MyNeo4j

app = Flask(__name__)

#### nota del 29 marzo: RIcordarsi che non si può fare explainability sull'edge 0 del grafo perchè quello è tolto di default (in montecarlo simulation)
@app.route('/')
def hello_world():
  return 'Hello, World!'


@app.route('/get_json_of_best_subgraph_level_1')
def get_json_lv1():
  ## UserID, Rating, ItemID
  print('Chiamato get_json_of_best_subgraph_level_1')

## http://127.0.0.1:8080/get_json_of_best_subgraph_level_1?source_node=311&target_node=872
  source_node_userID = request.args.get('source_node')
  target_node_itemID = request.args.get('target_node')

  data, edge_index_level_1, edge = ottieni_etero_data(source_node_userID, target_node_itemID)
  data_clone = data.clone()
  final_hetero_data, final_predictions, model = allAlberto(data_clone)


  uri = "neo4j://34.154.222.156:7687"
  user = "neo4j"
  password = "Ontologia235g!"
  myNeo4j = MyNeo4j(uri, user, password)
  ### Dallo user_encoding passato come argomento ottengo userId
  results = myNeo4j.run_query(
    'MATCH (u:User{userId:"https://www.merlot.org/merlot/viewMember.htm?id=248734"})-[r:HAS_RATED]-(a:Article) return u.encoding, a.encoding')

  ## prediction_to_evaluate_index viene calcolato direttamente all'interno di montecarlo
  montecarlo = MonteCarlo(heterodata=data, edge_index=edge_index_level_1, deepnes_of_node_expansion=int(2),
                          min_graph_number_of_edges=int(2), model=model,
                           edge=edge,
                          number_of_brother=0)
  montecarlo.search()

  try:
    return send_file('winner_graph.json', attachment_filename='/winner_graph.json', as_attachment=True,
                     mimetype='application/json')
  except Exception as e:
    return str(e)


@app.route('/get_json_of_best_subgraph_starting_from_complete_graph')
def get_json_lv2():

  ## UserID, Rating, ItemID
  print('Chiamato get_json_of_best_subgraph_starting_from_complete_graph')

  ## http://127.0.0.1:8080/get_json_of_best_subgraph_level_1?source_node=311&target_node=872
  source_node = request.args.get('source_node')
  target_node = request.args.get('target_node')

  data = ottieni_etero_data(source_node, target_node)
  data_clone = data.clone()
  final_hetero_data, final_predictions, model = allAlberto(data_clone)

  edge = [torch.tensor(int(source_node)), torch.tensor(int(target_node))]
  prediction_index = get_index_starting_from_nodes(data['user', 'rates', 'item'].edge_index, edge)
  print(prediction_index)

  uri = "neo4j://34.154.222.156:7687"
  user = "neo4j"
  password = "Ontologia235g!"
  myNeo4j = MyNeo4j(uri, user, password)
  ### Dallo user_encoding passato come argomento ottengo userId
  results = myNeo4j.run_query(
    'MATCH (u:User{userId:"https://www.merlot.org/merlot/viewMember.htm?id=248734"})-[r:HAS_RATED]->(a:Article)<-[r1:HAS_RATED]-(u1:User)-[r2:HAS_RATED]->(a1:Article) return u.encoding, a.encoding, u1.encoding, a1.encoding, u1.encoding, a1.encoding')

#################################################################
  # Estrai i valori 'u.encoding' e 'a.encoding' dalla lista
  a_encodings = [int(item['a.encoding']) for item in results if item['a.encoding'] is not None]
  u_encodings = []
  u = int(results[0]['u.encoding'])
  for i in range(len(a_encodings)):
    u_encodings.append(u)
  edge_index = torch.tensor([u_encodings, a_encodings])
  print(edge_index)
#################################################################

  montecarlo = MonteCarlo(heterodata=data, edge_index=edge_index, deepnes_of_node_expansion=int(3),
                          min_graph_number_of_edges=int(3), model=model,
                           edge=edge,
                          number_of_brother=0)
  montecarlo.search()

  try:
    return send_file('winner_graph.json', attachment_filename='/winner_graph.json', as_attachment=True,
                     mimetype='application/json')
  except Exception as e:
    return str(e)
@app.route('/get_html_of_best_graph')
def get_html():
  return render_template('winner_graph.html')


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
