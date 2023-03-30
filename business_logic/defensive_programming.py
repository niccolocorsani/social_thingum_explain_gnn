import sys
import torch
from PyQt6.QtWidgets import QMessageBox, QApplication
from model_ml import predict_with_GNN, ModelGAT1


class DefensiveProgramming(QMessageBox):
  def __init__(self):
    self.app = QApplication(sys.argv)
    super(QMessageBox, self).__init__()

  ## Questa funzione valura se effettivamente è stato trainato correttamente il modello, altrimenti da errore
  def evaluate(self, test_data, model):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    msgBox = QMessageBox()
    ## Valuta la differenza delle predizioni su rete neurale allenata e non allenata
    predictions = predict_with_GNN(test_data, model)
    modello_non_addestrato = ModelGAT1(hidden_channels=32, data=test_data).to(device)
    predictions_not_trained = predict_with_GNN(test_data, modello_non_addestrato)
    media_trainato = sum(predictions) / len(predictions)
    media_non_trainato = sum(predictions_not_trained) / len(predictions_not_trained)
    print((media_trainato - media_non_trainato))
    if abs(media_trainato - media_non_trainato) < 0.001:
      msgBox.setText("differenza media_trainato e non trainato < 0.1")
      msgBox.exec()
  @staticmethod
  def launch_allert(self, text_alert):
    app = QApplication(sys.argv)
    msgBox = QMessageBox()
    msgBox.setText(text_alert)
    msgBox.exec()
    app.exec()


