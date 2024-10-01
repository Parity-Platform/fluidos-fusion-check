import flwr as fl
from client import FLClient

def start_simulation():
    fl.simulation.start_simulation(
        client_fn=lambda cid: FLClient(),
        num_clients=10,
        config=fl.server.ServerConfig(num_rounds=5),
    )

if __name__ == "__main__":
    start_simulation()