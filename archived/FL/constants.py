# Matrix constants
adj_filename = '../../dataset/roads.csv'
num_of_vertices = 170
points_per_hour = 12
num_for_predict = 12
len_input = 12

# Model constants
ctx = '3'
in_channels = 2
nb_block = 2
K = 3
nb_chev_filter = 64
nb_time_filter = 64
batch_size = 32
num_of_weeks = 0
num_of_days = 0
num_of_hours = 1
epochs = 2
learning_rate = 0.001
loss_function = 'mae'
metric_method = 'unmask'
missing_value = 0.0

# FL constants
server_start_port = 5000
rounds = 2
model_save_directory = 'models_node'

