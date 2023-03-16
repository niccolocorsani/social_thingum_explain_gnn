import os
import random
from datetime import datetime
from math import sqrt, log
import defensive_programming
import utility
from annotations.log_annontation_from_class import LogMethodCalls
from model_ml import predict_with_GNN
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

## Da rimuovere in produzione
def verifica_colonna(tensore, colonna):
  colonna = torch.stack(colonna).reshape(-1, 1)
  if colonna.shape[1] != 1:
    raise ValueError("La colonna deve essere un tensore di dimensione 2 con una sola colonna.")
  for j in range(tensore.shape[1]):
    if torch.equal(tensore[:, j, None], colonna):
      return True
  return False


def generateallchildren(columnindex, edge_index):
  output = []
  removed_columns = []
  for i in range(edge_index.shape[1]):
    if i != columnindex:
      newtensor = torch.tensor(edge_index[:, [j for j in range(edge_index.shape[1]) if j != i]])
      output.append(newtensor)
      removed_columns.append(i)
  return output, removed_columns


def remove_random_column(tensor, index_to_not_remove):
  num_columns = tensor.shape[1]
  random_index = random.randint(0, num_columns - 1)
  while random_index == index_to_not_remove:
    random_index = random.randint(0, num_columns - 1)
  if random_index < index_to_not_remove:
    index_to_not_remove = index_to_not_remove - 1
  return torch.cat((tensor[:, :random_index], tensor[:, random_index + 1:]), dim=1), random_index, index_to_not_remove


def back_propagate_through_all_path(dictionary, win, visited):
  for key in dictionary:
    if type(dictionary[key]) == dict:
      back_propagate_through_all_path(dictionary[key], win, visited)
    else:
      if key == "win":
        dictionary[key] += win
      if key == "visited":
        dictionary[key] += visited

  return dictionary


def get_index_starting_from_nodes(edge_index, edge):
  for i in range(edge_index.shape[1]):
    if edge_index[:, i][0] == edge[0].item() and edge_index[:, i][1] == edge[1].item():
      return i
  return None


import torch


def find_sub_edge_positions(edge_index, sub_edge_index):

  positions = []

  edge_index_t = edge_index.t()
  sub_edge_index_t = sub_edge_index.t()

  for i in range(sub_edge_index.shape[1]):
    for j in range(edge_index.shape[1]):
      if (sub_edge_index_t[i] == edge_index_t[j]).all():
        positions.append(j)

  return positions



#@LogMethodCalls
class MonteCarlo:
  def __init__(self, heterodata, edge_index, model, prediction_to_evaluate_index, edge, number_of_brother, deepnes_of_node_expansion=8,
               min_graph_number_of_edges=5):

    self.prediction_to_evaluate_index = prediction_to_evaluate_index
    self.model = model
    self.data = heterodata
    self.edge_index = edge_index
    self.deepnes_of_node_expansion = deepnes_of_node_expansion
    self.tree = {}  ## uso dizionario che è più veloce della lista
    self.list_of_final_leaf_graph = []
    self.min_graph_number_of_edges = min_graph_number_of_edges
    self.edge = edge
    self.number_of_brother = number_of_brother

    positions = find_sub_edge_positions(self.data['user', 'rates', 'item'].edge_index, self.edge_index)

    self.data = self.data.edge_subgraph({
      'rates': torch.tensor(positions),
      'rev_rates': torch.tensor(positions),
    })

    self.value_of_prediction = self.data['user', 'rates', 'item'].edge_label[
      self.prediction_to_evaluate_index]  ##  poi da rimuovere in produzione, solo per debuggare

  def remove_random_nodes_payng_attention_to_not_remove_nodes_of_edge(self, edge_index, edge):
    num_columns = edge_index.shape[1]
    random_index = random.randint(0, num_columns - 1)
    while edge_index[0][random_index].item() == edge[0].item() and edge_index[1][random_index].item() == edge[1].item():
      random_index = random.randint(0, num_columns - 1)
    return torch.cat((edge_index[:, :random_index], edge_index[:, random_index + 1:]), dim=1), random_index

  def select_child(self, tree_dic, father_id):
    map = {}
    for children_id in tree_dic[father_id]['childrens_id']:
      ## Se c'è almeno un valore con visited == 0 scelgo lui
      if any(value['visited'] == 0 for value in tree_dic.values()):
        children_id = next(key for key, value in tree_dic.items() if value['visited'] == 0)
        return children_id
      else:
        map[children_id] = tree_dic[children_id]['win'] / tree_dic[children_id]['visited'] + sqrt(
          2 * log(tree_dic[father_id]['visited']) / tree_dic[children_id]['visited'])
    best_child_id = max(map.items(), key=lambda item: item[1])[0]
    return best_child_id

  def simulation_montecarlo(self, node_id, edge_index):


    parent_node_id = node_id
    data = self.data.clone()  ## A ogni nuova simulazione di montecarlo si riparte con il grafo originale
    list_of_index = list(range(len(edge_index[0])))


