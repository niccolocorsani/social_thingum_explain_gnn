# Utilizza un'immagine Python ufficiale come base
FROM python:3.9.16

# Installa libGL
RUN apt-get update && apt-get install -y libgl1-mesa-glx

RUN apt-get update && apt-get install -y libxkbcommon0

# Crea una directory di lavoro
WORKDIR /app

COPY requirements.txt .

# Crea la directory /etc/cgroup/memory/docker
RUN mkdir -p /etc/cgroup/memory/docker

# Imposta la quantità di memoria massima disponibile all'interno dell'immagine Docker a 4 GB
RUN echo "memory.limit_in_bytes = 4G" > /etc/cgroup/memory/docker/memory.limit_in_bytes


RUN pip install --upgrade pip  \
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


RUN pip install requests   ## Il primo pip install non lo prende, per questo ne ho messo uno leggero

RUN pip install sentence-transformers

RUN pip install  --no-cache-dir pandas==1.5.3 ## Il fatto che era la prima istallazione gli dava noia




RUN pip install neo4j==5.6.0


RUN pip install scikit-learn~=1.2.2

RUN pip install numpy~=1.24.2

RUN pip install neo4j

#RUN pip install mysql

RUN pip install Flask


COPY ./business_logic/model_ml.py ./business_logic/model_ml.py
COPY ./business_logic/montecarlo.py ./business_logic/montecarlo.py
COPY ./business_logic/neo4j_queries.py ./business_logic/neo4j_queries.py
COPY ./business_logic/utility.py ./business_logic/utility.py
COPY ./business_logic/controller.py ./business_logic/controller.py
COPY ./business_logic/alberto.py ./business_logic/alberto.py


RUN sleep 10

# Espone la porta su cui l'applicazione sarà in ascolto (modificare il numero di porta in base alle proprie esigenze)
EXPOSE 8080

# Esegui l'applicazione Python (ui.py) quando il container viene avviato
CMD ["python", "business_logic/controller.py"]
