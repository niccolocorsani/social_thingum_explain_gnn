from neo4j import GraphDatabase
import torch
import utility


class App:

  def __init__(self, uri, user, password):
    self.uri = uri
    self.user = user
    self.password = password
    self.driver = GraphDatabase.driver(uri, auth=(user, password))

  def close(self):
    # Don't forget to close the driver connection when you are finished with it
    self.driver.close()

  def load_data_to_neo4j(self, edge_index, edge_label):
    driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
    with driver.session() as session:
      # Creazione dei nodi utente
      user_nodes = set(edge_index[0].tolist())
      for user in user_nodes:
        query = "CREATE (:User {name: $name})"
        session.run(query, name=str(user))

      # Creazione dei nodi film
      movie_nodes = set(edge_index[1].tolist())
      for movie in movie_nodes:
        query = "CREATE (:Movie {name: $name})"
        session.run(query, name=str(movie))

      # Creazione delle relazioni tra utenti e film
      for i in range(edge_index.shape[1]):
        user = str(edge_index[0][i].item())
        movie = str(edge_index[1][i].item())
        rating = str(edge_label[i].item())
        query = "MATCH (u:User {name: $user}), (m:Movie {name: $movie}) CREATE (u)-[:RATES {rating: $rating}]->(m)"
        session.run(query, user=user, movie=movie, rating=rating)

  def delete_all_nodes_and_relationships(self):
    with GraphDatabase.driver(self.uri, auth=(self.user, self.password)) as driver:
      with driver.session() as session:
        # Eseguire una transazione per eliminare tutti i nodi e le relazioni
        session.write_transaction(lambda tx: tx.run("MATCH (n) DETACH DELETE n"))


if __name__ == "__main__":

  # uri = "neo4j+s://3b8c198b.databases.neo4j.io"
  uri = "neo4j://34.154.222.156:7687"
  user = "neo4j"
  password = "Ontologia235g!"
  app = App(uri, user, password)


#### Carica dati
  app.delete_all_nodes_and_relationships()
  data, edge_index = utility.read_data()
  edge_index = data['user', 'rates', 'item'].edge_index
  edge_label = data['user', 'rates', 'item'].edge_label

  print(edge_index.shape)
  app.load_data_to_neo4j(edge_index=edge_index, edge_label=edge_label)
#### Carica dati

  print('fine')
  app.close()
