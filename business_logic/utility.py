import os
import torch
from torch_geometric.data import HeteroData
from torch_geometric.transforms import ToUndirected

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def readIntFromFile(filename):
  with open(filename, 'r') as f:
    content = f.read()
  return content
def readTensorFromFile(filename):
  with open(filename, 'r') as f:
    contents = f.read()
    contents = contents.replace('tensor(', '').replace(')', '')
    mytensor = torch.tensor(eval(contents))

  return mytensor
def write_to_graph_format(edge_index, fileName):
  with open(fileName, "w") as file:
    file.write("")
  for i in range(edge_index.shape[1] - 1):
    s = edge_index[0, i].item()
    o = edge_index[1, i + 1].item()

    with open(fileName, "a") as file:
      if i == 0:
        file.write('[')
        file.write('{\"source\":\"user_' + str(s) + '\", \"target\":\"movie_' + str(o) + '\"},\n')
      if i == (edge_index.shape[
                 1] - 2):
        file.write('{\"source\":\"user_' + str(s) + '\", \"target\":\"movie_' + str(o) + '\"}\n')
        file.write(']')
      else:
        file.write('{\"source\":\"user_' + str(s) + '\", \"target\":\"movie_' + str(
          o) + '\"},\n')  ## JSON hanno bisogno delle virgolette nella key
def read_data():

  device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
  movie_x = readTensorFromFile(ROOT_DIR + "/output_alberto/movie_x.txt")
  edge_label = readTensorFromFile(ROOT_DIR + "/output_alberto/edge_label.txt")
  edge_index = readTensorFromFile(ROOT_DIR + "/output_alberto/edge_index.txt")
  movie_len = readIntFromFile(ROOT_DIR + "/output_alberto/movies_len.txt")
  users_len = readIntFromFile(ROOT_DIR + "/output_alberto/users_len.txt")

  # Write a function to create a list of users where each user is a number from 0 to users_len
  users = []
  for i in range(int(users_len)):
    users.append(i)

  data = HeteroData()
  data['user'].num_nodes = len(users)  # Users do not have any features.
  data['movie'].x = movie_x

  # Create an edge type "('user', 'rates', 'movie')" and building the
  # graph connectivity:
  data['user', 'rates', 'movie'].edge_index = edge_index
  data['user', 'rates', 'movie'].edge_label = edge_label

  # Add user node features for message passing:
  data['user'].x = torch.eye(data['user'].num_nodes, device=device)
  del data['user'].num_nodes

  # Add a reverse ('movie', 'rev_rates', 'user') relation for message passing.
  data = ToUndirected()(data)
  del data['movie', 'rev_rates', 'user'].edge_label  # Remove "reverse" label.
  data = data.to(device)

  return data, edge_index
def removeFilesFromFolder(folderName):
  import os
  import shutil

  for filename in os.listdir(folderName):
    file_path = os.path.join(folderName, filename)
    try:
      if os.path.isfile(file_path) or os.path.islink(file_path):
        os.unlink(file_path)
      elif os.path.isdir(file_path):
        shutil.rmtree(file_path)
    except Exception as e:
      print('Failed to delete %s. Reason: %s' % (file_path, e))

