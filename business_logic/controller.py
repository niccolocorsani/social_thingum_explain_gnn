import os

import torch
from flask import Flask, request, send_file, render_template
from alberto import ottieni_etero_data, get_index_starting_from_nodes
from model_ml import allAlberto
from montecarlo import MonteCarlo

app = Flask(__name__)

@app.route('/')
def hello_world():

  return 'Hello, World!'

@app.route('/get_json_of_best_subgraph')
def get_json():

  # http://127.0.0.1:5000/get_json_of_best_subgraph?source_node=311&target_node=872
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


    try:

      return send_file('winner_graph.json', attachment_filename='/winner_graph.json', as_attachment=True,
                       mimetype='application/json')

    except Exception as e:

      return str(e)

@app.route('/get_html_of_best_graph')
def get_html():
  return render_template('winner_graph.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
