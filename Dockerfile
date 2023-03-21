# Utilizza un'immagine Python ufficiale come base
FROM python:3.9.16



RUN pip install --upgrade pip

# Crea una directory di lavoro
WORKDIR /app

COPY requirements.txt .




RUN pip install torch
RUN TORCH=$(python -c "import torch; print(torch.__version__)")
RUN echo -e "\e[31m${TORCH}\e[0m"

RUN pip install -q torch-scatter -f https://data.pyg.org/whl/torch-${TORCH}.html
RUN pip install -q torch-sparse -f https://data.pyg.org/whl/torch-${TORCH}.html
RUN pip install -q git+https://github.com/pyg-team/pytorch_geometric.git

RUN pip install PyQt6
RUN pip install mysql
RUN pip install neo4j


RUN pip install numpy~=1.24.2
RUN pip install scikit-learn~=1.2.2
RUN pip install tqdm~=4.65.0
RUN pip install PyQt6~=6.4.2
RUN pip install mysql-connector-python==8.0.32
RUN pip install neo4j==5.6.0
RUN pip install pandas==1.5.3
RUN pip install protobuf==3.20.3
RUN pip install google-cloud-bigquery==3.7.0
RUN pip install mysql~=0.0.3
RUN pip install sentence-transformers






# Copia la cartella business_logic nella directory di lavoro
COPY business_logic ./business_logic

# Espone la porta su cui l'applicazione sarà in ascolto (modificare il numero di porta in base alle proprie esigenze)
EXPOSE 8000

# Esegui l'applicazione Python (ui.py) quando il container viene avviato
CMD ["python", "business_logic/ui.py"]
