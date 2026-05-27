/**
 * Gère la logique client pour le Trust Game.
 * Gère le minuteur, le chat IA (GPT), et les transactions de jetons.
 */

/* ── Gestion du minuteur ── */

/**
 * Met à jour l'affichage visuel du minuteur de discussion.
 * Gère les classes de couleur selon l'urgence (warning, urgent, done).
 */
function updateChatTimer() {
    updateTimeRemaining();
    const el = document.getElementById("time");
    const remaining = document.getElementById("time_remaining");
    const label = document.getElementById("timer_label");
    if (!el || !remaining) return;

    remaining.textContent = timeRemaining;

    el.classList.remove('chat-timer--warning', 'chat-timer--urgent', 'chat-timer--done');

    if (timeRemaining <= 0) {
        clearInterval(chatTimer);
        el.classList.add('chat-timer--done');
        if (label) label.textContent = '— Discussion terminée';
        disableChat(true);
    } else if (timeRemaining < 60) {
        el.classList.add('chat-timer--urgent');
        if (label) label.textContent = '— Dernière minute';
    } else if (timeRemaining <= 120) {
        el.classList.add('chat-timer--warning');
        if (label) label.textContent = '— Bientôt terminé';
    } else {
        if (label) label.textContent = '';
    }
}

/**
 * Calcule le temps restant en secondes à partir du timestamp d'expiration.
 */
function updateTimeRemaining() {
    const now = Date.now() / 1000;
    timeRemaining = Math.max(parseInt(expireTime - now), 0);
}

/* ── Contrôle de l'interface de chat ── */

/**
 * Désactive l'interface de chat GPT à la fin du temps ou après une décision.
 * @param {boolean} is_expired - Indique si la désactivation est due à l'expiration du temps.
 */
function disableChat(is_expired) {
    const placeholder = is_expired ? "Temps écoulé" : "Joueur A a pris sa décision";
    if (has_chat_gpt) setDisabled(inputGPT, buttonGPT, placeholder);
}

/**
 * Désactive un couple input/bouton spécifique.
 * @param {HTMLElement} input - Le champ de saisie.
 * @param {HTMLElement} button - Le bouton d'envoi.
 * @param {string} placeholder - Le nouveau texte du placeholder.
 */
function setDisabled(input, button, placeholder) {
    if (!input || !button) return;
    input.disabled = true;
    button.disabled = true;
    input.placeholder = placeholder;
}

/* ── Gestion de l'affichage (Bulles de chat) ── */

/**
 * Ajoute une bulle de message dans le conteneur spécifié.
 * @param {string} containerId - ID du conteneur HTML.
 * @param {string} text - Contenu du message.
 * @param {string} bubbleClass - Classe CSS pour le style de la bulle (ex: chat-bubble--self).
 */
