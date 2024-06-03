from clusters import create_infrastructure
import numpy as np
from utils import write_hash, check_and_create_directory, upload_file, adjancency_matrix_cluster, create_model
import torch

def create_cluster():
    graph, leaders = create_infrastructure()
    clusters = []
    cluster_dir = "clusters"
    check_and_create_directory(cluster_dir)
    for index_cluster, leader in enumerate(leaders):
        cluster_nodes = [node for node in graph if leader in graph[node]['leaders']]
        clusters.append(cluster_nodes)
        # cluster_path = f"{cluster_dir}/{index_cluster + 1}"
        # write_hash(cluster_nodes, cluster_path)
        # clusters.append(upload_file(cluster_path))
    
    write_hash(clusters, 'test.txt')
    # write_hash(clusters, 'hash/clusters_node.txt')


def create_data_per_node():
    directory_path='train_nodes'
    no_nodes = 170
    check_and_create_directory(directory_path)
    data = np.load('data/flow_occupy.npz')
    hash_codes = []
    for index in range(0, no_nodes):
        print(f"Node: {index + 1}")
        file_path = f'{directory_path}/{index + 1}.npz'
        new_data = {
            'train_x':data['train_x'][:, [index], :, :],
            'train_target':data['train_target'],
            'test_x':data['test_x'][:, [index], :, :],
            'test_target':data['test_target'],
            'mean':data['mean'][:, :, [0, 2], :],
            'std':data['std'][:, :, [0, 2], :]
        }
        np.savez_compressed(file_path, 
            train_x=new_data['train_x'], 
            train_target=new_data['train_target'], 
            test_x=new_data['test_x'], 
            test_target=new_data['test_target'],
            mean=new_data['mean'],
            std=new_data['std'],
            node=index+1)
        hash_codes.append(upload_file(file_path))
    write_hash(hash_codes, 'hash/train_nodes_hash.txt')


def create_adj_matrix():
    graph, leaders = create_infrastructure()
    adj_hash_clusters = []
    adj_dir = "adj_clusters"
    distance_df_filename = 'data/roads.csv'
    check_and_create_directory(adj_dir)
  
    for index_cluster, leader in enumerate(leaders):
        cluster_nodes = [node for node in graph if leader in graph[node]['leaders']]
        matrix = adjancency_matrix_cluster(distance_df_filename, cluster_nodes)
        adj_cluster_path = f"{adj_dir}/{index_cluster + 1}.npz"
        np.savez_compressed(adj_cluster_path,
                            matrix=matrix,
                            cluster_index=index_cluster + 1,
                            nodes=cluster_nodes)
        adj_hash_clusters.append(upload_file(adj_cluster_path))
    
    write_hash(adj_hash_clusters, 'hash/adj_clusters_hash.txt')


def create_global_model():
    graph, leaders = create_infrastructure()
    model_hash_clusters = []
    model_dir = "model_clusters"
    distance_df_filename = 'data/roads.csv'
    check_and_create_directory(model_dir)
  
    for index_cluster, leader in enumerate(leaders):
        cluster_nodes = [node for node in graph if leader in graph[node]['leaders']]
        matrix = adjancency_matrix_cluster(distance_df_filename, cluster_nodes)
        model = create_model(matrix, 1)
        model_cluster_path = f"{model_dir}/{index_cluster}.pth"
        torch.save(model.state_dict(), model_cluster_path)
        model_hash_clusters.append(upload_file(model_cluster_path))
    
    write_hash(model_hash_clusters, 'hash/model_hash_clusters.txt')


if __name__ == "__main__":
    create_cluster()  
    # create_data_per_node()
    # create_adj_matrix()
    # create_global_model()