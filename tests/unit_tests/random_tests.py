import unittest
from torch_geometric.utils import k_hop_subgraph
import torch
from montecarlo import verifica_colonna, get_index_starting_from_nodes, find_sub_edge_positions
from neo4j_queries import remove_duplicate_columns
from torch_geometric.data import HeteroData


def invert_rows(tensor):
  return tensor.flip(dims=[0])


class TestBuildTree(unittest.TestCase):
  def test_generate_tree_dict(self):
    # Define an edge_index tensor
    edge_index = torch.tensor([[10, 1, 13, 14, 15, 16],
                               [1, 0, 2, 1, 3, 1]])

    # Create a networkx graph object

    # Define the node index and the number of hops
    node_idx = 1
    k = 1

    # Extract the k-hop subgraph around the node
    subgraph = k_hop_subgraph(node_idx, k, edge_index)

    # Print the resulting subgraph
    print(subgraph)

  def test_inverti_righe(self):
    edge_index = torch.tensor([[10, 1, 13, 14, 15, 16], [1, 0, 2, 1, 3, 1]])
    inverted_edge_index = invert_rows(edge_index)

    print(inverted_edge_index)
    inverted_edge_index = invert_rows(inverted_edge_index)

    print(inverted_edge_index)
    self.assertTrue(torch.allclose(inverted_edge_index, edge_index))


class TestRemoveDuplicateColumns(unittest.TestCase):

  def test_all_columns_are_duplicates(self):
    tensor_indices = torch.tensor([[1, 3, 3, 3], [3, 3, 3, 3]])
    tensor_label = torch.tensor([0.3, 0.5, 0.2, 0.7])
    expected_unique_tensor = torch.tensor([[1, 3]])
    expected_new_tensor_label = [0.3, 0.5]
    unique_tensor, new_tensor_label = remove_duplicate_columns(tensor_indices, tensor_label)
    self.assertEqual(expected_unique_tensor.shape[1], len(new_tensor_label))

  def test_multiple_columns_are_duplicates(self):
    tensor_indices = torch.tensor([[1, 3, 2, 3], [3, 3, 3, 0]])
    tensor_label = torch.tensor([0.3, 0.5, 0.2, 0.7])
    expected_unique_tensor = torch.tensor([[1, 3, 2, 3], [3, 3, 3, 0]])
    unique_tensor, new_tensor_label = remove_duplicate_columns(tensor_indices, tensor_label)
    self.assertEqual(expected_unique_tensor.shape[1], len(new_tensor_label))

  def test_multiple_columns_are_duplicates(self):
    tensor_indices = torch.tensor([[1, 3, 2, 3, 3, 3], [3, 3, 3, 0, 3, 3]])
    tensor_label = torch.tensor([0.3, 0.5, 0.2, 0.7, 0.2, 0.2])
    expected_unique_tensor = torch.tensor([[1, 3, 2, 3], [3, 3, 3, 0]])
    unique_tensor, new_tensor_label = remove_duplicate_columns(tensor_indices, tensor_label)
    self.assertEqual(expected_unique_tensor.shape[1], len(new_tensor_label))


