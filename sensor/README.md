This Python script serves a simple HTTP endpoint that:

1. Listens for POST requests containing sensor data
2. Accepts any data structure
3. Logs the data to the terminal (with timestamps)
4. Returns a success response to the client

### How to use:

1. Save the code to a file (e.g., `sensor_server.py`)
2. Run the server: `python sensor_server.py` (optional: specify a port like `python sensor_log.py 5000`)
3. Send POST requests with your sensor data to `http://localhost:8080` (or your custom port)

The server will automatically handle both JSON and non-JSON data, and it includes CORS headers to allow cross-origin requests if needed.