import pandas as pd
import numpy as np

# Simulate federated learning metrics
def generate_training_data(rounds=10):
    rounds = np.arange(1, rounds + 1)
    loss = np.exp(-0.3 * rounds) + np.random.normal(0, 0.02, rounds.size)
    accuracy = 1 - loss + np.random.normal(0, 0.01, rounds.size)
    return pd.DataFrame({'Round': rounds, 'Loss': loss, 'Accuracy': accuracy})

# Simulate device statuses
def generate_device_data(devices=5):
    device_ids = [f'Device_{i}' for i in range(1, devices + 1)]
    statuses = np.random.choice(['Online', 'Offline'], size=devices, p=[0.8, 0.2])
    cpu_usage = np.random.uniform(10, 90, size=devices)
    memory_usage = np.random.uniform(10, 90, size=devices)
    return pd.DataFrame({
        'Device ID': device_ids,
        'Status': statuses,
        'CPU Usage (%)': cpu_usage,
        'Memory Usage (%)': memory_usage
    })