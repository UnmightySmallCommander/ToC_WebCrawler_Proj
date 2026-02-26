from flask import Flask, request, jsonify
from flask_cors import CORS
from crawler_main import crawl 
import os

app = Flask(__name__)
# This line is critical - it tells the browser port 5173 is allowed
CORS(app) 

@app.route('/crawl', methods=['POST']) # Make sure this matches App.tsx
def handle_crawl():
    try:
        data = request.json
        url = data.get('input_url')
        randomize = data.get('random', False)
        if not url:
            return jsonify({"error": "No URL provided"}), 400

        result = crawl(url, randomize=randomize) # Using your crawler_main.py
        return jsonify(result)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
