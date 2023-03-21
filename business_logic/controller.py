import torch
from flask import Flask, request

from alberto import ottieni_etero_data, get_index_starting_from_nodes
from model_ml import allAlberto
from montecarlo import MonteCarlo

app = Flask(__name__)

@app.route('/')
def hello_world():

  data = ottieni_etero_data()
  data_clone = data.clone()
  final_hetero_data, final_predictions, model = allAlberto(data_clone)

  edge = [torch.tensor(311), torch.tensor(872)]
  prediction_index = get_index_starting_from_nodes(data['user', 'rates', 'item'].edge_index, edge)
  print(prediction_index)

  montecarlo = MonteCarlo(heterodata=data, edge_index=data[
    'user', 'rates', 'item'].edge_index, deepnes_of_node_expansion=int(20),
                          min_graph_number_of_edges=int(20), model=model,
                          prediction_to_evaluate_index=int(prediction_index), edge=edge,
                          number_of_brother=0)
  montecarlo.search()

  return 'Hello, World!'

@app.route('/api/v1/get_json_of_best_subgraph')
def api_hello_v1():

  # http://127.0.0.1:5000/api/v1/get_json_of_best_subgraph?source_node=e&target_node=9
    source_node = request.args.get('source_node')
    target_node = request.args.get('target_node')

    data = ottieni_etero_data()
    data_clone = data.clone()
    final_hetero_data, final_predictions, model = allAlberto(data_clone)

    edge = [torch.tensor(int(source_node)), torch.tensor(int(target_node))]
    prediction_index = get_index_starting_from_nodes(data['user', 'rates', 'item'].edge_index, edge)
    print(prediction_index)

    montecarlo = MonteCarlo(heterodata=data, edge_index=data[
      'user', 'rates', 'item'].edge_index, deepnes_of_node_expansion=int(20),
                            min_graph_number_of_edges=int(20), model=model,
                            prediction_to_evaluate_index=int(prediction_index), edge=edge,
                            number_of_brother=0)
    montecarlo.search()






    return f'Source Node: {source_node}, Target Node: {target_node}'

@app.route('/api/v2/hello')
def api_hello_v2():
    return 'Hello, World! - API v2'

if __name__ == '__main__':
    app.run()
