import os

import torch
from flask import Flask, request, send_file, render_template
from alberto import ottieni_etero_data, get_index_starting_from_nodes
from model_ml import allAlberto
from montecarlo import MonteCarlo
from neo4j_queries import MyNeo4j

app = Flask(__name__)

#### nota del 29 marzo: Ricordarsi che non si può fare explainability sull'edge 0 del grafo perchè quello è tolto di default (in montecarlo simulation)
@app.route('/')
def hello_world():
  return 'Hello, World!'


@app.route('/get_json_of_best_subgraph_level_1')
def get_json_lv1():

  ## UserID, Rating, ItemID
  print('Chiamato get_json_of_best_subgraph_level_1')

## http://127.0.0.1:8080/get_json_of_best_subgraph_level_1?source_node=311&target_node=674
  source_node_userID = request.args.get('source_node')
  target_node_itemID = request.args.get('target_node')

  data, edge_index_level_1, edge = ottieni_etero_data(source_node_userID, target_node_itemID)
  data_clone = data.clone()
  final_hetero_data, final_predictions, model = allAlberto(data_clone)

  deepnes_of_node_expansion = 0
  min_graph_number_of_edges = 0

  print('Dimensione grafo iniziale: '+ str(len(edge_index_level_1[0])))

  if len(edge_index_level_1[0]) < 5:
    return 'Grafo troppo piccolo per fare explainability'

  if 10 > len(edge_index_level_1[0]) > 5:
    deepnes_of_node_expansion = 2
    min_graph_number_of_edges = 2

  if len(edge_index_level_1[0]) > 10:
    deepnes_of_node_expansion = 4
    min_graph_number_of_edges = 6


  ## prediction_to_evaluate_index viene calcolato direttamente all'interno di montecarlo
  montecarlo = MonteCarlo(heterodata=data, edge_index=edge_index_level_1, deepnes_of_node_expansion=int(deepnes_of_node_expansion),
                          min_graph_number_of_edges=int(min_graph_number_of_edges), model=model,
                           edge=edge,
                          number_of_brother=0)
  montecarlo.search()

  try:
    return send_file('winner_graph.json', attachment_filename='/winner_graph.json', as_attachment=True,
                     mimetype='application/json')
  except Exception as e:
    return str(e)


@app.route('/get_json_of_best_subgraph_starting_from_complete_graph')
def get_json_all_graph():

  ## UserID, Rating, ItemID
  print('Chiamato get_json_of_best_subgraph_starting_from_complete_graph')

  ## http://127.0.0.1:8080/get_json_of_best_subgraph_starting_from_complete_graph?source_node=311&target_node=872
  source_node = request.args.get('source_node')
  target_node = request.args.get('target_node')

  data, _, _= ottieni_etero_data(source_node, target_node)
  data_clone = data.clone()
  final_hetero_data, final_predictions, model = allAlberto(data_clone)

  edge = [torch.tensor(int(source_node)), torch.tensor(int(target_node))]

  montecarlo = MonteCarlo(heterodata=data, edge_index=None, deepnes_of_node_expansion=int(3),
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
