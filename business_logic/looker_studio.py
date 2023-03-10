import looker_sdk
from google.oauth2 import service_account


def fai():
  # Configurazione delle credenziali per l'API di Looker
  sdk = looker_sdk.init31()  # Inserire il nome dell'istanza Looker
  creds = service_account.Credentials.from_service_account_file(
    'path/to/credentials.json',  # Inserire il percorso delle credenziali Google
    scopes=['https://www.googleapis.com/auth/cloud-platform']
  )

  # Query di aggiornamento dei dati in BigQuery
  query = "UPDATE my_table SET column1 = 'new_value' WHERE column2 = 'criteria'"

  # Esecuzione della query in BigQuery
  from google.cloud import bigquery
  client = bigquery.Client(credentials=creds)
  query_job = client.query(query)

  # Aggiornamento del modello Looker utilizzando l'API di Looker
  result = sdk.run_inline_query(
    'my_model',  # Inserire il nome del modello Looker
    result_format='json_detail',
    body={
      'model': 'my_model',
      'view': 'my_view',
      'fields': ['column1', 'column2'],
      'filters': {
        'column2': 'criteria'
      },
      'query': query
    }
  )

  # Stampa dei risultati dell'aggiornamento
  print(result)

if __name__ == '__main__':

  fai()
