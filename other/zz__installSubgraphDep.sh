# Install PyTorch Geometric and Open Graph Benchmark
pip install -q torch-scatter -f https://data.pyg.org/whl/torch-1.10.0+cu113.html
pip install -q torch-sparse -f https://data.pyg.org/whl/torch-1.10.0+cu113.html
pip install torch-geometric
pip install ogb

# BA-Shapes is currently only available on the Pytorch Geometric GitHub.
# It will be included in the PyPi package in the next release.
git clone https://github.com/pyg-team/pytorch_geometric.git
cp pytorch_geometric/torch_geometric/datasets/ba_shapes.py .
