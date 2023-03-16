import os
import socketserver
import sys
import torch
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QTextEdit, QHBoxLayout, \
  QVBoxLayout, QWidget, QMessageBox
import neo4j_queries
import utility
from defensive_programming import DefensiveProgramming
from model_ml import allAlberto, predict_with_GNN, ModelGAT1
from montecarlo import MonteCarlo
from utility import read_data, removeFilesFromFolder

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
torch.set_printoptions(threshold=100000)


def get_index_starting_from_nodes(edge_index, edge):
  for i in range(edge_index.shape[1]):
    if edge_index[:, i][0] == edge[0].item() and edge_index[:, i][1] == edge[1].item():
      return i
  return None

class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.initUI()

  def initUI(self):
    # Set window title
    self.setWindowTitle('Simulation UI')

    # Create a central widget and set it as the central widget for the main window
    central_widget = QWidget(self)
    self.setCentralWidget(central_widget)

    # Create a vertical layout for the central widget
    vbox = QVBoxLayout()
    central_widget.setLayout(vbox)

    # Create a horizontal layout for the deepnes label and input field
    hbox_deepnes = QHBoxLayout()
    vbox.addLayout(hbox_deepnes)

    # Create and add deepnes label to the horizontal layout
    deepnes_label = QLabel('Deepnes of node expansion:')
    hbox_deepnes.addWidget(deepnes_label)

    # Create and add deepnes input field to the horizontal layout
    self.deepnes_input = QLineEdit()
    self.deepnes_input.setText('7')
    self.deepnes_input.setToolTip(
      'The deepnees of the expansion phase, reppresent how much time should be performed the expansion phase')
    hbox_deepnes.addWidget(self.deepnes_input)

    # Create and add deepnes label to the horizontal layout
    min_number_of_edges_label = QLabel('Min number of edges of the output subgraph:')
    hbox_deepnes.addWidget(min_number_of_edges_label)

    # Create and add deepnes input field to the horizontal layout
    self.min_number_of_edges_input = QLineEdit()
    self.min_number_of_edges_input.setText('12')
    self.min_number_of_edges_input.setToolTip(
      'The min number o edges that should have the leaf node in the simulation phase. The total number of edges in the DB neo4j is 16062')
    hbox_deepnes.addWidget(self.min_number_of_edges_input)

    # Create and add deepnes label to the horizontal layout
    number_of_brothers_label = QLabel('Brothers:')
    hbox_deepnes.addWidget(number_of_brothers_label)

    # Create and add deepnes input field to the horizontal layout
    self.number_of_brothers = QLineEdit()
    self.number_of_brothers.setText('4')
    self.number_of_brothers.setToolTip(
      'blablablablabla')
    hbox_deepnes.addWidget(self.number_of_brothers)

    # Create a horizontal layout for the index of prediction label and input field
    hbox_prediction_index = QHBoxLayout()
    vbox.addLayout(hbox_prediction_index)

    # Create and add index of prediction label to the horizontal layout
    # prediction_index_label = QLabel(
    #   'Index of prediction to explain  ')
    # hbox_prediction_index.addWidget(prediction_index_label)

    # Create and add index of prediction input field to the horizontal layout
    # self.prediction_index_input = QLineEdit()
    # self.prediction_index_input.setText('90')
    # self.prediction_index_input.setToolTip('The index of the edge to which make explainability')
    # hbox_prediction_index.addWidget(self.prediction_index_input)

    # Create and add index of prediction label to the horizontal layout
    source_target_nodes_label = QLabel('Specify source and target nodes: ')
    hbox_prediction_index.addWidget(source_target_nodes_label)

    # Create and add index of prediction input field to the horizontal layout
    self.source_index_input = QLineEdit()
    self.source_index_input.setText('1')
    hbox_prediction_index.addWidget(self.source_index_input)

    # Create and add index of prediction input field to the horizontal layout
    self.target_index_input = QLineEdit()
    self.target_index_input.setText('90')
    hbox_prediction_index.addWidget(self.target_index_input)

    # # Create and add run simulation button to the vertical layout
    # self.run_neo4j_button = QPushButton('Get data from neo4j based on edge_index')
    # vbox.addWidget(self.run_neo4j_button)
    # self.run_neo4j_button.clicked.connect(self.get_data_from_neo4j)

    # Create and add output text area to the vertical layout
    self.output_text = QTextEdit()
    vbox.addWidget(self.output_text)

    # Create and add run simulation button to the vertical layout
    self.run_simulation_button_with_s_t = QPushButton('Run montecarlo tree search with source and target nodes fast way..')
    vbox.addWidget(self.run_simulation_button_with_s_t)
    self.run_simulation_button_with_s_t.clicked.connect(self.run_simulation_with_source_and_target_nodes_fast_way)

    # Create and add run simulation button to the vertical layout
    # self.run_simulation_button = QPushButton('Run montecarlo tree search with index')
    # vbox.addWidget(self.run_simulation_button)
    # self.run_simulation_button.clicked.connect(self.run_simulation_with_index)

    # Create and add run simulation button to the vertical layout
    self.see_starter_graph_button = QPushButton('See starter subgraph')
    vbox.addWidget(self.see_starter_graph_button)
    self.see_starter_graph_button.clicked.connect(lambda: self.openWebPage('starter_graph.html'))

    # Create and add run simulation button to the vertical layout
    self.see_winner_graph_button = QPushButton('See winner subgraph')
    vbox.addWidget(self.see_winner_graph_button)
    self.see_winner_graph_button.clicked.connect(lambda: self.openWebPage('winner_graph.html'))

    # Display the window
    self.show()

  def openWebPage(self, htmlFile):
    import webbrowser
    import http.server
    import threading
    import random
    import os

    # Generate a random port number
    # Get the path of the HTML file to serve
    html_file_path = ROOT_DIR + '/charts.html'

    # Generate a random port number
    port = random.randint(1024, 65535)

    os.chdir(os.path.dirname(html_file_path))
    # Start a simple HTTP server to serve the HTML file at the random port number
    handler_class = http.server.SimpleHTTPRequestHandler
    handler_class.extensions_map['.html'] = 'text/html'
    httpd = socketserver.TCPServer(("", port), handler_class)
    threading.Thread(target=httpd.serve_forever).start()
    # Open the web page in the default browser
    webbrowser.open(('http://localhost:{}/' + htmlFile).format(port))

  def evaluate_defensive_programming(self, test_data, model):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    msgBox = QMessageBox()
    ## Valuta la differenza delle predizioni su rete neurale allenata e non allenata
    predictions = predict_with_GNN(test_data, model)
    modello_non_addestrato = ModelGAT1(hidden_channels=32, data=test_data).to(device)
    predictions_not_trained = predict_with_GNN(test_data, modello_non_addestrato)
    media_trainato = sum(predictions) / len(predictions)
    media_non_trainato = sum(predictions_not_trained) / len(predictions_not_trained)
    if abs(media_trainato - media_non_trainato) < 0.1:
      msgBox.setText("differenza media_trainato e non trainato < 0.1")
      msgBox.exec()

  def get_data_from_neo4j(self):

    self.data, self.edge_index = read_data()
    prediction_index = self.prediction_index_input.text()

    print('Tutto edge_index: ')
    print(len(self.data['user', 'rates', 'item'].edge_index[0]))
    user = self.edge_index[0][int(prediction_index)]  ## Prendo il nodo a partire dall'arco specificato
    self.output_text.append('Inizio recezione grafo con neo4j su arco identificato come: ' + str(
      self.edge_index[0][int(prediction_index)]) + str(self.edge_index[1][int(prediction_index)]))

    ## TODO mettere edge_index in modo tale da tagliarlo per l'ultimo nodo user.....
    self.edge_index, _ = neo4j_queries.get_subgraph_from_neo4j_to_explainability(user_number=str(user.item()),
                                                                                 number_of_brothers=int(
                                                                                   self.number_of_brothers.text()))
    self.output_text.append('.......' + '\n')
    self.output_text.append('edge_index dimensione iniziale: ' + str(len(self.edge_index[0])) + '\n')

  def run_simulation_with_index(self):

    with open(ROOT_DIR + "/starter_graph.txt", 'w') as f:
      f.write('')
      f.close()
    with open(ROOT_DIR + "/winner_graph.txt", 'w') as f:
      f.write('')
      f.close()

    deepnes = self.deepnes_input.text()
    min_edges = self.min_number_of_edges_input.text()
    prediction_index = self.prediction_index_input.text()

    ## Cose da preprocessing
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    self.data, self.edge_index = read_data()

    print('Tutto edge_index: ')
    print(len(self.data['user', 'rates', 'item'].edge_index[0]))
    user = self.edge_index[0][int(prediction_index)]  ## Prendo il nodo a partire dall'arco specificato
    self.output_text.append('Inizio recezione grafo con neo4j su arco identificato come: ' + str(
      self.edge_index[0][int(prediction_index)]) + str(self.edge_index[1][int(prediction_index)]))

    ## TODO mettere edge_index in modo tale da tagliarlo per l'ultimo nodo user.....
    self.edge_index, _ = neo4j_queries.get_subgraph_from_neo4j_to_explainability(user_number=str(user.item()),
                                                                                 number_of_brothers=int(
                                                                                   self.number_of_brothers.text()))
    self.output_text.append('.......' + '\n')
    self.output_text.append('edge_index dimensione iniziale: ' + str(len(self.edge_index[0])) + '\n')

    ## Alleno la rete neurale con il sotto grafo che in realtà è il grafo originale, ma con una copia se no si rompe la variabile data
    self.output_text.append('Inizio allenamento rete neurale..')
    data_clone = self.data.clone()
    final_hetero_data, final_predictions, self.model = allAlberto(data_clone)
    self.output_text.append('Fine allenamento rete neurale..')

    # self.data['user','rates','item'].edge_label_index = self.data['user','rates','item'].edge_index ## Questa riga è quella che causa IndexError: The shape of the mask [16062] at index 0 does not match the shape of the indexed tensor [2, 16062] at index 0, Tuttavia l'istruzione sotto non funzionerebbe senza questa riga
    # self.evaluate_defensive_programming(self.data, self.model)

    edge = [self.edge_index[0][int(prediction_index)], self.edge_index[1][int(prediction_index)]]

    utility.write_to_graph_format(self.edge_index, ROOT_DIR + "/starter_graph.txt")

    brothers = self.number_of_brothers.text()

    ## Poichè quando viene fatto subgraph si rompe un po tutto, l'idea è che gli viene passato il data prinicpale e edge_index e non verrà modificato mai data, ma verrà creato new_data
    monte_carlo = MonteCarlo(heterodata=self.data, edge_index=self.edge_index, deepnes_of_node_expansion=int(deepnes),
                             min_graph_number_of_edges=int(min_edges), model=self.model,
                             prediction_to_evaluate_index=int(prediction_index), edge=edge,
                             number_of_brother=int(brothers))
    win_dic, list_of_final_dic = monte_carlo.search()
    # Call the backend with the specified parameters and display the output in the text area
    self.output_text.append('deepnes_of_node_expansion: ' + deepnes + '\n')
    self.output_text.append('prediction_index: ' + prediction_index + '\n')
    self.output_text.append('........................................')
    print(win_dic)
    self.output_text.append(
      'edge_index: ' + str(win_dic['edge_index'].tolist()) + '\n' + 'win: ' + str(win_dic['win']))
    self.output_text.append('........................................')
    for dic in list_of_final_dic:
      self.output_text.append(
        'other win values: ' + str(dic['win']))

  def run_simulation_with_source_and_target_nodes_fast_way(self):

    with open(ROOT_DIR + "/starter_graph.txt", 'w') as f:
      f.write('')
      f.close()
    with open(ROOT_DIR + "/winner_graph.txt", 'w') as f:
      f.write('')
      f.close()

    deepnes = self.deepnes_input.text()
    min_edges = self.min_number_of_edges_input.text()

    ## Cose da preprocessing
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    self.data, self.edge_index = read_data()

    print('Tutto edge_index: ')
    print(len(self.data['user', 'rates', 'item'].edge_index[0]))
    self.output_text.append(
      'Inizio recezione grafo con neo4j su arco identificato come: ' + str((self.source_index_input.text())) + str(
        self.target_index_input.text()))

    self.edge_index, _ = neo4j_queries.get_subgraph_from_neo4j_to_explainability_starting_from_1_lv_subgraph(user_number=str(self.source_index_input.text()))
    self.output_text.append('.......' + '\n')
    self.output_text.append('edge_index dimensione iniziale: ' + str(len(self.edge_index[0])) + '\n')

    ## Alleno la rete neurale con il sotto grafo che in realtà è il grafo originale, ma con una copia se no si rompe la variabile data
    self.output_text.append('Inizio allenamento rete neurale..')
    data_clone = self.data.clone()
    final_hetero_data, final_predictions, self.model = allAlberto(data_clone)
    self.output_text.append('Fine allenamento rete neurale..')

    # self.data['user','rates','item'].edge_label_index = self.data['user','rates','item'].edge_index ## Questa riga è quella che causa IndexError: The shape of the mask [16062] at index 0 does not match the shape of the indexed tensor [2, 16062] at index 0, Tuttavia l'istruzione sotto non funzionerebbe senza questa riga
    # self.evaluate_defensive_programming(self.data, self.model)

    edge = [torch.tensor(int(self.source_index_input.text())), torch.tensor(int(self.target_index_input.text()))]

    utility.write_to_graph_format(self.edge_index, ROOT_DIR + "/starter_graph.txt")

    brothers = self.number_of_brothers.text()

    prediction_index = get_index_starting_from_nodes(edge_index=self.edge_index, edge=edge)

  #### Messo questo perchè il primo elemento dell'edge_index viene sempre rimosso ( per il discorso che si parte da root_node = "0" )
    edge_index_informativo =  [riga[1:] for riga in self.edge_index]

    print(self.edge_index)

    if(prediction_index == None):
      DefensiveProgramming.launch_allert(self,'Attenzione edge non presente, scegli tra i seguenti target_nodes: '+ str(edge_index_informativo[1]))
      return

    ## Poichè quando viene fatto subgraph si rompe un po tutto, l'idea è che gli viene passato il data prinicpale e edge_index e non verrà modificato mai data, ma verrà creato new_data
    monte_carlo = MonteCarlo(heterodata=self.data, edge_index=self.edge_index, deepnes_of_node_expansion=int(deepnes),
                             min_graph_number_of_edges=int(min_edges), model=self.model,
                             prediction_to_evaluate_index=int(prediction_index), edge=edge,
                             number_of_brother=int(brothers))
    win_dic, list_of_final_dic = monte_carlo.search()
    # Call the backend with the specified parameters and display the output in the text area
    self.output_text.append('deepnes_of_node_expansion: ' + deepnes + '\n')
    self.output_text.append('prediction_index: ' + str(prediction_index) + '\n')
    self.output_text.append('........................................')
    print(win_dic)
    self.output_text.append(
      'edge_index: ' + str(win_dic['edge_index'].tolist()) + '\n' + 'win: ' + str(win_dic['win']))
    self.output_text.append('........................................')
    for dic in list_of_final_dic:
      self.output_text.append(
        'other win values: ' + str(dic['win']))


if __name__ == '__main__':
  app = QApplication(sys.argv)
  window = MainWindow()
  sys.exit(app.exec())
