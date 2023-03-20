# Utilizza un'immagine Python ufficiale come base
FROM python:3.9.9-alpine

# Crea una directory di lavoro
WORKDIR /app

# Copia il file requirements.txt nella directory di lavoro
COPY requirements.txt .




RUN apt-get update && apt-get install -y libopenblas-dev

RUN pip install numpy

# Add other necessary commands and configurations

# Aggiorna pip all'ultima versione disponibile
RUN pip install --upgrade pip


# Installa le dipendenze specificate nel file requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Installa torch manualmente
RUN pip install torch

# Installa torch-geometric manualmente
RUN pip install torch_geometric


# Copia la cartella business_logic nella directory di lavoro
COPY business_logic ./business_logic

# Espone la porta su cui l'applicazione sarà in ascolto (modificare il numero di porta in base alle proprie esigenze)
EXPOSE 8000

# Esegui l'applicazione Python (ui.py) quando il container viene avviato
CMD ["python", "business_logic/ui.py"]
