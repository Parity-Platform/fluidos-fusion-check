import torch
from torch import nn, optim
from torch.utils.data import DataLoader, TensorDataset
import flwr as fl

# Define your model (e.g., a simple neural network)
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.fc = nn.Linear(10, 2)  # Adjust input and output sizes as needed

    def forward(self, x):
        return self.fc(x)

# Load local data
def load_data():
    # Replace with actual data loading logic
    X = torch.randn(100, 10)
    y = torch.randint(0, 2, (100,))
    dataset = TensorDataset(X, y)
    return DataLoader(dataset, batch_size=16)

# Define Flower client
class FLClient(fl.client.NumPyClient):
    def __init__(self):
        self.model = Net()
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.SGD(self.model.parameters(), lr=0.01)
        self.train_loader = load_data()

    def get_parameters(self):
        return [val.cpu().numpy() for val in self.model.state_dict().values()]

    def set_parameters(self, parameters):
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = {k: torch.tensor(v) for k, v in params_dict}
        self.model.load_state_dict(state_dict, strict=True)

    def fit(self, parameters, config):
        self.set_parameters(parameters)
        self.model.train()
        for epoch in range(1):  # One epoch per round
            for data, target in self.train_loader:
                self.optimizer.zero_grad()
                output = self.model(data)
                loss = self.criterion(output, target)
                loss.backward()
                self.optimizer.step()
        return self.get_parameters(), len(self.train_loader.dataset), {}

    def evaluate(self, parameters, config):
        # Implement evaluation logic if needed
        return 0.0, len(self.train_loader.dataset), {}

if __name__ == "__main__":
    client = FLClient()
    fl.client.start_numpy_client(server_address="server:8080", client=client)