function appendBubble(containerId, text, bubbleClass, withTimestamp = false) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${bubbleClass}`;
    bubble.innerHTML = text;
    container.appendChild(bubble);
    if (withTimestamp) {
        const ts = document.createElement('div');
        ts.className = 'msg-ts';
        ts.textContent = new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
        container.appendChild(ts);
    }
    container.scrollTop = container.scrollHeight;
}

/* ── Logique d'envoi des messages ── */

/**
 * Prépare les données pour un message envoyé à l'IA (GPT).
 * @param {string} message - Le contenu du message.
 * @param {string} playerPrefix - Préfixe du joueur (ex: "Vous: ").
 * @returns {Object} - Données formatées pour liveSend.
 */
function sendChatMessageGPT(message, playerPrefix) {
    appendBubble('chatbox-gpt', playerPrefix + message, 'chat-bubble--self', true);
    const thinking = document.getElementById('gpt-thinking');
    if (thinking) thinking.style.display = 'flex';
    return { message: message, is_chat_gpt: true };
}

/**
 * Fonction maîtresse d'envoi de message (déclenchée par l'UI).
 * @param {HTMLElement} input - Le champ input source.
 * @param {string|null} playerPrefix - Préfixe si c'est un chat GPT.
 */
function sendChatMessage(input, playerPrefix = null) {
    const message = input.value.trim();
    if (!message) return;
    const dataToSend = sendChatMessageGPT(message, playerPrefix);
    input.value = "";
    input.focus();
    liveSend(dataToSend);
}

/* ── Synchronisation et État du jeu ── */

/**
 * Restaure l'état de l'interface à partir des données sauvegardées (rechargement de page).
 */
function refreshFromSavedData() {
    const amount_sent = js_vars.amount_sent;
    const amount_sent_back = js_vars.amount_sent_back;

    if (amount_sent != null) {
        disableChat(false);
        liveRecv({ status: "sent", amount_sent: amount_sent });
        liveRecv({ status: "received", amount_sent: amount_sent, tripled_amount: amount_sent * js_vars.multiplier });
    }
    if (amount_sent_back != null) {
        liveRecv({
            status: "complete", can_proceed: true,
            amount_sent: amount_sent, amount_sent_back: amount_sent_back,
            tripled_amount: amount_sent * js_vars.multiplier
        });
    }
}

/* ── Gestion des Transactions ── */

/**
 * Envoie le montant de jetons choisi par le Joueur A.
 * Valide la saisie et met à jour l'UI locale avant l'envoi.
 */
function sendTokens() {
    const amountInput = document.getElementById("amount_input");
    const errorEl = document.getElementById("amount_error");
    const amount = parseInt(amountInput.value);

    if (isNaN(amount) || amount < 0 || amount > js_vars.endowment) {
        amountInput.classList.add("shake");
        if (errorEl) errorEl.style.display = 'block';
        setTimeout(() => amountInput.classList.remove("shake"), 300);
        return;
    }
    if (errorEl) errorEl.style.display = 'none';
    liveSend({ amount_sent: amount, time_remaining: timeRemaining });
    document.getElementById("send_button").disabled = true;
    document.getElementById("sent_amount").textContent = amount;
    const sent_word = document.getElementById("sent_amount_word");
    if (sent_word) sent_word.textContent = "€";
    document.getElementById("waiting_message").classList.remove("d-none");
}

/**
 * Envoie le montant de jetons renvoyé par le Joueur B.
 * Valide la saisie par rapport au montant triplé reçu.
 */
function sendTokensBack() {
    const amountBackInput = document.getElementById("amount_back_input");
    const errorEl = document.getElementById("amount_back_error");
    const maxAmount = parseInt(document.getElementById("tripled_amount_1").textContent);
    const amountBack = parseInt(amountBackInput.value);

    if (isNaN(amountBack) || amountBack < 0 || amountBack > maxAmount) {
        amountBackInput.classList.add("shake");
        if (errorEl) errorEl.style.display = 'block';
        setTimeout(() => amountBackInput.classList.remove("shake"), 300);
        return;
    }
    if (errorEl) errorEl.style.display = 'none';
    liveSend({ amount_sent_back: amountBack });
    document.getElementById("send_back_button").disabled = true;
}

/* ── Affichage des Résultats ── */

/**
 * Affiche le bilan financier pour le Joueur A.
 * @param {Object} data - Résultats de la transaction.
 */
function resultsPlayerA(data) {
    const resultsDiv = document.getElementById("final_results_content");
    const { amount_sent: sent, amount_sent_back: back } = data;
    const final = js_vars.endowment - sent + back;
    resultsDiv.innerHTML = `
    <p>Vous avez envoyé <strong>${sent}€</strong> au Joueur B.</p>
    <p>Le Joueur B vous a renvoyé <strong>${back}€</strong>.</p>
    <p><strong>Votre solde final : ${final}€</strong></p>`;
}

/**
 * Affiche le bilan financier pour le Joueur B.
 * @param {Object} data - Résultats de la transaction.
 */
function resultsPlayerB(data) {
    const resultsDiv = document.getElementById("final_results_content");
    const { amount_sent: received, tripled_amount: tripled, amount_sent_back: back } = data;
    const final = tripled - back;
    resultsDiv.innerHTML = `
    <p>Vous avez reçu <strong>${tripled}€</strong> (${received} × ${js_vars.multiplier}).</p>
    <p>Vous avez renvoyé <strong>${back}€</strong> au Joueur A.</p>
    <p><strong>Votre solde final : ${final}€</strong></p>`;
}

/**
 * Met à jour le bloc de résultats selon le rôle du joueur.
 */
function updateFinalResults(data) {
    if (roleIsPlayerA) resultsPlayerA(data);
    else resultsPlayerB(data);
}

/* ── Handlers de Réception (liveRecv) ── */

/**
 * Affiche la réponse générée par l'IA (GPT).
 */
function handleChatGPTReply(data) {
    const thinking = document.getElementById('gpt-thinking');
    if (thinking) thinking.style.display = 'none';
    appendBubble('chatbox-gpt', data.bot_prefix + data.reply, 'chat-bubble--gpt', true);

    // Phase 2 de la démo : la première réponse IA déclenche la flèche IA.
    if (demoState === 'awaiting_ia') {
        demoState = 'showing_ia';
        requestAnimationFrame(() => {
            const iaBubble = lastBubbleByClass('chat-bubble--gpt');
            // Faire disparaître la flèche "Vous"
            document.querySelectorAll('.demo-arrow--user').forEach(el => el.classList.add('demo-arrow--fade-out'));
            if (iaBubble) showDemoArrow(iaBubble, "L'assistant vous répond", 'ia');
        });
        // Laisser la flèche IA visible ~2.5 s, puis terminer la démo
        setTimeout(finalizeDemo, 2500);
    }
}

/**
 * Gère les erreurs techniques lors de la communication avec l'API GPT.
 */
function handleGPTError(data) {
    const thinking = document.getElementById('gpt-thinking');
    if (thinking) thinking.style.display = 'none';
    appendBubble('chatbox-gpt', data.message, 'chat-bubble--error');
    setDisabled(inputGPT, buttonGPT, "Service IA indisponible");

    // Si l'erreur survient pendant la démo, on déverrouille quand même la suite
    // pour ne pas laisser l'utilisateur bloqué derrière l'overlay.
    if (demoState === 'awaiting_ia' || demoState === 'awaiting_user_bubble') {
        finalizeDemo();
    }
}

/**
 * Confirme l'envoi réussi pour le Joueur A.
 */
function handleSentStatus(data) {
    disableChat(false);
    document.getElementById("send_button").disabled = true;
    document.getElementById("sent_amount").textContent = data.amount_sent;
    const sent_word = document.getElementById("sent_amount_word");
    if (sent_word) sent_word.textContent = "€";
    document.getElementById("waiting_message").classList.remove("d-none");
}

/**
 * Gère la réception de jetons pour le Joueur B et active l'interface de renvoi.
 */
function handleReceivedStatus(data) {
    disableChat(false);
    document.getElementById("waiting_for_A").classList.add("d-none");
    document.getElementById("received_amount_display").classList.remove("d-none");
    document.getElementById("received_amount").textContent = data.amount_sent;
    const rec_word = document.getElementById("received_amount_word");
    if (rec_word) rec_word.textContent = "€";

    document.getElementById("tripled_amount_1").textContent = data.tripled_amount;
    const trip1_word = document.getElementById("tripled_amount_1_word");
    if (trip1_word) trip1_word.textContent = "€";

    document.getElementById("tripled_amount_2").textContent = data.tripled_amount;
    const trip2_word = document.getElementById("tripled_amount_2_word");
    if (trip2_word) trip2_word.textContent = "€";
    
    document.getElementById("amount_back_input").max = data.tripled_amount;
    if (typeof setupSliderB === 'function') setupSliderB(data.tripled_amount);
}

/**
 * Gère la fin du jeu et l'affichage des résultats finaux.
 */
function handleCompleteStatus(data) {
    canProceed = data.can_proceed;
    document.getElementById("game_results").classList.remove("d-none");
    updateFinalResults(data);
    if (canProceed) document.getElementById("proceed_button").disabled = false;
}

/**
 * Envoie le premier message automatique à l'assistant IA pour initier l'interaction.
 * Appelée au démarrage du timer (mode normal) ou au chargement direct (mode démo).
 */
function autoInitChat() {
    if (!has_chat_gpt) return;
    const role = roleIsPlayerA ? "A" : "B";
    const msg = `Bonjour, je suis le Joueur ${role}. Comment peux-tu m'aider ?`;
    const chatbox = document.getElementById('chatbox-gpt');
    if (chatbox && chatbox.innerHTML.includes(msg)) return;
    appendBubble('chatbox-gpt', '<strong>Joueur:</strong> ' + msg, 'chat-bubble--self', true);
    liveSend({ message: msg, is_chat_gpt: true, auto_init: true });
    const thinking = document.getElementById('gpt-thinking');
    if (thinking) thinking.style.display = 'flex';
}

