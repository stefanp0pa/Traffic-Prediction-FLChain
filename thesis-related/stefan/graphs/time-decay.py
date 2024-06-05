import numpy as np
import matplotlib.pyplot as plt

def time_decay(t, A, alpha):
    """Compute the value of the time decay function at time t."""
    return A * np.exp(-alpha * t)

def main():
    # Parameters for the time decay function
    A = 1.0    # Initial value
    alpha = 0.9  # Decay rate
    
    # Time values from 0 to 10
    t_values = np.linspace(0, 10, 50)
    
    # Compute the decay values
    decay_values = time_decay(t_values, A, alpha)
    
    # Plot the decay function
    plt.plot(t_values, decay_values, marker='o', linestyle='-')
    plt.title(r'Time Decay Function $f(t) = A \cdot e^{-\alpha t}$')
    plt.xlabel('Time (t)')
    plt.ylabel(r'$f(t)$')
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    main()
