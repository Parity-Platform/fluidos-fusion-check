from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import datetime
import sys

class SensorDataHandler(BaseHTTPRequestHandler):
    def _set_response(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        # Get content length from headers
        content_length = int(self.headers['Content-Length'])
        
        # Read the POST data
        post_data = self.rfile.read(content_length)
        
        # Get current timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Try to parse as JSON
        try:
            sensor_data = json.loads(post_data.decode('utf-8'))
            print(f"[{timestamp}] Received sensor data:")
            print(json.dumps(sensor_data, indent=2))
        except json.JSONDecodeError:
            # If not valid JSON, print as raw data
            print(f"[{timestamp}] Received non-JSON sensor data:")
            print(post_data.decode('utf-8', errors='replace'))
        
        # Send response back to client
        self._set_response()
        response = {"status": "success", "message": "Data received"}
        self.wfile.write(json.dumps(response).encode('utf-8'))

def run_server(port=8080):
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, SensorDataHandler)
    print(f"Starting sensor data server on port {port}...")
    print(f"Send POST requests to http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()
        sys.exit(0)

if __name__ == "__main__":
    # You can specify a different port as a command-line argument
    import sys
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)
    
    # Print debugging information
    print(f"Python version: {sys.version}")
    print(f"Starting server on 0.0.0.0:{port}")
    
    try:
        run_server(port)
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)