/**
 * Gère le déclenchement du chronomètre et le premier message IA.
 * En mode normal, déclenche aussi la démo pédagogique si elle n'a pas déjà été jouée.
 */
function handleStartTimer(data) {
    expireTime = parseFloat(data.start_timer);

    if (typeof showGameElements === 'function') {
        showGameElements();
    }

    // Mode normal : la démo n'a pas encore été jouée → on la lance APRÈS le start_timer.
    // Le chrono ne démarre pas tant que finalizeDemo n'a pas été appelé.
    // Mode démo : la démo a déjà été lancée au DOMContentLoaded. Le start_timer arrive
    // ici suite à demo_complete → demoState === 'done' → on tombe dans le flux normal.
    if (has_chat_gpt && demoState === 'idle') {
        runDemoSequence();
        return;
    }

    chatTimer = setInterval(updateChatTimer, 1000);
    autoInitChat();
}

function showToast(message, type) {
    alert(message);
}

/* ── Reconnexion partenaire (Bilendi) ── */

let reconnectTimer = null;
let reconnectSeconds = 0;

function showReconnectOverlay(timeoutSeconds) {
    const overlay = document.getElementById('reconnect-overlay');
    if (!overlay) return;
    overlay.style.display = 'flex';
    reconnectSeconds = timeoutSeconds;
    updateReconnectCountdown();
    reconnectTimer = setInterval(updateReconnectCountdown, 1000);
    setDisabled(inputGPT, buttonGPT, "Partenaire déconnecté");
}

