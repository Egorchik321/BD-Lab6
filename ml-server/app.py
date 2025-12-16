from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    user_id = data.get('user_id', 1)
    n = data.get('n', 5)
    
    # Заглушка для рекомендаций
    recommendations = list(np.random.choice(1000, size=n, replace=False))
    
    return jsonify({
        'user_id': user_id,
        'recommendations': recommendations
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)