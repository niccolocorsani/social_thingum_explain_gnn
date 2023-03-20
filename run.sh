pip install --upgrade
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
pip install torch
pip install torch_geometric
python3 business_logic/ui_manage_report.py
