import unittest

from main import run_every_things


class TestBuildTree(unittest.TestCase):
  def test_generate_tree_dict(self):
    run_every_things()


if __name__ == '__main__':
  unittest.main()
