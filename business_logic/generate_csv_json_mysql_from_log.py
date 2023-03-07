def convert_json_to_csv(json_file_name, csv_file_name):
  import pandas as pd
  import json

  with open(ROOT_DIR + json_file_name, 'r') as f:
    data = json.load(f)
  df = pd.DataFrame(data)
  df.to_csv(ROOT_DIR + csv_file_name, index=False)


import os
import mysql.connector
import json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def convert_log_to_json(log_file_path, json_file_path):
  with open(log_file_path, 'r') as f:
    logs = f.read().split('\n\n')
####TODO Perhcè prende sempre gli stessi valori ??
  results = []
  for log in logs:
    if not log:
      continue
    lines = log.strip().split('\n')
    for line in lines:
      values = line.strip().split(';')
      log_dict = {}

      for element in values:
        key = element.split(":")[0]
        value = element.split(":")[1]
        if key == 'edge_index':

          value = value.replace('tensor([', '').replace('])', '')
          input_string = value
          matrix_string = '[' + input_string.replace(' ', '').replace('][', '],[') + ']'
          # La riga sopra trasforma la stringa in un formato che Python riconosce come matrice
          matrix = eval(matrix_string)
          # La funzione eval() interpreta la stringa come codice Python, quindi ora abbiamo una matrice
          transposed_matrix = list(map(list, zip(*matrix)))
          # La funzione zip() crea una lista di tuple, dove ogni tupla contiene gli elementi corrispondenti
          # dalle righe della matrice originale. La funzione map() applica la funzione list() a ogni tupla,
          # in modo da convertire le tuple in liste. Infine, la funzione list() converte il risultato in una lista.
          value = transposed_matrix
        elif key == 'index_prediction_to_evaluate':
          value = int(value)
        elif key == 'nodes_corresponding_to_index_prediction_to_evaluate':
          value = [int(x) for x in value.split(',')]
        elif key == 'min_number_of_edges':
          value = int(value)
        elif key == 'deepnes_of_node_expansion':
          value = int(value)
        elif key == 'number_of_brother':
          value = int(value)
        elif key == 'win':
          value = float(value)
        elif key == 'difference_in_prediction':
          continue
        log_dict[key] = value
      results.append(log_dict)

  with open(json_file_path, 'w') as f:
    json.dump(results, f)


def get_mysql_connection():
  # Connessione al database
  conn = mysql.connector.connect(
    host="localhost",
    user="myuser",
    password="mypassword",
    database="mydatabase"
  )
  return conn

def drop_all_tables(conn):

  # get a cursor object
  cursor = conn.cursor()

  # get a list of all the tables in the database
  cursor.execute("SHOW TABLES")
  tables = cursor.fetchall()

  # loop through the tables and drop each one
  for table in tables:
    table_name = table[0]
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

  # commit the changes and close the connection
  conn.commit()
  cursor.close()
  conn.close()

def create_tables(conn):
  cursor = conn.cursor()

  subgraph_schema = "CREATE TABLE IF NOT EXISTS subgraph (id INT AUTO_INCREMENT PRIMARY KEY, index_prediction_to_evaluate INT, nodes_corresponding_to_index_prediction_to_evaluate VARCHAR(255), min_number_of_edges INT, deepnes_of_node_expansion INT, win DECIMAL(10, 9),number_of_brother INT)"
  cursor.execute(subgraph_schema)

  edges_schema = "CREATE TABLE IF NOT EXISTS edges (id INT AUTO_INCREMENT PRIMARY KEY, subgraph_id INT, source_node INT, target_node INT, FOREIGN KEY (subgraph_id) REFERENCES subgraph(id))"
  cursor.execute(edges_schema)

  cursor.close()
  conn.close()


def load_json_to_mysql(json_file, conn):
  with open(json_file) as f:
    json_data = json.load(f)

  cursor = conn.cursor()
  # Inserimento dei dati nella tabella "subgraph"
  values = []
  edge_values = []
  for item in json_data:
    nodes = json.dumps(item["nodes_corresponding_to_index_prediction_to_evaluate"])
    subgraph_values = (
    item["index_prediction_to_evaluate"], nodes, item["min_number_of_edges"], item["deepnes_of_node_expansion"],
    item["win"], item['number_of_brother'])
    cursor.execute(
      "INSERT INTO subgraph (index_prediction_to_evaluate, nodes_corresponding_to_index_prediction_to_evaluate, min_number_of_edges, deepnes_of_node_expansion, win,number_of_brother) VALUES (%s, %s, %s, %s, %s,%s)",
      subgraph_values)
    subgraph_id = cursor.lastrowid
    for edge in item["edge_index"]:
      edge_values.append((subgraph_id, edge[0], edge[1]))

  # Esecuzione delle query di inserimento
  edge_sql = "INSERT INTO edges (subgraph_id, source_node, target_node) VALUES (%s, %s, %s)"
  cursor.executemany(edge_sql, edge_values)

  # Commit delle modifiche e chiusura della connessione
  conn.commit()
  cursor.close()
  conn.close()


def print_mysql_tables(conn):
  ## TODO capire perchè non salva le tavole..... nella creazione dello schema
  cursor = conn.cursor()

  # Query per selezionare tutti i valori dalla tabella "subgraph"
  subgraph_sql = "SELECT * FROM subgraph"
  cursor.execute(subgraph_sql)
  subgraph_data = cursor.fetchall()

  # Stampa dei valori della tabella "subgraph"
  print("TABELLA SUBGRAPH")
  print(
    "ID\tINDEX_PREDICTION_TO_EVALUATE\tNODES_CORRESPONDING_TO_INDEX_PREDICTION_TO_EVALUATE\tMIN_NUMBER_OF_EDGES\tDEEPNES_OF_NODE_EXPANSION\tWIN")
  for row in subgraph_data:
    print(f"{row[0]}\t{row[1]}\t{row[2]}\t{row[3]}\t{row[4]}\t{row[5]}")
  print("")

  # Query per selezionare tutti i valori dalla tabella "edges"
  edges_sql = "SELECT * FROM edges"
  cursor.execute(edges_sql)
  edges_data = cursor.fetchall()

  # Stampa dei valori della tabella "edges"
  print("TABELLA EDGES")
  print("ID\tSUBGRAPH_ID\tSOURCE_NODE\tTARGET_NODE")
  for row in edges_data:
    print(f"{row[0]}\t{row[1]}\t{row[2]}\t{row[3]}")

  # Chiusura della connessione
  cursor.close()
  conn.close()

def run_all_pipeline_to_update_my_sql():
  convert_log_to_json(ROOT_DIR + '/log_esito_montecarlo_1.0.1.txt', ROOT_DIR + '/log.json')
  conn = get_mysql_connection()
  drop_all_tables(conn)
  conn.connect()
  create_tables(conn)
  conn.connect()
  load_json_to_mysql(ROOT_DIR + '/log.json', conn)
  conn.connect()
  print_mysql_tables(conn)
if __name__ == '__main__':

  run_all_pipeline_to_update_my_sql()


