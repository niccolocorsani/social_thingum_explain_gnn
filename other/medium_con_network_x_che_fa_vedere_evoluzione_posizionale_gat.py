import networkx as nx
import numpy as np
from matplotlib import pyplot as plt
from sklearn.manifold import TSNE
from torch_geometric.datasets import Planetoid
import torch.nn.functional as F
from torch.nn import Linear, Dropout
from torch_geometric.nn import GCNConv, GATv2Conv
import torch
torchversion = torch.__version__

if __name__ == '__main__':

    # Import dataset from PyTorch Geometric
    dataset = Planetoid(root=".", name="CiteSeer")




    data = dataset[0]

    # Print information about the dataset
    print(f'Dataset: {dataset}')
    print('-------------------')
    print(f'Number of graphs: {len(dataset)}')
    print(f'Number of nodes: {data.x.shape[0]}')
    print(f'Number of features: {dataset.num_features}')
    print(f'Number of classes: {dataset.num_classes}')

    # Print information about the graph
    print(f'\nGraph:')
    print('------')
    print(f'Edges are directed: {data.is_directed()}')
    print(f'Graph has isolated nodes: {data.has_isolated_nodes()}')
    print(f'Graph has loops: {data.has_self_loops()}')

    from torch_geometric.utils import remove_isolated_nodes

    isolated = (remove_isolated_nodes(data['edge_index'])[2] == False).sum(dim=0).item()
    print(f'Number of isolated nodes = {isolated}')

    from torch_geometric.utils import to_networkx

    G = to_networkx(data, to_undirected=True)
    plt.figure(figsize=(18, 18))
    plt.axis('off')
    nx.draw_networkx(G,
                     pos=nx.spring_layout(G, seed=0),
                     with_labels=False,
                     node_size=50,
                     node_color=data.y,
                     width=2,
                     edge_color="grey"
                     )
    plt.title("Riga 55 dataset originale")
    plt.show()
#####Plot degree del grafo, non so a cosa serve..
    from torch_geometric.utils import degree
    from collections import Counter

    # Get list of degrees for each node
    degrees = degree(data.edge_index[0]).numpy()

    # Count the number of nodes for each degree
    numbers = Counter(degrees)

    # Bar plot
    fig, ax = plt.subplots(figsize=(18, 7))
    ax.set_xlabel('Node degree')
    ax.set_ylabel('Number of nodes')
    plt.bar(numbers.keys(),
            numbers.values(),
            color='#0A047A')
    plt.show()
#####Plot degree del grafo, non so a cosa serve..

    import torch.nn.functional as F
    from torch.nn import Linear, Dropout
    from torch_geometric.nn import GCNConv, GATv2Conv


    class GCN(torch.nn.Module):
        """Graph Convolutional Network"""

        def __init__(self, dim_in, dim_h, dim_out):
            super().__init__()
            self.gcn1 = GCNConv(dim_in, dim_h)
            self.gcn2 = GCNConv(dim_h, dim_out)
            self.optimizer = torch.optim.Adam(self.parameters(),
                                              lr=0.01,
                                              weight_decay=5e-4)

        def forward(self, x, edge_index):
            h = F.dropout(x, p=0.5, training=self.training)
            h = self.gcn1(h, edge_index)
            h = torch.relu(h)
            h = F.dropout(h, p=0.5, training=self.training)
            h = self.gcn2(h, edge_index)
            return h, F.log_softmax(h, dim=1)


    class GAT(torch.nn.Module):
        """Graph Attention Network"""

        def __init__(self, dim_in, dim_h, dim_out, heads=8):
            super().__init__()
            self.gat1 = GATv2Conv(dim_in, dim_h, heads=heads)
            self.gat2 = GATv2Conv(dim_h * heads, dim_out, heads=1)
            self.optimizer = torch.optim.Adam(self.parameters(),
                                              lr=0.005,
                                              weight_decay=5e-4)

        def forward(self, x, edge_index):
            h = F.dropout(x, p=0.6, training=self.training)
            h = self.gat1(x, edge_index)
            h = F.elu(h)
            h = F.dropout(h, p=0.6, training=self.training)
            h = self.gat2(h, edge_index)
            return h, F.log_softmax(h, dim=1)


    def accuracy(pred_y, y):
        """Calculate accuracy."""
        return ((pred_y == y).sum() / len(y)).item()


    def train(model, data):
        """Train a GNN model and return the trained model."""
        criterion = torch.nn.CrossEntropyLoss()
        optimizer = model.optimizer
        epochs = 50 ## TODO da rimettere 200

        model.train()
        for epoch in range(epochs + 1):
            optimizer.zero_grad()
            h, out = model(data.x, data.edge_index)

            ####### Plot l'evoluzione del grafo
            tsne = TSNE(n_components=2, learning_rate='auto',
                        init='pca').fit_transform(h.detach())

            # Plot TSNE
            plt.figure(figsize=(10, 10))
            plt.axis('off')
            plt.scatter(tsne[:, 0], tsne[:, 1], s=50, c=data.y)
            plt.title(
                "Plot nel loop")
            plt.show()
            ####### Plot l'evoluzione del grafo



            loss = criterion(out[data.train_mask], data.y[data.train_mask])
            acc = accuracy(out[data.train_mask].argmax(dim=1), data.y[data.train_mask])
            loss.backward()
            optimizer.step()

            # Validation
            val_loss = criterion(out[data.val_mask], data.y[data.val_mask])
            val_acc = accuracy(out[data.val_mask].argmax(dim=1), data.y[data.val_mask])

            # Print metrics every 10 epochs
            if (epoch % 10 == 0):
                print(f'Epoch {epoch:>3} | Train Loss: {loss:.3f} | Train Acc: '
                      f'{acc * 100:>6.2f}% | Val Loss: {val_loss:.2f} | '
                      f'Val Acc: {val_acc * 100:.2f}%')

        return model


    def test(model, data):
        """Evaluate the model on test set and print the accuracy score."""
        model.eval()
        _, out = model(data.x, data.edge_index)
        acc = accuracy(out.argmax(dim=1)[data.test_mask], data.y[data.test_mask])
        return acc


    # Create GCN
    gcn = GCN(dataset.num_features, 16, dataset.num_classes)
    print(gcn)

    # Train
    train(gcn, data)

    # Test
    acc = test(gcn, data)
    print(f'GCN test accuracy: {acc*100:.2f}%\n')



