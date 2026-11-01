import os
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ⚠️ REMPLACE CES VALEURS PAR TES VRAIES CLÉS PAYDUNYA (TEST)
PAYDUNYA_MASTER_KEY = "test_public_DvChTyXrRQIrZ0gcsZKne6ERbfV"
PAYDUNYA_PRIVATE_KEY = "test_private_YdEyNZnkp6M46a9x5qnGJblxgg3"
PAYDUNYA_TOKEN = "ZM3rDIgpzGycg2cOrt2K"

AMIRA_PHONE = "22391999235"
PRICES = {"pat": 10000, "cui": 5000, "all": 15000}

# Tes codes secrets
CODES_DB = {
    "AJ-2503-72BD": {"appareil": None, "packs": ["pat", "cui"]},
    "AJ-PAT-10000": {"appareil": None, "packs": ["pat"]},
    "AJ-CUI-5000": {"appareil": None, "packs": ["cui"]},
    "AJ-ALL-15000": {"appareil": None, "packs": ["pat", "cui"]}
}

@app.route('/')
def accueil():
    return send_from_directory('.', 'Amira_jamila.html')

@app.route('/api/config')
def config():
    return jsonify({"wa": f"https://wa.me/{AMIRA_PHONE}"})

@app.route('/api/pay', methods=['POST'])
def pay():
    data = request.json
    plan = data.get('plan')
    if plan not in PRICES:
        return jsonify({"error": "Pack inconnu"}), 400

    montant = PRICES[plan]
    
    url = "https://app.paydunya.com/api/v1/checkout-invoice/create"
    headers = {
        "Content-Type": "application/json",
        "PAYDUNYA-MASTER-KEY": PAYDUNYA_MASTER_KEY,
        "PAYDUNYA-PRIVATE-KEY": PAYDUNYA_PRIVATE_KEY,
        "PAYDUNYA-TOKEN": PAYDUNYA_TOKEN
    }
    payload = {
        "invoice": {
            "total_amount": montant,
            "description": f"Achat pack {plan}"
        },
        "store": {
            "name": "Amira Jamila",
            "website_url": "https://monapplicationfinale.onrender.com"
        },
        "actions": {
            "cancel_url": "https://monapplicationfinale.onrender.com",
            "return_url": "https://monapplicationfinale.onrender.com/?paid=1",
            "callback_url": "https://monapplicationfinale.onrender.com/api/notify"
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        res_data = response.json()
        if res_data.get("response_code") == "00":
            return jsonify({"url": res_data["response_text"]}) 
        else:
            return jsonify({"error": "Erreur PayDunya"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notify', methods=['POST'])
def notify():
    return jsonify({"status": "OK"}), 200

@app.route('/api/redeem', methods=['POST'])
def redeem():
    data = request.json
    code = data.get('code')
    device = data.get('device')

    if code not in CODES_DB:
        return jsonify({"error": "Code invalide"}), 403
    
    info = CODES_DB[code]
    
    if info["appareil"] is None:
        info["appareil"] = device
    elif info["appareil"] != device:
        return jsonify({"error": "Ce code est déjà utilisé sur un autre appareil."}), 403

    return jsonify({"token": "token_secret", "packs": info["packs"]})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