####TODO da mettere controlli a destra e sinistra
##TODO qui va tagliato l'edge_index levandogli i nodi che compaiono nella stringa node_id

    list_of_edges_to_remove = node_id.split('_')
    list_of_edges_to_remove = list(map(int, list_of_edges_to_remove))
    list_of_edges_to_keep = [x for x in list_of_index if x not in list_of_edges_to_remove]
    edge_index = edge_index[:, list_of_edges_to_keep]

####################################################################

    while edge_index.shape[1] > self.min_graph_number_of_edges:

      len_edge_prima = len(edge_index[0])  # da rimuovere in produzione
      edge_index, index = self.remove_random_nodes_payng_attention_to_not_remove_nodes_of_edge(edge_index, self.edge)
      try:
        list_of_index.pop(index)
      except:
        print('non in lista: ' + str(index))
        print(list_of_index)

## Da rimuovere in produzione
      # if len(list_of_index) != len(edge_index[0]):
      #   defensive_programming.DefensiveProgramming.launch_allert(self,
      #                                                            'Dimensione edge_index e list_of_index differente')
## Da rimuovere in produzione
## Da rimuovere in produzione
      # if verifica_colonna(edge_index, self.edge) == False:
      #   defensive_programming.DefensiveProgramming.launch_allert(self,
      #                                                            'self.edge_index non contiene più l arco su cui faccio explainability')
## Da rimuovere in produzione
## Da rimuovere in produzione
      # if len(edge_index[0]) == len_edge_prima:
      #   defensive_programming.DefensiveProgramming.launch_allert(self,
      #                                                            'Attenzione nessun arco rimosso')
## da rimuovere in produzione
# ## Da rimuovere in produzione
#       try:
#         dim_grafo_prima = len(new_data['user', 'rates', 'item'].edge_index[0])
#       except Exception as e:
#         pass
## Da rimuovere in produzione
      # child_id = node_id + '_' + str(index)
      # node_id = child_id
## Da rimuovere in produzione
      # try:
      #   debug_data = new_data.clone()
      # except:
      #   pass
## Da rimuovere in produzione

## Questo si può spostare più in giù, non deve essere eseguito tutte le volte
      new_data = data.edge_subgraph({
        'rates': torch.tensor(list_of_index),
        'rev_rates': torch.tensor(list_of_index),
      })
      dim_grafo_dopo = len(new_data['user', 'rates', 'item'].edge_index[0])  ## Da rimuovere in produzione

      new_data['user', 'rates', 'item'].edge_label_index = new_data[
        'user', 'rates', 'item'].edge_index

## Da rimuovere in produzione
      # try:
      #   subtract = debug_data['user', 'rates', 'item'].edge_index - new_data['user', 'rates', 'item'].edge_index
      #   print('rimosso: ' + subtract)
      # except:
      #   pass