class TestVerificaColonna(unittest.TestCase):
  def test_colonna_presente(self):
    tensore = torch.tensor([[0, 1, 2], [0, 0, 0]])
    colonna = [torch.tensor(1), torch.tensor(0)]
    self.assertTrue(verifica_colonna(tensore, colonna))

  def test_colonna_presente1(self):
    tensore = torch.tensor([[0, 1, 2], [0, 0, 0]])
    colonna = [torch.tensor(0), torch.tensor(0)]
    self.assertTrue(verifica_colonna(tensore, colonna))

  def test_colonna_presente2(self):
    tensore = torch.tensor([[0, 1, 2], [0, 0, 0]])
    colonna = [torch.tensor(2), torch.tensor(0)]
    self.assertTrue(verifica_colonna(tensore, colonna))

  def test_colonna_non_presente(self):
    tensore = torch.tensor([[0, 1, 2], [0, 0, 0]])
    colonna = [torch.tensor(1), torch.tensor(7)]
    self.assertFalse(verifica_colonna(tensore, colonna))

  def test_colonna_non_presente2(self):
    tensore = torch.tensor([[0, 1, 2], [0, 0, 0]])
    colonna = [torch.tensor(1), torch.tensor(8)]
    self.assertFalse(verifica_colonna(tensore, colonna))

  def test_colonna_non_presente3(self):
    tensore = torch.tensor([[0, 1, 2], [0, 0, 0]])
    colonna = [torch.tensor(24), torch.tensor(7)]
    self.assertFalse(verifica_colonna(tensore, colonna))

  class TestTrovaIndice(unittest.TestCase):

    def test_trova_indice(self):
      # test con variabile2 presente in variabile1
      variabile1 = torch.tensor([[1, 2, 5, 6, 98], [0, 6, 1, 2, 140]])
      variabile2 = [torch.tensor(98), torch.tensor(140)]
      self.assertEqual(get_index_starting_from_nodes(variabile1, variabile2), 4)

      # test con variabile2 non presente in variabile1
      variabile1 = torch.tensor([[1, 2, 5, 6, 98], [0, 6, 1, 2, 140]])
      variabile2 = [torch.tensor(3), torch.tensor(4)]
      self.assertIsNone(get_index_starting_from_nodes(variabile1, variabile2))

    def test_trova_indice_con_tensores(self):
      # Dati di input e output attesi
      variabile1 = torch.tensor([[1, 2, 5, 6, 98], [0, 6, 1, 2, 140]])
      variabile2 = torch.tensor([98, 140])
      expected_output = 4

      # Esecuzione della funzione e confronto con l'output atteso
      output = get_index_starting_from_nodes(variabile1, variabile2)
      self.assertEqual(output, expected_output)

      # Dati di input e output attesi
      variabile1 = torch.tensor([[1, 2, 5, 6, 98], [0, 6, 1, 2, 140]])
      variabile2 = torch.tensor([5, 1])
      expected_output = 2

      # Esecuzione della funzione e confronto con l'output atteso
      output = get_index_starting_from_nodes(variabile1, variabile2)
      self.assertEqual(output, expected_output)

      # Dati di input e output attesi
      variabile1 = torch.tensor([[1, 2, 5, 6, 98], [0, 6, 1, 2, 140]])
      variabile2 = torch.tensor([6, 2])
      expected_output = 3

      # Esecuzione della funzione e confronto con l'output atteso
      output = get_index_starting_from_nodes(variabile1, variabile2)
      self.assertEqual(output, expected_output)

    def test_trova_indice_con_tensores(self):
      # Dati di input e output attesi
      variabile1 = torch.tensor([[1, 2, 5, 6, 98], [0, 6, 1, 2, 140]])
      variabile2 = torch.tensor([98, 140])
      expected_output = 4

      # Esecuzione della funzione e confronto con l'output atteso
      output = get_index_starting_from_nodes(variabile1, variabile2)
      self.assertEqual(output, expected_output)

      # Dati di input e output attesi
      variabile1 = torch.tensor([[10, 20, 50, 60, 980], [0, 60, 10, 20, 1400]])
      variabile2 = torch.tensor([50, 10])
      expected_output = 2

      # Esecuzione della funzione e confronto con l'output atteso
      output = get_index_starting_from_nodes(variabile1, variabile2)
      self.assertEqual(output, expected_output)

      # Dati di input e output attesi
      variabile1 = torch.tensor([[1, 2, 5, 6, 98], [0, 6, 1, 2, 140]])
      variabile2 = torch.tensor([3, 4])
      expected_output = None

      # Esecuzione della funzione e confronto con l'output atteso
      output = get_index_starting_from_nodes(variabile1, variabile2)
      self.assertEqual(output, expected_output)


class Subgraph_edge_Test(unittest.TestCase):
  def test_generate_tree_dict(self):
    pass


import torch
import unittest


class TestFindSubEdgePositions(unittest.TestCase):

  def test_simple_case(self):
    edge_index = torch.tensor([[0, 1, 2, 3], [1, 2, 0, 3]])
    sub_edge_index = torch.tensor([[0, 2], [1, 0]])
    positions = find_sub_edge_positions(edge_index, sub_edge_index)
    self.assertEqual(positions, [0, 2])

  def test_duplicate_edges(self):
    edge_index = torch.tensor([[0, 1, 2, 3], [1, 2, 2, 3]])
    sub_edge_index = torch.tensor([[2, 0], [2, 1]])
    positions = find_sub_edge_positions(edge_index, sub_edge_index)
    self.assertEqual(positions, [2, 0])

  def test_missing_edge(self):
    edge_index = torch.tensor([[0, 1, 2, 3], [1, 2, 0, 3]])
    sub_edge_index = torch.tensor([[0, 2, 3], [1, 3, 3]])
    positions = find_sub_edge_positions(edge_index, sub_edge_index)
    self.assertEqual(positions, [0, 3])

  def test_empty_sub_edge_index(self):
    edge_index = torch.tensor([[0, 1, 2, 3], [1, 2, 0, 3]])
    sub_edge_index = torch.tensor([], dtype=torch.long)
    positions = find_sub_edge_positions(edge_index, sub_edge_index)
    self.assertEqual(positions, [])

  def test_empty_edge_index(self):
    edge_index = torch.tensor([], dtype=torch.long)
    sub_edge_index = torch.tensor([[0, 2], [1, 0]], dtype=torch.long)
    positions = find_sub_edge_positions(edge_index, sub_edge_index)
    self.assertEqual(positions, None)


if __name__ == '__main__':
  unittest.main()
