console.log('✅ script.js chargé');

document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('sendBtn');
    const input = document.getElementById('question');
    const chat = document.getElementById('chat');
    const intentLbl = document.getElementById('intent');
    const matchedLbl = document.getElementById('matched');
    const confFill = document.getElementById('conf-fill');
    const stars = document.querySelectorAll('.star');

    let currentInteraction = null;
    let isLoading = false;

    // Fonction principale pour envoyer une question
    async function sendQuestion(q) {
        const question = q.trim();
        if (!question || isLoading) return;

        // Affichage de la question utilisateur
        chat.innerHTML += `<div class="user-msg"><b>Vous :</b> ${question}</div>`;
        input.value = '';
        input.focus();

        // Réinitialiser les étoiles
        stars.forEach(s => { s.textContent="☆"; s.style.pointerEvents='auto'; });

        // Afficher loader
        const loaderDiv = document.createElement('div');
        loaderDiv.className = 'bot-msg';
        loaderDiv.innerHTML = '<i>💭 Bot réfléchit…</i>';
        chat.appendChild(loaderDiv);
        chat.scrollTop = chat.scrollHeight;

        isLoading = true;

        try {
            const res = await fetch('/ask', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({question:question})
            });
            const data = await res.json();
            currentInteraction = data;

            // Retirer loader
            loaderDiv.remove();

            // Affichage réponse bot
            chat.innerHTML += `<div class="bot-msg"><b>Bot :</b> ${data.response}</div>`;

            // Suggestions
            if(data.recs && data.recs.length>0){
                const suggDiv = document.createElement('div');
                suggDiv.className = 'recs';
                suggDiv.style.display = "grid";
                suggDiv.style.gridTemplateRows = "repeat(5, auto)";
                suggDiv.style.gridAutoFlow = "column";
                suggDiv.style.gap = "6px 12px";
                suggDiv.style.marginTop = "4px";

                data.recs.forEach((r) => {
                    const itemDiv = document.createElement('div');
                    itemDiv.style.display = "inline-flex";
                    itemDiv.style.alignItems = "center";

                    const circle = document.createElement('span');
                    circle.style.display = "inline-block";
                    circle.style.width = "8px";
                    circle.style.height = "8px";
                    circle.style.backgroundColor = "black";
                    circle.style.borderRadius = "50%";
                    circle.style.marginRight = "6px";
                    itemDiv.appendChild(circle);

                    const a = document.createElement('a');
                    a.textContent = r;
                    a.style.cursor = "pointer";
                    itemDiv.appendChild(a);

                    suggDiv.appendChild(itemDiv);
                });

                chat.appendChild(suggDiv);
            }

            // Mise à jour des informations
            intentLbl.textContent = data.intent;
            matchedLbl.textContent = data.matched;
            confFill.style.width = data.confidence + "%";
            confFill.textContent = data.confidence + "%";

            let color = "#43A047";
            if(data.confidence < 40) color = "#E53935";
            else if(data.confidence < 80) color = "#FB8C00";
            confFill.style.background = color;

        } catch(err){
            loaderDiv.remove();
            chat.innerHTML += '<div class="bot-msg"><b>Erreur :</b> Impossible de contacter le serveur.</div>';
            console.error(err);
        }

        chat.scrollTop = chat.scrollHeight;
        isLoading = false;
    }

    // Click sur le bouton Envoyer
    btn.addEventListener('click', () => sendQuestion(input.value));

    // Envoi avec Enter
    input.addEventListener('keypress', e => { if(e.key==='Enter') sendQuestion(input.value); });

    // Gestion étoiles de satisfaction
    stars.forEach(s => {
        s.addEventListener('click', () => {
            const val = parseInt(s.dataset.value);
            stars.forEach((st, i) => { st.textContent = i<val?"★":"☆"; st.style.pointerEvents='none'; });
            chat.innerHTML += `<div><i>⭐ Merci pour votre évaluation : ${val} / 5</i></div>`;
        });
    });

    // Event delegation pour les recommandations
    chat.addEventListener('click', (e) => {
        if(e.target.tagName === 'A' && e.target.parentElement.parentElement.classList.contains('recs')){
            sendQuestion(e.target.textContent);
        }
    });
});
