import unittest

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


if __name__ == '__main__':
  unittest.main()
