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
            document.getElementById('bouton-whatsapp').href = `https://wa.me/${data.phone.replace(/\s/g, '')}`;
        } else {
            message.textContent = data.erreur;
            message.style.color = "red";
        }
    } catch (e) {
        message.textContent = "Erreur de connexion.";
        message.style.color = "red";
    }
}