######################### TSNE PLOT

    # Create GAT
    gat = GAT(dataset.num_features, 8, dataset.num_classes)
    print(gat)

    # Train
    train(gat, data)

    # Test
    acc = test(gat, data)
    print(f'GAT test accuracy: {acc * 100:.2f}%\n')

    untrained_gat = GAT(dataset.num_features, 8, dataset.num_classes)

    # Get embeddings
    h, _ = untrained_gat(data.x, data.edge_index)

    # Train TSNE
    tsne = TSNE(n_components=2, learning_rate='auto',
                init='pca').fit_transform(h.detach())

    # Plot TSNE
    plt.figure(figsize=(10, 10))
    plt.axis('off')
    plt.scatter(tsne[:, 0], tsne[:, 1], s=50, c=data.y)
    plt.title("Riga 203, credo sia il modello non addestrato e quindi con un solo aggiornamento di gat perchè non passa attraverso le epoche")
    plt.show()


    # Get embeddings
    h, _ = gat(data.x, data.edge_index)

    # Train TSNE
    tsne = TSNE(n_components=2, learning_rate='auto',
                init='pca').fit_transform(h.detach())

    # Plot TSNE
    plt.figure(figsize=(10, 10))
    plt.axis('off')
    plt.scatter(tsne[:, 0], tsne[:, 1], s=50, c=data.y)
    plt.title("Riga 218, con il modello addestrato")
    plt.show()

## TODO fare questo plot all'interno delle epoche ecc..



################# Plot accuracy for each node degree

    from torch_geometric.utils import degree

    # Get model's classifications
    _, out = gat(data.x, data.edge_index)

    # Calculate the degree of each node
    degrees = degree(data.edge_index[0]).numpy()

    # Store accuracy scores and sample sizes
    accuracies = []
    sizes = []

    # Accuracy for degrees between 0 and 5
    for i in range(0, 6):
        mask = np.where(degrees == i)[0]
        accuracies.append(accuracy(out.argmax(dim=1)[mask], data.y[mask]))
        sizes.append(len(mask))

    # Accuracy for degrees > 5
    mask = np.where(degrees > 5)[0]
    accuracies.append(accuracy(out.argmax(dim=1)[mask], data.y[mask]))
    sizes.append(len(mask))

    # Bar plot
    fig, ax = plt.subplots(figsize=(18, 9))
    ax.set_xlabel('Node degree')
    ax.set_ylabel('Accuracy score')
    plt.bar(['0', '1', '2', '3', '4', '5', '>5'],
            accuracies,
            color='#0A047A')
    for i in range(0, 7):
        plt.text(i, accuracies[i], f'{accuracies[i] * 100:.2f}%',
                 ha='center', color='#0A047A')
    for i in range(0, 7):
        plt.text(i, accuracies[i] // 2, sizes[i],
                 ha='center', color='white')
