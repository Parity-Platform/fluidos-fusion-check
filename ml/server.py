import flwr as fl

def start_server():
    # Start Flower server
    fl.server.start_server(
        server_address="0.0.0.0:8080",
        config=fl.server.ServerConfig(num_rounds=5),
    )

if __name__ == "__main__":
    start_server()