# ## Da rimuovere in produzione
#       if verifica_colonna(new_data[
#                             'user', 'rates', 'item'].edge_index, self.edge) == False:
#         defensive_programming.DefensiveProgramming.launch_allert(self,
#                                                                  'self.edge_index non contiene più l arco su cui faccio explainability')
## Da rimuovere in produzione
## Da rimuovere in produzione
      # if verifica_colonna(new_data[
      #                       'user', 'rates', 'item'].edge_index, self.edge) == False:
      #   defensive_programming.DefensiveProgramming.launch_allert(self,
      #                                                            'self.edge_index non contiene più l arco su cui faccio explainability')
      ##TODO Mettere controllo del tipo: new_data['user', 'rates', 'item'].edge_index deve contenere tutti gli torch.unique(edge_index[0]) nodi
## Da rimuovere in produzione
      # try:
      #   if dim_grafo_dopo > dim_grafo_prima:
      #     defensive_programming.DefensiveProgramming.launch_allert(self,
      #                                                              'Attenzione, dimensione grafo dopo > dimensione grafo prima')
      # except Exception as e:
      #   pass
# ## Da rimuovere in produzione
    try:
      predictions = predict_with_GNN(new_data, self.model)
    except:
      defensive_programming.DefensiveProgramming.launch_allert(self,
                                                               'The dimension of the leaf graph is higher than the dimension of the root graph. Try to increase the number of brothers')
    index_of_prediction_to_evaluate = get_index_starting_from_nodes(edge_index, self.edge)
## Da rimuovere in produzione
    # if new_data['user', 'rates', 'item'].edge_label[index_of_prediction_to_evaluate] != self.value_of_prediction:
    #   defensive_programming.DefensiveProgramming.launch_allert(self,'Edge to evaluate valore errato')
## Da rimuovere in produzione
## Da rimuovere in produzione
    # if new_data['user', 'rates', 'item'].edge_label[index_of_prediction_to_evaluate] != \
    #   data['user', 'rates', 'item'].edge_label[self.prediction_to_evaluate_index]:
    #   defensive_programming.DefensiveProgramming.launch_allert(self,
    #                                                            'Edge to evaluate valore errato')
