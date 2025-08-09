# api/tauri_builder_api.py
from flask import Flask, jsonify, request
from tauri_builder import TauriBuilder, BuildConfig

app = Flask(__name__)

@app.route('/build', methods=['POST'])
def build():
    data = request.json
    config = BuildConfig(**data)
    builder = TauriBuilder(config)
    result = builder.run()
    return jsonify({"status": "success", "artifacts": result})

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "healthy", "version": "1.0.0"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)