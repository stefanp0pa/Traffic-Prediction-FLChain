import numpy as np
import matplotlib.pyplot as plt

def compute_lambda_sequence(alpha, t_max):
    # Initialize the lambda sequence with the starting value
    lambda_values = [1.0]

    for t in range(1, t_max):
        # Compute the numerator sum using the new formula
        numerator_sum = sum(np.exp(-alpha * (t - l)) * lambda_values[l - 1] for l in range(1, t))
        # Compute the denominator sum
        denominator_sum = sum(np.exp(-alpha * (t - l)) for l in range(1, t + 1))
        
        # Ensure floating-point division
        if denominator_sum != 0:  # Avoid division by zero
            lambda_t = numerator_sum / denominator_sum
            lambda_t += 0.01
        else:
            lambda_t = 0
        
        # Append the computed value to the sequence
        lambda_values.append(lambda_t)

    print(lambda_values)
    return lambda_values

def main():
    # Define the alpha value and the number of points to compute
    alpha = 0.01
    t_max = 100
    
    # Compute the lambda sequence
    lambda_values = compute_lambda_sequence(alpha, t_max)
    lambda_values = lambda_values[1:]
    # Create the x values (1, 2, 3, ..., t_max)
    x_values = list(range(1, t_max))
    
    # Plot the lambda values
    plt.plot(x_values, lambda_values, marker='o', linestyle='-')
    plt.title(r'$\lambda(t)$ Sequence with $\alpha={}$'.format(alpha))
    plt.xlabel('t')
    plt.ylabel(r'$\lambda(t)$')
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    main()
