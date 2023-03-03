import mysql.connector
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

if __name__ == '__main__':

  # Configurazione delle credenziali per accedere a MySQL
  mysql_config = {
    'user': 'myuser',
    'password': 'mypassword',
    'host': 'localhost',
    'database': 'mydatabase'
  }

  # Connessione a MySQL
  cnx = mysql.connector.connect(**mysql_config)

  # Ottieni l'elenco delle tabelle da MySQL
  cursor = cnx.cursor()
  cursor.execute("SHOW TABLES")
  tables = [table[0] for table in cursor]

  ##### bigQueryAuth

  # Configurazione delle informazioni per accedere a BigQuery
  project_id = 'your-project-id'
  credentials_info = {
  "type": "service_account",
  "project_id": "virtual-plexus-379510",
  "private_key_id": "86577b28e1daf3eeb87c6481f35910ad9d386d70",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC/Z/zRS835cZ9U\nafGjH1EA4kbKp61/Il+zpDGtlqCc4Qn+ocCGxd/hxhb9PvDOlUqgMpVs4kiT7RK2\n1zWSPKYYqt4uE31oe3RkgkHajiQSSerbe2nmxPtBIZspd34I4JzExVpEzaX4NQx4\nBV328tJ+Ov/lnGmi1EvmK0CWCf6de3BNL+sp4mRnSidOjHMOfOf9Hqxlvn/b2UHs\nPGn+GWdEw2YTAO2x/ZlT85SqXjP+6lrM7pMbybgki0xYJ1Y7vnqgFGcwG/4MLB3M\nouBcWbpEHkl1pv/1HLtYcRIp+sNOoz0cuc2//N/XqtEeFO9CcMvOek8g44mFzyiz\nVasjnOptAgMBAAECggEAKnpJKuisEDL1VV5CrD0ftLbC16gxMoD+JKeoh7nhMJen\nqG0cxTwmNJyJzw94ERykKFu5eiXYzg1jpRSrNKZFhT1sW+Ti5LxbJxAaTcbUPgPN\n/YIMzVRDX1+2J9R3McCpQej7YMAT2HrrZrpoMU0PxkhRMJOPBP4gzvaj2Xhj225d\n7v3aeygbJmj8yswgXi8MJHnk6B7Eeh0nJT8l6K0TTryCzV317zJfkAQxpBUCB7aw\nttTrnw85CXeUcag5kdB23TFY2jedUHQBqFrU6jsrZ/qtg20fise8tTPda4yZRaWI\nyn7iA84pwPPU7C1cQIkcEEgvGrlZV7rpjdpJqdk1wQKBgQD3iH/Eh5gTN0HxbyAL\nAUp0VfHB6RkxN70GCN/E7thvQxOUE1HshHoSJpnSoBp+qEWD60GYAud0LQrpOCwt\nALMT6AX4AQLqPG0ywP7LtjDX4RpJ4mG2qxMlat+okHmWkan1OpbcwklzH3CmUawB\nOBE2Cm4a857yOeqcj0d9jxrKLQKBgQDF9ASLxZEFbR/S2cm8Or4J7fEED8KSgo0C\nvgvJC2G5skNvKzG2TYVhY4X813otsX1tNNcY+d0wr3qLiuFtmlIUxurHAVx0iOPN\n8INML1kvSPElth5/ZLUhMjnCbUj1dxzRuWdWB2RJmSndtDURgmDOe+h70P48nwP7\np5SmBAQJQQKBgHkvXYYE8EHwGput0N0ya5YbAXnyub+rzyHmNE9As7t89lfXQZNu\npCjAtywz7+S0Uxwrj/hw64moB6B4PMBniESlok5xiFDO9pMTg2qOLslxziH/7+Cz\nTnNSKF9pI+3AMJn7biJ0B+uRp9/1OiV6oop3fsI5JUbnbeHqD5D7/5ydAoGAcYWP\nVdjnYgVCyti7KIdHlMov/fRL0VmtJHV4rMMqOCRTJ93NlI7AfylkHaw1FR9Enuw+\nrsQcZV89F+l9fi2SBPhOi/Hr46jde60Cnx5INyXNpaLbupM2jOMQ3L9vp9W3YU7C\nREPY75w2tj4ycOgkPEYy/U7NflZzIk7ooIyNBAECgYEAu1VORnuDRdXkqj1H+8kp\nnAT82ErImpP6oUrNIim7x90NFiE/5G6gzd1vRNlbg73b0N5zYWdErJ9HvJtAuBJn\nsjkoycmniPdQK15sccT3mjbmlbyuR0aVPBz0/Q3CNkTlOOj8u+MitlVzRA5J4Md5\n6ggzHBGtOEF36WyI2To8bZc=\n-----END PRIVATE KEY-----\n",
  "client_email": "zzzzz-176@virtual-plexus-379510.iam.gserviceaccount.com",
  "client_id": "108826005939950329076",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/zzzzz-176%40virtual-plexus-379510.iam.gserviceaccount.com"
}


  # Configurazione delle credenziali per accedere a BigQuery
  creds = service_account.Credentials.from_service_account_info(credentials_info)

  # Configurazione delle opzioni di connessione a BigQuery
  client_options = {"api_endpoint": "https://bigquery.googleapis.com"}

  # Inizializzazione del client BigQuery
  client = bigquery.Client(credentials=creds, client_options=client_options)
  ########

  # Estrarre i dati dalle tabelle MySQL e convertire i tipi di dati NumPy in Python standard
  cnx = mysql.connector.connect(**mysql_config)

  df = pd.read_sql_query('SELECT * FROM subgraph', cnx)  ## TODO come si vede in questa riga, il df non prende bene una colonna che imposta tutti i valori a Nan.... Passare da dataframe a list normale
  df = df.apply(pd.to_numeric, errors='coerce')


  # Ottenere le informazioni sullo schema del dataframe pandas df
  columns = df.columns
  dtypes = df.dtypes

  # Creare una lista di oggetti SchemaField di BigQuery
  schema = []

  for name, field_type in zip(columns, dtypes):
    print(name)
    print(field_type)
    if field_type == 'int64':
      field_type = 'INTEGER'
    if field_type == 'float64':
      field_type = 'FLOAT'


    schema_field = bigquery.SchemaField(name=name, field_type=field_type)
    schema.append(schema_field)

  table_ref = client.dataset('dataset_name').table('subgraph1')
  table = bigquery.Table(table_ref, schema=schema)
  table = client.create_table(table)

  # Caricare i dati del dataframe pandas nella tabella di BigQuery
  rows_to_insert = df.values.tolist()
  errors = client.insert_rows(table, rows_to_insert)

  # Verificare che non ci siano errori durante l'inserimento dei dati
  if errors == []:
    print('I dati sono stati inseriti correttamente nella tabella di BigQuery.')
  else:
    print('Si è verificato un errore durante l\'inserimento dei dati nell')


  df = pd.read_sql_query('SELECT * FROM edges', cnx)
  df = df.apply(pd.to_numeric, errors='coerce')


  # Ottenere le informazioni sullo schema del dataframe pandas df
  columns = df.columns
  dtypes = df.dtypes

  # Creare una lista di oggetti SchemaField di BigQuery
  schema = []

  for name, field_type in zip(columns, dtypes):
    print(name)
    print(field_type)
    if field_type == 'int64':
      field_type = 'INTEGER'
    if field_type == 'float64':
      field_type = 'FLOAT'


    schema_field = bigquery.SchemaField(name=name, field_type=field_type)
    schema.append(schema_field)

  table_ref = client.dataset('dataset_name').table('edges1')
  table = bigquery.Table(table_ref, schema=schema)
  table = client.create_table(table)

  # Caricare i dati del dataframe pandas nella tabella di BigQuery
  rows_to_insert = df.values.tolist()
  errors = client.insert_rows(table, rows_to_insert)

  # Verificare che non ci siano errori durante l'inserimento dei dati
  if errors == []:
    print('I dati sono stati inseriti correttamente nella tabella di BigQuery.')
  else:
    print('Si è verificato un errore durante l\'inserimento dei dati nell')

