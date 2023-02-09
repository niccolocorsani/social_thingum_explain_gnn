import os
import sys
import torch
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QTextEdit, QHBoxLayout, \
  QVBoxLayout, QWidget, QMessageBox
from defensive_programming import DefensiveProgramming
from model_ml import allAlberto, predict_with_GNN, ModelGAT1
from montecarlo import MonteCarlo
from utility import read_data, removeFilesFromFolder

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
torch.set_printoptions(threshold=100000)


class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.initUI()
    ## Cose da preprocessing
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    self.data, self.edge_index = read_data()

    self.edge_index = self.edge_index[:, :80]
    data_rotto_usabile_solo_una_volta = self.data.subgraph({
      'user': torch.tensor(self.edge_index[0]),
      'movie': torch.tensor(self.edge_index[1]),
    })

    ## Alleno la rete neurale con il sotto grafo che in realtà è il grafo originale, ma con una copia se no si rompe la variabile data
    final_hetero_data, final_predictions, self.model = allAlberto(data_rotto_usabile_solo_una_volta)

    data_rotto_usabile_solo_una_volta['user', 'rates', 'movie'].edge_label_index = data_rotto_usabile_solo_una_volta[
      'user', 'rates', 'movie'].edge_index
    self.evaluate(data_rotto_usabile_solo_una_volta, self.model)
    removeFilesFromFolder(ROOT_DIR + "/all_edge_index/")

  def evaluate(self, test_data, model):
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
    deepnes_label = QLabel('Deepnes:')
    hbox_deepnes.addWidget(deepnes_label)

    # Create and add deepnes input field to the horizontal layout
    self.deepnes_input = QLineEdit()
    hbox_deepnes.addWidget(self.deepnes_input)

    # Create a horizontal layout for the index of prediction label and input field
    hbox_prediction_index = QHBoxLayout()
    vbox.addLayout(hbox_prediction_index)

    # Create and add index of prediction label to the horizontal layout
    prediction_index_label = QLabel('Index of prediction to explain:')
    hbox_prediction_index.addWidget(prediction_index_label)

    # Create and add index of prediction input field to the horizontal layout
    self.prediction_index_input = QLineEdit()
    hbox_prediction_index.addWidget(self.prediction_index_input)

    # Create and add run simulation button to the vertical layout
    self.run_simulation_button = QPushButton('Run simulation')
    vbox.addWidget(self.run_simulation_button)
    self.run_simulation_button.clicked.connect(self.run_simulation)

    # Create and add output text area to the vertical layout
    self.output_text = QTextEdit()
    vbox.addWidget(self.output_text)

    # Display the window
    self.show()

  def run_simulation(self):
    deepnes = self.deepnes_input.text()
    prediction_index = self.prediction_index_input.text()

    ## Poichè quando viene fatto subgraph si rompe un po tutto, l'idea è che gli viene passato il data prinicpale e edge_index e non verrà modificato mai data, ma verrà creato new_data
    monte_carlo = MonteCarlo(heterodata=self.data, edge_index=self.edge_index, deepnes=int(deepnes), model=self.model,
                             prediction_to_evaluate_index=int(prediction_index))
    win_dic = monte_carlo.search()
    # Call the backend with the specified parameters and display the output in the text area
    self.output_text.append('deepnes: ' + deepnes + '\n')
    self.output_text.append('prediction_index: ' + prediction_index + '\n')
    self.output_text.append('........................................')
    self.output_text.append(
      'edge_index: ' + str(win_dic['edge_index'].tolist()) + '\n' + 'win: ' + str(win_dic['win'].item()))


if __name__ == '__main__':
  app = QApplication(sys.argv)
  window = MainWindow()
  sys.exit(app.exec())
