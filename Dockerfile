# Utilizza un'immagine Python ufficiale come base
FROM python:3.9.16

# Crea una directory di lavoro
WORKDIR /app

COPY requirements.txt .


# Crea la directory /etc/cgroup/memory/docker
RUN mkdir -p /etc/cgroup/memory/docker

# Imposta la quantità di memoria massima disponibile all'interno dell'immagine Docker a 4 GB
RUN echo "memory.limit_in_bytes = 4G" > /etc/cgroup/memory/docker/memory.limit_in_bytes


RUN pip install --upgrade pip  \
    && pip install virtualenv \
      && virtualenv venv \
        && . venv/bin/activate \
          && pip install torch \
            && TORCH=$(python -c "import torch; print(torch.__version__)") \
              && echo "${TORCH}"  \
                && echo https://data.pyg.org/whl/torch-${TORCH}.html  \
                  && pip install -q torch-scatter -f https://data.pyg.org/whl/torch-${TORCH}.html  \
                   && echo 'istallazione torch-scatter-completata'  \
                     && pip install -q torch-sparse -f https://data.pyg.org/whl/torch-${TORCH}.html  \
                       && echo 'istallazione torch-sparse-completata'  \
                          && pip install -q git+https://github.com/pyg-team/pytorch_geometric.git \
                            && echo 'istallazione torch-geometric completata'  \


RUN pip install PyQt6 mysql neo4j numpy~=1.24.2 scikit-learn~=1.2.2 tqdm~=4.65.0 PyQt6~=6.4.2 mysql-connector-python==8.0.32 neo4j==5.6.0 pandas==1.5.3 protobuf==3.20.3 google-cloud-bigquery==3.7.0 mysql~=0.0.3 sentence-transformers


# Copia la cartella business_logic nella directory di lavoro
COPY business_logic ./business_logic

# Espone la porta su cui l'applicazione sarà in ascolto (modificare il numero di porta in base alle proprie esigenze)
EXPOSE 8000

# Esegui l'applicazione Python (ui.py) quando il container viene avviato
CMD ["python", "business_logic/ui.py"]
