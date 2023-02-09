from unittest import TestCase
import torch
from business_logic.model_ml import  allAlberto, ModelGAT1, predict_with_GNN
from business_logic.utility import read_data
import torch_geometric.transforms as T


class Invariante(TestCase):

  def __init__(self, *args, **kwargs):
    super(Invariante, self).__init__(*args, **kwargs)
    self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    self.data, self.edge_index = read_data()

    self.new_edge_index = self.edge_index[:, :300]
    self.data = self.data.subgraph({
      'user': torch.tensor(self.new_edge_index[0]),
      'movie': torch.tensor(self.new_edge_index[1]),
    })

    #### Devo rispilittare anche perhcè se no non funziona per il discorso che non c'è l'attributo edge_index_label
    self.train_data, self.val_data, self.test_data = T.RandomLinkSplit(
      num_val=0.1,
      num_test=0.1,
      neg_sampling_ratio=0,
      edge_types=[('user', 'rates', 'movie')],
      rev_edge_types=[('movie', 'rev_rates', 'user')],
    )(self.data)
    ## Allena la rete neurale
    final_hetero_data, final_predictions, self.model = allAlberto(self.data)

  def test_invariante_predizione_modello_allenato_differnte_da_modello_non_allenato(self):


    print('Invariants test')

    ## Valuta la differenza delle predizioni su rete neurale allenata e non allenata
    predictions = predict_with_GNN(self.test_data, self.model)
    modello_non_addestrato = ModelGAT1(hidden_channels=32, data=self.data).to(self.device)
    predictions_not_trained = predict_with_GNN(self.test_data, modello_non_addestrato)

    media_trainato = sum(predictions) / len(predictions)
    media_non_trainato = sum(predictions_not_trained) / len(predictions_not_trained)

    assert abs(media_trainato - media_non_trainato) > 0.1  # is_all_nodes_reachable(edge_index) == True