function hideReconnectOverlay() {
    const overlay = document.getElementById('reconnect-overlay');
    if (overlay) overlay.style.display = 'none';
    if (reconnectTimer) {
        clearInterval(reconnectTimer);
        reconnectTimer = null;
    }
}

function updateReconnectCountdown() {
    if (reconnectSeconds <= 0) {
        clearInterval(reconnectTimer);
        reconnectTimer = null;
        onReconnectTimeout();
        return;
    }
    const min = Math.floor(reconnectSeconds / 60);
    const sec = reconnectSeconds % 60;
    const minEl = document.getElementById('reconnect-countdown-minutes');
    const secEl = document.getElementById('reconnect-countdown-seconds');
    if (minEl) minEl.textContent = min;
    if (secEl) secEl.textContent = String(sec).padStart(2, '0');
    reconnectSeconds--;
}

function onReconnectTimeout() {
    const countdownText = document.getElementById('reconnect-countdown-text');
    if (countdownText) countdownText.style.display = 'none';
    const status = document.getElementById('reconnect-status');
    if (status) status.style.display = 'block';
    liveSend({ reconnect_timeout: true });
}

function showPartnerBackOverlay() {
    hideReconnectOverlay();
    const overlay = document.getElementById('reconnect-back-overlay');
    if (!overlay) return;
    overlay.style.display = 'flex';
    setTimeout(() => {
        overlay.style.display = 'none';
    }, 2500);
    if (inputGPT) {
        inputGPT.disabled = false;
        inputGPT.placeholder = "Parler à l'Assistant IA…";
    }
    if (buttonGPT) buttonGPT.disabled = false;
}

function handleSkippedStatus(data) {
    canProceed = data.can_proceed;
    hideReconnectOverlay();
    document.getElementById('game_results').classList.remove('d-none');
    const resultsDiv = document.getElementById('final_results_content');
    resultsDiv.innerHTML = `
      <p>Votre partenaire n'a pas pu se reconnecter à temps.</p>
      <p><strong>Cette étape est sautée. Vous passez à la suite de l'expérience.</strong></p>`;
    document.getElementById('proceed_button').disabled = false;
}

/* ── Séquence démo interactive (mode demo_mode uniquement) ── */

let demoState = 'idle'; // 'idle' | 'awaiting_user_bubble' | 'awaiting_ia' | 'showing_ia' | 'done'

const DEMO_ARROW_SVG_USER = `
<svg class="demo-arrow__svg" viewBox="0 0 64 48" fill="none" stroke="currentColor"
     stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"
     style="transform: scaleX(-1);">
  <path d="M2 24 C 14 8, 30 8, 50 24" />
  <path d="M44 16 L 52 24 L 44 32" />
</svg>`;

const DEMO_ARROW_SVG_IA = `
<svg class="demo-arrow__svg" viewBox="0 0 64 48" fill="none" stroke="currentColor"
     stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <path d="M2 24 C 14 8, 30 8, 50 24" />
  <path d="M44 16 L 52 24 L 44 32" />
</svg>`;

