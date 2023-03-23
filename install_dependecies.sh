pip install --upgrade pip
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt


pip install torch
TORCH=$(python -c "import torch; print(torch.__version__)")
echo -e "\e[31m${TORCH}\e[0m"

pip install -q torch-scatter -f https://data.pyg.org/whl/torch-${TORCH}.html
pip install -q torch-sparse -f https://data.pyg.org/whl/torch-${TORCH}.html
pip install -q git+https://github.com/pyg-team/pytorch_geometric.git

pip install PyQt6
pip install mysql
pip install neo4j
pip install sentence-transformers

python3 business_logic/ui.py
