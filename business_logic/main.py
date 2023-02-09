import os
from defensive_programming import DefensiveProgramming
from model_ml import allAlberto
from montecarlo import MonteCarlo
from utility import read_data, removeFilesFromFolder
import torch
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
torch.set_printoptions(threshold=100000)


def run_every_things():

  ## Cose da preprocessing
  defensive_programming = DefensiveProgramming()
  device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
  data, edge_index = read_data()

  ## Riduco dimensione grafo
  print(edge_index.shape)


  edge_index = edge_index[:, :80]
  data_rotto_usabile_solo_una_volta = data.subgraph({
    'user': torch.tensor(edge_index[0]),
    'movie': torch.tensor(edge_index[1]),
  })

  ## Alleno la rete neurale con il sotto grafo che in realtà è il grafo originale, ma con una copia se no si rompe la variabile data
  final_hetero_data, final_predictions, model = allAlberto(data_rotto_usabile_solo_una_volta)


  data_rotto_usabile_solo_una_volta['user', 'rates', 'movie'].edge_label_index = data_rotto_usabile_solo_una_volta['user', 'rates', 'movie'].edge_index
  defensive_programming.evaluate(data_rotto_usabile_solo_una_volta, model)
  removeFilesFromFolder(ROOT_DIR+"/all_edge_index/")

  ## Poichè quando viene fatto subgraph si rompe un po tutto, l'idea è che gli viene passato il data prinicpale e edge_index e non verrà modificato mai data, ma verrà creato new_data
  monte_carlo = MonteCarlo(heterodata=data, edge_index=edge_index, deepnes=10,model=model,prediction_to_evaluate_index=4)
  monte_carlo.search()

  print('fine')





if __name__ == '__main__':
  run_every_things()
