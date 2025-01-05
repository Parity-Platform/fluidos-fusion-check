import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler
import numpy as np

import pandas as pd

# Define the neural network model
class SimpleNN(nn.Module):
    def __init__(self, input_size, hidden_size):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, 1)
    
    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        out = self.relu(out)
        out = self.fc3(out)
        return out

# Training function
def train_local_nn(client_data, client_targets, input_size, hidden_size, epochs=100, lr=0.001):
    model = SimpleNN(input_size, hidden_size)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    prev_loss = 1000000000000.0
    for epoch in range(epochs):
        model.train()
        outputs = model(client_data)
        loss = criterion(outputs, client_targets)
        print(f"loss: {loss/prev_loss}")
        prev_loss = loss
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    
    return model

# Aggregation function for federated learning
def aggregate_nn_models(models):
    global_model = SimpleNN(input_size, hidden_size)
    
    with torch.no_grad():
        # Stack and average each layer's weights and biases separately
        for name, param in global_model.named_parameters():
            # Stack corresponding layers' parameters from each model and compute the mean
            param.data = torch.mean(torch.stack([m.state_dict()[name] for m in models]), dim=0)
    
    return global_model


# Load the dataset to understand its structure
file_path = './seraf_energy.csv'
data = pd.read_csv(file_path)

# Display the first few rows of the data to understand its structure
data.head()

# Convert timestamp to datetime format and extract relevant features (e.g., hour, day of the week)
data['timestamp'] = pd.to_datetime(data['timestamp'])
data['hour'] = data['timestamp'].dt.hour
data['day_of_week'] = data['timestamp'].dt.dayofweek

# Drop columns that are not useful for prediction
data = data.drop(columns=['unit', 'timestamp', 'charge_id'])

# Split the dataset into two clients (randomly for simulation purposes)
client_1_data = data.sample(frac=0.5, random_state=1)
client_2_data = data.drop(client_1_data.index)

# Example code to train and aggregate models
input_size = 2  # Number of features (e.g., hour, day_of_week)
hidden_size = 100
X_scaled = StandardScaler().fit_transform(data[['hour', 'day_of_week']])
y = data['value'].values
X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
y_tensor = torch.tensor(y, dtype=torch.float32).view(-1, 1)

# Split data between clients
client_1_data_tensor = X_tensor[:len(client_1_data)]
client_1_targets_tensor = y_tensor[:len(client_1_data)]
client_2_data_tensor = X_tensor[len(client_1_data):]
client_2_targets_tensor = y_tensor[len(client_1_data):]

# Train local models
client_1_nn = train_local_nn(client_1_data_tensor, client_1_targets_tensor, input_size, hidden_size)
client_2_nn = train_local_nn(client_2_data_tensor, client_2_targets_tensor, input_size, hidden_size)

# Aggregate models
global_nn_model = aggregate_nn_models([client_1_nn, client_2_nn])

# Evaluate the global model
global_nn_model.eval()
with torch.no_grad():
    y_pred_tensor = global_nn_model(X_tensor)
    mse_nn = nn.MSELoss()(y_pred_tensor, y_tensor).item()

print(f"Mean Squared Error of the Global Model: {mse_nn}")