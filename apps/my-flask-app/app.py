import os
from flask import Flask, render_template_string, request

app = Flask(__name__)

# Define the path for the counter file within the mounted volume
# This corresponds to the /srv directory inside the container,
# which is mounted to /home/<your_username>/network_share on pi-worker2
COUNTER_FILE = "/srv/counter.txt"

# Ensure the directory for the counter file exists
# This is important if /srv is empty on first run
os.makedirs(os.path.dirname(COUNTER_FILE), exist_ok=True)

def read_counter():
    """Reads the current counter value from the file."""
    if not os.path.exists(COUNTER_FILE):
        return 0
    with open(COUNTER_FILE, "r") as f:
        try:
            return int(f.read().strip())
        except ValueError:
            return 0 # Handle case where file is empty or contains non-integer

def write_counter(count):
    """Writes the counter value to the file."""
    with open(COUNTER_FILE, "w") as f:
        f.write(str(count))

@app.route('/')
def index():
    """Displays the current counter and provides buttons to increment/decrement."""
    current_count = read_counter()
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Persistent Counter</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
                .container { background-color: #f0f0f0; padding: 30px; border-radius: 10px; display: inline-block; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
                h1 { color: #333; }
                p { font-size: 2em; margin: 20px 0; color: #007bff; }
                button { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; margin: 5px; }
                button:hover { background-color: #0056b3; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Persistent Counter App</h1>
                <p>Current Count: {{ count }}</p>
                <form action="/increment" method="post" style="display:inline;">
                    <button type="submit">Increment</button>
                </form>
                <form action="/decrement" method="post" style="display:inline;">
                    <button type="submit">Decrement</button>
                </form>
            </div>
        </body>
        </html>
    ''', count=current_count)

@app.route('/increment', methods=['POST'])
def increment():
    """Increments the counter and redirects back to the index."""
    current_count = read_counter()
    new_count = current_count + 1
    write_counter(new_count)
    return index() # Render index directly for simplicity

@app.route('/decrement', methods=['POST'])
def decrement():
    """Decrements the counter and redirects back to the index."""
    current_count = read_counter()
    new_count = current_count - 1
    write_counter(new_count)
    return index() # Render index directly for simplicity

if __name__ == '__main__':
    # Listen on all available network interfaces within the Docker container
    # This is standard for containerized web apps
    app.run(host='0.0.0.0', port=80)