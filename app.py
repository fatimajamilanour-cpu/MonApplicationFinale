import os
import json
from flask import Flask, request, jsonify
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
    # On charge le code HTML de ton application
    try:
        with open('Amira_jamila.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Erreur : Le fichier HTML n'est pas trouvé."

@app.route('/api/config')
def config():
    return jsonify({"wa": "https://wa.me/22391999235", "prix": 1000})

@app.route('/api/recettes-premium', methods=['POST'])
def get_recettes():
    data = request.json
    code = data.get('code')
    appareil_id = data.get('device')

    if code not in CODES_DB:
        return jsonify({"error": "Code invalide"}), 403
    
    code_info = CODES_DB[code]
    if code_info["appareil"] is None:
        code_info["appareil"] = appareil_id
    elif code_info["appareil"] != appareil_id:
        return jsonify({"error": "Ce code est déjà utilisé sur un autre appareil"}), 403

    # On renvoie les recettes premium
    return jsonify({
        "recettes": [
            {"n": "Pain burger", "i": "Farine, levure...", "s": "Pétrir..."},
            {"n": "Yassa", "i": "Poulet, oignons...", "s": "Mariner..."}
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
