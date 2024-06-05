import numpy as np
import matplotlib.pyplot as plt

def exponentially_weighted_moving_average(data, alpha):
    ewma_values = [data[0]]  # Initialize with the first data point
    
    for i in range(1, len(data)):
        ewma = alpha * data[i] + (1 - alpha) * ewma_values[-1]
        ewma_values.append(ewma)
    
    return ewma_values

def exponentially_weighted_moving_average2(alpha, t_max, acc):
    lambda_values = [1.0]
    ewma_values = [1.0]
    for t in range(1, t_max):
        ewma = alpha * lambda_values[t-1] + (1 - alpha) * ewma_values[-1]
        ewma_values.append(ewma)
        lambda_values.append(ewma + acc)
    
    return ewma_values, lambda_values

import random

def generate_random_numbers(center, count=100, delta=0.1):
    return [random.uniform(center - delta, center + delta) for _ in range(count)]

def stabilized_ewma(decay, t_max, acc, acc_scale, emwa_factor=0.75):
    lambda_values = [0.0]
    for t in range(1, t_max):
        numerator_sum = sum(np.exp(-decay * (t - l)) * lambda_values[l] for l in range(0, t))
        denominator_sum = 1 + sum(np.exp(-decay * (t - l)) for l in range(0, t))
        lambda_t = numerator_sum / denominator_sum
        lambda_values.append((1 - emwa_factor) * lambda_t + emwa_factor* (acc[t]/acc_scale))

    return lambda_values        

def reputation_scores_evolution():
    decay = 0.25
    t_max = 50
    acc_scale = 0.65
    ewma_factor = 0.3
    
    acc_1 = 1.0
    random_data_1 = generate_random_numbers(acc_1, count=50, delta=0.05)
    
    acc_2 = 0.75
    random_data_2 = generate_random_numbers(acc_2, count=50, delta=0.05)
    
    acc_3 = 0.5
    random_data_3 = generate_random_numbers(acc_3, count=50, delta=0.05)
    
    acc_4 = 0.25
    random_data_4 = generate_random_numbers(acc_4, count=50, delta=0.05)
    
    reputation_values_1 = stabilized_ewma(decay, t_max, random_data_1, acc_scale, ewma_factor)
    reputation_values_2 = stabilized_ewma(decay, t_max, random_data_2, acc_scale, ewma_factor)
    reputation_values_3 = stabilized_ewma(decay, t_max, random_data_3, acc_scale, ewma_factor)
    reputation_values_4 = stabilized_ewma(decay, t_max, random_data_4, acc_scale, ewma_factor)
    
    x_values = list(range(0, t_max))
    
    # Plot all reputation values on the same graph
    plt.plot(x_values, reputation_values_1, marker='.', linestyle='-', label='Acc. 1.00, dev. 0.05')
    plt.plot(x_values, reputation_values_2, marker='.', linestyle='-', label='Acc. 0.75, dev. 0.05')
    plt.plot(x_values, reputation_values_3, marker='.', linestyle='-', label='Acc. 0.50, dev. 0.05')
    plt.plot(x_values, reputation_values_4, marker='.', linestyle='-', label='Acc. 0.25, dev. 0.05')
    
    # plt.title(f'Reputation with decay={decay}')
    plt.xlabel('Rounds')
    plt.ylabel('Reputation')
    plt.grid(True)
    plt.legend(fontsize='small')  # Add a legend to distinguish between the three lines
    plt.show()


def reputation_drop_decays():
    decay_1 = 0.25
    decay_2 = 0.5
    decay_3 = 0.75
    t_max = 50
    acc_scale = 0.65
    ewma_factor = 0.3

    acc_1 = 1.0
    random_data_1 = generate_random_numbers(acc_1, count=20, delta=0.05)
    acc_2 = 0.25
    random_data_2 = generate_random_numbers(acc_2, count=10, delta=0.05)
    acc_3 = 0.25
    random_data_3 = generate_random_numbers(acc_3, count=20, delta=0.05)
    
    random_data = random_data_1 + random_data_2 + random_data_3

    reputation_values_1 = stabilized_ewma(decay_1, t_max, random_data, acc_scale, ewma_factor)
    reputation_values_2 = stabilized_ewma(decay_2, t_max, random_data, acc_scale, ewma_factor)
    reputation_values_3 = stabilized_ewma(decay_3, t_max, random_data, acc_scale, ewma_factor)
    
    x_values = list(range(0, t_max))
    
    # Plot all reputation values on the same graph
    plt.plot(x_values, reputation_values_1, marker='.', linestyle='-', label='Decay = 0.25')
    plt.plot(x_values, reputation_values_2, marker='.', linestyle='-', label='Decay = 0.50')
    plt.plot(x_values, reputation_values_3, marker='.', linestyle='-', label='Decay = 0.75')
    
    # plt.title(f'Reputation with decay={decay}')
    plt.xlabel('Rounds')
    plt.ylabel('Reputation')
    plt.grid(True)
    plt.legend(fontsize='small')  # Add a legend to distinguish between the three lines
    plt.show()
    

def main():
    # reputation_scores_evolution()
    reputation_drop_decays()

if __name__ == '__main__':
    main()
