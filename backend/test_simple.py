from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Flask is working!"})

if __name__ == '__main__':
    print("Starting simple Flask test server...")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
