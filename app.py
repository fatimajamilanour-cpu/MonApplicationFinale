import os
import json
import hashlib
import secrets
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app)
SECRET_KEY = os.environ.get("SECRET_KEY", "phrase_secrete_par_defaut")
AMIRA_PHONE = os.environ.get("AMIRA_PHONE", "+22391999235")
PRIX_MINIMUM = 1000
MAX_TENTATIVES = 10

CODES_DB = {} 
TENTATIVES = {}

def hacher_code(code):
    return hashlib.sha256(f"{code}{SECRET_KEY}".encode()).hexdigest()

# C'EST ICI QUE LA PAGE HTML EST CHARGÉE
@app.route('/')
def accueil():
    # On met le code HTML directement ici
    html = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Recettes Secrètes</title>
        <style>
            body { text-align:center; font-family:sans-serif; padding:50px; background:#f4f4f9; }
            .box { background:white; padding:30px; border-radius:10px; max-width:400px; margin:auto; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
            input { padding:10px; width:80%; margin-bottom:10px; text-transform:uppercase; }
            button { background:#6C4CE8; color:white; padding:10px 20px; border:none; border-radius:5px; cursor:pointer; }
            #message { font-weight:bold; margin-top:15px; }
            #recettes-cachees { display:none; text-align:left; margin-top:15px; background:#e3f4ea; padding:10px; border-radius:8px; }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Recettes Secrètes</h2>
            <p>Entre ton code d'accès :</p>
            <input type="text" id="codeInput" placeholder="AJ-XXXX-XXXX">
            <br>
            <button onclick="verifierCode()">Débloquer</button>
            <p id="message"></p>
            <div id="recettes-cachees">
                <ul id="liste-recettes"></ul>
            </div>
        </div>
        <script>
            function getAppareilId() {
                let id = localStorage.getItem('appareil_id');
                if (!id) { id = 'app-' + Math.random().toString(36).substr(2, 9); localStorage.setItem('appareil_id', id); }
                return id;
            }
            async function verifierCode() {
                const code = document.getElementById('codeInput').value;
                const message = document.getElementById('message');
                message.textContent = "Vérification...";
                try {
                    const reponse = await fetch('/api/recettes-premium', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ code: code, appareil_id: getAppareilId() })
                    });
                    const data = await reponse.json();
                    if (reponse.ok) {
                        message.textContent = "Code accepté !";
                        message.style.color = "green";
                        document.getElementById('recettes-cachees').style.display = "block";
                        const liste = document.getElementById('liste-recettes');
                        liste.innerHTML = "";
                        data.recettes.forEach(r => {
                            liste.innerHTML += `<li><b>${r.titre}</b> : ${r.ingredients}</li>`;
                        });
                    } else {
                        message.textContent = data.erreur;
                        message.style.color = "red";
                    }
                } catch (e) {
                    message.textContent = "Erreur de connexion.";
                    message.style.color = "red";
                }
            }
        </script>
    </body>
    </html>
    """
    CODES_DB[hacher_code("AJ-2503-72BD")] = {"appareil": None}
    return html

@app.route('/api/recettes-premium', methods=['POST'])
def get_recettes():
    data = request.json
    code = data.get('code')
    appareil_id = data.get('appareil_id')

    ip = request.remote_addr
    maintenant = time.time()
    if ip not in TENTATIVES:
        TENTATIVES[ip] = []
    TENTATIVES[ip] = [t for t in TENTATIVES[ip] if maintenant - t < 60]
    if len(TENTATIVES[ip]) >= MAX_TENTATIVES:
        return jsonify({"erreur": "Trop de tentatives. Attendez 1 minute."}), 429
    TENTATIVES[ip].append(maintenant)

    empreinte = hacher_code(code)
    
    if empreinte not in CODES_DB:
        return jsonify({"erreur": "Code invalide"}), 403
    
    code_info = CODES_DB[empreinte]
    
    if code_info.get("appareil") is None:
        code_info["appareil"] = appareil_id
    elif code_info["appareil"] != appareil_id:
        return jsonify({"erreur": "Ce code est déjà utilisé sur un autre appareil"}), 403

    with open('premium.json', 'r', encoding='utf-8') as f:
        recettes = json.load(f)
    
    return jsonify({"recettes": recettes, "phone": AMIRA_PHONE})

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'newcode':
        prix = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
        if prix < PRIX_MINIMUM:
            print(f"Erreur : Le prix minimum est de {PRIX_MINIMUM} FCFA")
        else:
            nouveau_code = f"AJ-{secrets.token_hex(2).upper()}-{secrets.token_hex(2).upper()}"
            CODES_DB[hacher_code(nouveau_code)] = {"appareil": None}
            print(f"Code généré : {nouveau_code}")
    else:
        app.run(debug=True, port=5000)
