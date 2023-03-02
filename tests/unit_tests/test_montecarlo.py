import unittest

import torch

from montecarlo import generateallchildren, MonteCarlo


class TestBuildTree(unittest.TestCase):
  def test_generate_tree_dict(self):
    # Test 1: n = 2
    result = generate_tree_dict(2)
    print(result)

    expected = {
      '0_1': {
        'win': 0.1191,
        'visited': 1,
        '0_1_2': {
          'win': 0.1191,
          'visited': 1
        }
      },
      'win': 0.1191,
      'visited': 1
    }

    assert result == expected, f"Expected {expected}, but got {result}"

    # Test 2: n = 3
    result = generate_tree_dict(3)

    print(result)

    expected = {'0_1': {'win': 0.1191, 'visited': 1,
                        '0_1_2': {'win': 0.1191, 'visited': 1, '0_1_2_3': {'win': 0.1191, 'visited': 1}}},
                'win': 0.1191, 'visited': 1}

    assert result == expected, f"Expected {expected}, but got {result}"

    # Test 3: n = 0
    result = generate_tree_dict(0)
    print(result)
    expected = {
      'win': 0.1191,
      'visited': 1
    }
    assert result == expected, f"Expected {expected}, but got {result}"


def generate_tree_dict(n):
  tree = {}
  key = "0"
  subtree = tree
  for i in range(n):
    key += "_" + str(i + 1)
    subtree[key] = {
      "win": 0.1191,
      "visited": 1
    }
    subtree = subtree[key]
  tree["win"] = 0.1191
  tree["visited"] = 1
  return tree


class TestGenerateAllChildren(unittest.TestCase):
  def test_generateallchildren(self):
    mytensor = torch.tensor([[0, 1, 2, 3], [0, 0, 2, 1]])
    columnindex = 1
    expected_output = [torch.tensor([[1, 2, 3], [0, 2, 1]]), torch.tensor([[0, 1, 3], [0, 0, 1]]),
                       torch.tensor([[0, 1, 2], [0, 0, 2]])]
    output, _ = generateallchildren(columnindex, mytensor)
    for i in range(3):
      print(f"Output {i}: {output[i]}")
      print(f"Expected Output {i}: {expected_output[i]}")
      self.assertTrue(torch.allclose(output[i], expected_output[i]))

  def test_generateallchildren2(self):
    mytensor = torch.tensor([[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]])
    columnindex = 2
    expected_output = [torch.tensor([[1, 2, 3], [5, 6, 7], [9, 10, 11]]),
                       torch.tensor([[0, 2, 3], [4, 6, 7], [8, 10, 11]]),
                       torch.tensor([[0, 1, 2], [4, 5, 6], [8, 9, 10]]),
                       ]
    output, removed_columns = generateallchildren(columnindex, mytensor)
    for i in range(3):
      print('output')
      print(output[i])
      print('expetcted')
      if i != 2:
        self.assertTrue(removed_columns[i]==i)
      self.assertTrue(torch.allclose(output[i], expected_output[i]))



if __name__ == '__main__':
  unittest.main()