/**
 * Lance la séquence pédagogique : envoie le premier message auto, affiche la
 * flèche "Vous", attend la réponse IA pour afficher la flèche "L'assistant vous répond",
 * puis envoie demo_complete au serveur pour démarrer le chrono.
 */
// Réponse IA simulée pour la démo (pas d'appel API → coût zéro + robuste aux pannes API).
const DEMO_FAKE_IA_REPLY = "Bonjour ! Je peux vous rappeler les règles du jeu et vous aider à réfléchir à votre décision. Posez-moi vos questions quand vous voulez.";

function runDemoSequence() {
    demoState = 'awaiting_user_bubble';
    document.querySelector('.gameplay-layout')?.classList.add('demo-active');
    showDemoOverlay();
    setDisabled(inputGPT, buttonGPT, "Démo en cours…");

    // Bulle utilisateur simulée (pas de liveSend → pas d'appel API).
    const role = roleIsPlayerA ? "A" : "B";
    const userMsg = `Bonjour, je suis le Joueur ${role}. Comment peux-tu m'aider ?`;
    appendBubble('chatbox-gpt', '<strong>Joueur:</strong> ' + userMsg, 'chat-bubble--self', true);
    const thinking = document.getElementById('gpt-thinking');
    if (thinking) thinking.style.display = 'flex';

    // Listeners pour que les flèches suivent le scroll / resize.
    window.addEventListener('scroll', repositionAllArrows, true);
    window.addEventListener('resize', repositionAllArrows);

    requestAnimationFrame(() => {
        const userBubble = lastBubbleByClass('chat-bubble--self');
        if (userBubble) showDemoArrow(userBubble, 'Vous', 'user');
        demoState = 'awaiting_ia';
    });

    // Simule la réponse IA après ~1.4 s ("IA en train d'écrire…").
    setTimeout(simulateDemoIaReply, 1400);
}

/**
 * Affiche la bulle IA simulée puis la flèche "L'assistant vous répond".
 */
function simulateDemoIaReply() {
    if (demoState !== 'awaiting_ia') return;
    const thinking = document.getElementById('gpt-thinking');
    if (thinking) thinking.style.display = 'none';
    appendBubble('chatbox-gpt', '<strong>GPT:</strong> ' + DEMO_FAKE_IA_REPLY, 'chat-bubble--gpt', true);

    demoState = 'showing_ia';
    requestAnimationFrame(() => {
        const iaBubble = lastBubbleByClass('chat-bubble--gpt');
        document.querySelectorAll('.demo-arrow--user').forEach(el => el.classList.add('demo-arrow--fade-out'));
        if (iaBubble) showDemoArrow(iaBubble, "L'assistant vous répond", 'ia');
    });
    setTimeout(finalizeDemo, 4500);
}

/**
 * Sélectionne la dernière bulle de chat ayant la classe spécifiée.
 * On ne peut pas utiliser :last-of-type car appendBubble ajoute un .msg-ts
 * (même tag <div>) après chaque bulle.
 */
function lastBubbleByClass(cls) {
    const bubbles = document.querySelectorAll('#chatbox-gpt .' + cls);
    return bubbles.length ? bubbles[bubbles.length - 1] : null;
}

function showDemoOverlay() {
    if (document.querySelector('.demo-overlay')) return;
    const overlay = document.createElement('div');
    overlay.className = 'demo-overlay';
    document.body.appendChild(overlay);
}

function hideDemoOverlay() {
    const overlay = document.querySelector('.demo-overlay');
    if (!overlay) return;
    overlay.classList.add('demo-overlay--fade-out');
    setTimeout(() => overlay.remove(), 400);
}

// Liste des couples (flèche, bulle) actifs pour repositionner au scroll/resize.
const _activeDemoArrows = [];

/**
 * Affiche une flèche (SVG + libellé) à droite de la bulle ciblée et l'attache
 * au scroll/resize pour qu'elle reste collée à la bulle.
 * @param {HTMLElement} targetBubble - L'élément bulle à pointer.
 * @param {string} label - Texte affiché dans le badge.
 * @param {'user'|'ia'} kind - Détermine le sens de la flèche et la classe CSS.
 */
