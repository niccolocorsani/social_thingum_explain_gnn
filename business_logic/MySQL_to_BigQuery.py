import time
import mysql.connector
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
def trasferisci_mysql_a_big_query():
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

  df = pd.read_sql_query('SELECT * FROM subgraph',
                         cnx)
  df = df.apply(lambda x: x if x.name == 'nodes_corresponding_to_index_prediction_to_evaluate' else pd.to_numeric(x,
                                                                                                                  errors='coerce'),
                axis=0)
  # Ottenere le informazioni sullo schema del dataframe pandas df
  columns = df.columns
  dtypes = df.dtypes

  # Creare una lista di oggetti SchemaField di BigQuery
  schema = []

  # Mettere i tipi nel formato che piace a BigQuery
  for name, field_type in zip(columns, dtypes):
    print(name)
    print(field_type)
    if field_type == 'int64':
      field_type = 'INTEGER'
    if field_type == 'float64':
      field_type = 'FLOAT'
    if field_type == 'object':
      field_type = 'STRING'

    schema_field = bigquery.SchemaField(name=name, field_type=field_type)
    schema.append(schema_field)

  dataset_name = 'dataset_name'

  # Ottieni una lista di tutte le tabelle nel dataset
  client.list_tables(dataset_name)

  # # Itera su ogni tabella e rimuovila
  # for table in tables:
  #   table_ref = client.dataset(dataset_name).table(table.table_id)
  #   client.delete_table(table_ref)
  #   print(f'Tabella {table.table_id} rimossa dal dataset {dataset_name}')

  # Se prima voglio eliminare la tabella e ricrearla, devo mettere un timeout lungo, se no non troverà la tabella nel codice seguente
  # Come work around attulae, prima di ogni esecuzione devo eliminare le tabelle a mano, fare run manuali finchè non l'ha creato ecc....
  table_ref = client.dataset('dataset_name').table('subgraph1')
  table = bigquery.Table(table_ref, schema=schema)
  # table = client.create_table(table)

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
    if field_type == 'object':
      field_type = 'STRING'

    schema_field = bigquery.SchemaField(name=name, field_type=field_type)
    schema.append(schema_field)

  table_ref = client.dataset('dataset_name').table('edges1')
  table = bigquery.Table(table_ref, schema=schema)

  # table = client.create_table(table)

  # Caricare i dati del dataframe pandas nella tabella di BigQuery
  rows_to_insert = df.values.tolist()
  errors = client.insert_rows(table, rows_to_insert)

  # Verificare che non ci siano errori durante l'inserimento dei dati
  if errors == []:
    print('I dati sono stati inseriti correttamente nella tabella di BigQuery.')
  else:
    print('Si è verificato un errore durante l\'inserimento dei dati nell')

  #   # Set up query
  #   query = """
  # SELECT distinct(nodes_corresponding_to_index_prediction_to_evaluate) FROM `virtual-plexus-379510.dataset_name.join_subgraph_edges`
  #   """
  #
  #   # Run query and get results
  #   query_job = client.query(query)
  #   results = query_job.result()
  #
  #   valori = []
  #   # Print results
  #   for row in results:
  #     valori.append(eval(row[
  #                          'nodes_corresponding_to_index_prediction_to_evaluate']))  # estraiamo la sottostringa contenente i valori tra apici singoli
  #
  #   for element in valori:
  #     table_name = "join_subgraph_edges_filtered_by_edge" + str(element).replace(" ", "")
  #     query = """
  #             CREATE TABLE `dataset_name.{table}`
  #             AS
  #             SELECT tabella1.id, tabella1.index_prediction_to_evaluate, tabella1.min_number_of_edges, tabella1.win, tabella1.nodes_corresponding_to_index_prediction_to_evaluate,tabella1.number_of_brother, tabella1.difference_in_prediction, tabella1.deepnes_of_node_expansion, tabella2.source_node ,tabella2.target_node
  #             FROM `dataset_name.subgraph1` as tabella1
  #             JOIN `dataset_name.edges1` as tabella2
  #             ON tabella1.id = tabella2.subgraph_id
  #             where tabella1.nodes_corresponding_to_index_prediction_to_evaluate =
  #             """ + str(element) +';'
  #
  #     # Esegui la query
  #     query_job = client.query(query)

  # Definisci la tua query
  # query = """
  #         CREATE TABLE `dataset_name.join_subgraph_edges`
  #         AS
  #         SELECT tabella1.id, tabella1.index_prediction_to_evaluate, tabella1.min_number_of_edges, tabella1.win, tabella1.nodes_corresponding_to_index_prediction_to_evaluate,tabella1.number_of_brother, tabella1.difference_in_prediction, tabella1.deepnes_of_node_expansion, tabella2.source_node ,tabella2.target_node
  #         FROM `dataset_name.subgraph1` as tabella1
  #         JOIN `dataset_name.edges1` as tabella2
  #         ON tabella1.id = tabella2.subgraph_id;
  # """

  # # Esegui la query
  # query_job = client.query(query)

  # una query che mi unisce il valore della colonna source e target in una stringa unica
  query = """CREATE TABLE `dataset_name.join_subgraph_edges`
AS
SELECT tabella1.id, tabella1.index_prediction_to_evaluate, tabella1.min_number_of_edges, tabella1.win, tabella1.nodes_corresponding_to_index_prediction_to_evaluate, tabella1.number_of_brother, tabella1.difference_in_prediction, tabella1.deepnes_of_node_expansion, CONCAT(tabella2.source_node, ',', tabella2.target_node) AS source_target_nodes
FROM `dataset_name.subgraph1` AS tabella1
JOIN `dataset_name.edges1` AS tabella2
ON tabella1.id = tabella2.subgraph_id;
         """
  # Esegui la query
  query_job = client.query(query)


if __name__ == '__main__':
  trasferisci_mysql_a_big_query()