## Da rimuovere in produzione

    diff = abs(predictions[index_of_prediction_to_evaluate] - \
               data['user', 'rates', 'item'].edge_label[self.prediction_to_evaluate_index])

    ## Da rimuovere in produzione
    # if new_data['user', 'rates', 'item'].edge_index[0][index_of_prediction_to_evaluate] != \
    #   data['user', 'rates', 'item'].edge_index[0][self.prediction_to_evaluate_index] or new_data['user', 'rates', 'item'].edge_index[1][index_of_prediction_to_evaluate] != \
    #   data['user', 'rates', 'item'].edge_index[1][self.prediction_to_evaluate_index]:
    #   defensive_programming.DefensiveProgramming.launch_allert(self,'Edge_index to evaluate valore errato')
    ## Da rimuovere in produzione



    win = 0
    ## Random value serve per i test che essendo poco allenato se no da sempre gli stessi valori
    random_value = random.uniform(0.0000001, 0.000099)
    #### Se la differenza è tanta gli attribuisco un valore basso, se poca gli attribuisco un valore positivo
    if 0.2 >= diff > 0.1:
      win = (0 + random_value)
    if 0.1 >= diff > 0.05:
      win = (0.5 + random_value)
    if 0.05 >= diff > 0.01:
      win = (1 + random_value)
    if 0.01 >= diff >= 0.005:
      win = (2 + random_value)
    if 0.0025 >= diff >= 0.001:
      win = (4 + random_value)
    if diff < 0.001:
      win = (8 + random_value)


    self.list_of_final_leaf_graph.append({'edge_index': edge_index, 'win': win, 'diff':diff})
    self.tree = self.back_propagate(self.tree, parent_node_id, win)

    return

  def back_propagate(self, tree, node_id, win):

    path = node_id.split('_')
    node_id_of_the_path = '0'

    for i, element in enumerate(path):

      if i == 0:
        node_id_of_the_path = '0'
        tree[node_id_of_the_path]['visited'] = tree[node_id_of_the_path]['visited'] + 1
        tree[node_id_of_the_path]['win'] = tree[node_id_of_the_path]['win'] + win
      else:
        node_id_of_the_path = node_id_of_the_path + '_' + element
        tree[node_id_of_the_path]['visited'] = tree[node_id_of_the_path]['visited'] + 1
        tree[node_id_of_the_path]['win'] = tree[node_id_of_the_path]['win'] + win

    return tree

  def node_expansion(self, current_root_node_id):
    _, ids_of_children_of_root_nodes = generateallchildren(self.prediction_to_evaluate_index, self.edge_index)

    ## Da rimuovere in produzione
    # if self.data['user', 'rates', 'item'].edge_label[self.prediction_to_evaluate_index] != self.value_of_prediction:
    #   defensive_programming.DefensiveProgramming.launch_allert(self,
    #                                                            'Edge to evaluate valore errato in node expansion')
    ## Da rimuovere in produzione

    ids_of_children_format_with_under_score = []
    #### Aggiungo tutti i figli di root, tranne quello dove verrebbe rimosso il ramo relativo alla predizione che voglio fare
    for id_of_children in ids_of_children_of_root_nodes:
      id = current_root_node_id + '_' + str(id_of_children)
      ids_of_children_format_with_under_score.append(id)
      self.tree[id] = {'win': 0, 'visited': 0, 'childrens_id': []}
    self.tree[current_root_node_id] = {'win': 0, 'visited': 0, 'childrens_id': ids_of_children_format_with_under_score}

  def search(self):
    self.list_of_final_leaf_graph = []
    iterations = 0
    root_node_id = str(0)

    while len(root_node_id.split('_')) < self.deepnes_of_node_expansion:
      self.node_expansion(current_root_node_id=root_node_id)
      for i in range(len(self.edge_index[1])):
        best_child_id = self.select_child(self.tree, root_node_id)
        self.simulation_montecarlo(node_id=best_child_id,
                                   edge_index=self.edge_index)
        iterations = iterations + 1
        print(iterations)

        if iterations % 100 == 0:
          print(iterations)
      ## Cambio il root node e inizio la prima fase di Expansion
      root_node_id = self.select_child(self.tree, root_node_id)
    win_dic = max(self.list_of_final_leaf_graph,
                  key=lambda x: x['win'])
    utility.write_to_graph_format(win_dic['edge_index'],
                                  ROOT_DIR + '/winner_graph' + '.txt')



    ## Metti in una stringa la data di oggi in formato (YYYY-MM-DD)
    today = datetime.today().strftime('%Y-%m-%d')


    print(today)


#### TODO levare il diff dalla scrittura e dal progetto in generale
#### TODO è normale che diff sia incoerente con win, win_dic fa riferimento al miglior dizionario, diff fa riferimento all'ultimo valore ritornato win_dic a diff
    with open(ROOT_DIR + '/logs/'+str(today)+'.txt', mode='a') as f:
      f.write('current_time: '+str(datetime.now())+';edge_index: ' + str(win_dic['edge_index']).replace("\n", "") + ';index_prediction_to_evaluate: ' + str(
        self.prediction_to_evaluate_index).replace("\n",
                                                   "") + ';nodes_corresponding_to_index_prediction_to_evaluate: ' + str(
        self.edge[0].item()).replace("\n", "") + ',' + str(self.edge[1].item()).replace("\n",
                                                                                        "") + ';min_number_of_edges: ' + str(
        self.min_graph_number_of_edges).replace("\n", "") + ';deepnes_of_node_expansion: ' + str(
        self.deepnes_of_node_expansion).replace("\n", "") + ';win: ' + str(win_dic['win']).replace("\n", "") +';difference_in_prediction: '+str(win_dic['diff'])+';number_of_brother: '+str(self.number_of_brother) +'\n')

    ## Controllo così da levare in produzione
    if win_dic['edge_index'].shape != (2, self.min_graph_number_of_edges):
      defensive_programming.DefensiveProgramming.launch_allert(self, text_alert='Dimensione edge index non corretta')
    ## Controllo così da levare in produzione

    return win_dic, self.list_of_final_leaf_graph


if __name__ == '__main__':
  pass
