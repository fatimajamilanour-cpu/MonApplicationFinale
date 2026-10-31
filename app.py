import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Tes codes secrets
CODES_DB = {
    "AJ-2503-72BD": {"appareil": None},
    "AJ-9999-VIP1": {"appareil": None}
}

@app.route('/')
def accueil():
    # On charge le fichier HTML de ton application
    return send_from_directory('.', 'Amira_jamila.html')

@app.route('/api/config')
def config():
    return jsonify({"wa": "https://wa.me/22391999235", "prix": 1000})

@app.route('/api/redeem', methods=['POST'])
def redeem():
    data = request.json
    code = data.get('code')
    device = data.get('device')

    if code not in CODES_DB:
        return jsonify({"error": "Code invalide"}), 403
    
    if CODES_DB[code]["appareil"] is None:
        CODES_DB[code]["appareil"] = device
    elif CODES_DB[code]["appareil"] != device:
        return jsonify({"error": "Code déjà utilisé"}), 403

    # Ici, tu renvoies les recettes premium
    return jsonify({"token": "token_secret_pour_les_recettes"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