function showDemoArrow(targetBubble, label, kind) {
    if (!targetBubble) return;
    const arrow = document.createElement('div');
    arrow.className = `demo-arrow demo-arrow--${kind}`;
    const svg = kind === 'ia' ? DEMO_ARROW_SVG_IA : DEMO_ARROW_SVG_USER;
    // IA: label BEFORE SVG (label → SVG→ bulle à gauche) ; USER: SVG ← BEFORE label
    arrow.innerHTML = kind === 'ia'
        ? `<span class="demo-arrow__label">${label}</span>${svg}`
        : `${svg}<span class="demo-arrow__label">${label}</span>`;
    document.body.appendChild(arrow);

    _activeDemoArrows.push({ arrow, bubble: targetBubble, kind });
    repositionArrow(arrow, targetBubble, kind);
}

/**
 * Calcule et applique la position d'une flèche par rapport à sa bulle cible.
 * Utilise getBoundingClientRect (viewport-relative) compatible avec position:fixed.
 */
function repositionArrow(arrow, bubble, kind) {
    if (!arrow || !bubble || !document.body.contains(bubble)) return;
    const rect = bubble.getBoundingClientRect();
    const arrowRect = arrow.getBoundingClientRect();
    const top = rect.top + (rect.height / 2) - (arrowRect.height / 2);
    let left;
    if (kind === 'ia') {
        // Bulle IA à gauche → flèche à GAUCHE de la bulle
        left = rect.left - arrowRect.width - 12;
        if (left < 8) left = 8;
    } else {
        // Bulle USER à droite → flèche à DROITE de la bulle
        left = rect.right + 12;
        if (left + arrowRect.width > window.innerWidth - 8) {
            left = Math.max(8, rect.right - arrowRect.width);
        }
    }
    arrow.style.left = `${left}px`;
    arrow.style.top = `${top}px`;
}

function repositionAllArrows() {
    _activeDemoArrows.forEach(({ arrow, bubble, kind }) => repositionArrow(arrow, bubble, kind));
}

function hideDemoArrows() {
    document.querySelectorAll('.demo-arrow').forEach(el => {
        el.classList.add('demo-arrow--fade-out');
        setTimeout(() => el.remove(), 400);
    });
    _activeDemoArrows.length = 0;
    window.removeEventListener('scroll', repositionAllArrows, true);
    window.removeEventListener('resize', repositionAllArrows);
}

/**
 * Termine la séquence démo : retire flèches/overlay, réactive l'input,
 * puis démarre le chrono (mode normal) ou demande au serveur de le démarrer (mode démo).
 */
function finalizeDemo() {
    if (demoState === 'done') return;
    demoState = 'done';
    hideDemoArrows();
    hideDemoOverlay();
    document.querySelector('.gameplay-layout')?.classList.remove('demo-active');
    if (inputGPT) {
        inputGPT.disabled = false;
        inputGPT.placeholder = "Parler à l'Assistant IA…";
    }
    if (buttonGPT) buttonGPT.disabled = false;

    if (js_vars.demo_mode === true) {
        // Mode démo : le chrono n'a pas encore été initialisé côté serveur.
        // demo_complete déclenche expire_time + start_timer côté serveur.
        liveSend({ demo_complete: true });
    } else {
        // Mode normal : start_timer a déjà été reçu, expireTime est défini.
        // On démarre simplement le chrono côté client.
        if (!chatTimer) {
            chatTimer = setInterval(updateChatTimer, 1000);
        }
    }
}

/**
 * Point d'entrée principal pour tous les messages reçus via liveSend (Canaux oTree).
 * Oriente les données vers les handlers spécifiques.
 */
function liveRecv(data) {
    if (data.start_timer) handleStartTimer(data);
    if (data.partner_left) {
        const timeout = data.reconnect_timeout || 0;
        if (timeout > 0) {
            showReconnectOverlay(timeout);
        } else {
            showToast("Votre partenaire a quitté la session. Contactez l'expérimentateur.", "error");
            setDisabled(inputGPT, buttonGPT, "Partenaire déconnecté");
        }
    }
    if (data.partner_back) {
        showPartnerBackOverlay();
    }
    if (data.status === "skipped") handleSkippedStatus(data);
    if (data.type === "gpt_error") handleGPTError(data);
    if (data.is_chat_gpt && data.reply) handleChatGPTReply(data);

    if (data.status === "sent" && roleIsPlayerA) handleSentStatus(data);
    if (data.status === "received" && !roleIsPlayerA) handleReceivedStatus(data);
    if (data.status === "sent" || data.status === "received") {
        const timeEl = document.getElementById("time");
        if (timeEl) timeEl.classList.add("d-none");
    }
    if (data.status === "complete") handleCompleteStatus(data);
}
